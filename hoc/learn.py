import random
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path

from .state import STATE_SIZE, Game, GameState
from .action import ACTION_SIZE, Action

from typing import List

INPUT_SIZE = STATE_SIZE + ACTION_SIZE
MID_SIZE = 30
NUM_STAGES = 5
OUTPUT_SIZE = 1

def create_model() -> keras.Sequential:
    model = keras.Sequential()
    model.add(keras.Input(shape=(INPUT_SIZE,), dtype=tf.int16))
    for _ in range(NUM_STAGES - 1):
        model.add(layers.Dense(MID_SIZE, activation='relu'))
    model.add(layers.Dense(OUTPUT_SIZE, activation='linear'))

    model.compile(
        optimizer=keras.optimizers.RMSprop(),
        loss=keras.losses.MeanSquaredError()
    )

    return model

def model_strategy(state: GameState, model: keras.Sequential) -> Action:
    actions = state.available_actions()
    state_vect = state.flatten()
    inputs = tf.constant([state_vect + action.flatten() for action in actions])
    outputs: list = model(inputs) # type: ignore
    max_output = max(outputs)
    best_actions = [action for i, action in enumerate(actions)
                    if outputs[i] == max_output]
    return random.choice(best_actions)

MAX_GAME_LENGTH = 50
END_GAME_PAYOFF = 10.0
NO_PRINCESS_PENALTY = -10.0

OUTPUT_DIR = Path(__file__).parent / 'output'

round_index = 0

def play_games(model: keras.Sequential, n_games: int, discount_factor: float):
    def strategy(s: GameState) -> Action:
        return model_strategy(s, model)
    train_inputs: List[List[int]] = []
    train_outputs: List[List[float]] = []
    with (OUTPUT_DIR / f'games_{round_index}.txt').open('w') as output_file:
        for game_index in range(n_games):
            g = Game()
            g.run(strategy, MAX_GAME_LENGTH)
            train_inputs += [state.flatten() + action.flatten()
                            for state, action, __ in g.transcript]
            accum_output: List[float] = [0.0] * len(g.transcript)
            accum_output[-1] = (float(g.transcript[-1][2]) + 
                END_GAME_PAYOFF if g.state.finished else (
                NO_PRINCESS_PENALTY if not g.state.backedPrincess else 0.0))

            for i in range(len(accum_output) - 2, -1, -1):
                accum_output[i] = (accum_output[i + 1] * discount_factor 
                    + g.transcript[i][2])
            train_outputs += [[o] for o in accum_output]
            print(f'GAME {game_index + 1:4} of {n_games:4} => {g.summary:10}{min(accum_output):10.3f}{max(accum_output):10.3f}')
            output_row = ' '.join(map(str, [round_index, game_index, g.princessRound]
                + [state.successionPoints + payoff 
                    for state, _, payoff in g.transcript]))
            output_file.write(output_row + '\n')
    return train_inputs, train_outputs

def train(n_games_per_round: int, n_rounds: int, epochs: int, discount_factor: float):
    model = create_model()
    global round_index
    round_index = 0
    while round_index < n_rounds:
        all_inputs, all_outputs = play_games(
            model, n_games_per_round, discount_factor)
        train_size = int(0.9 * len(all_inputs))
        train_inputs = tf.constant(all_inputs[:train_size])
        train_outputs = tf.constant(all_outputs[:train_size])
        validation_inputs = tf.constant(all_inputs[train_size:])
        validation_outputs = tf.constant(all_outputs[train_size:])
        model.fit(train_inputs, train_outputs,
                  epochs=epochs,
                  validation_data=(validation_inputs, validation_outputs))
        model.save(OUTPUT_DIR / f'model_{round_index}')
        round_index += 1

train(200, 200, 200, 0.9)