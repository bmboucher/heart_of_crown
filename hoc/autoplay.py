from .state import GameState
from .action import Action
import random

from pathlib import Path
OUTPUT = Path(__file__).parent / 'output' / 'raw.txt'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def play_game() -> list[tuple[Action, GameState, GameState]]:
    s = GameState()
    transcript: list[tuple[Action, GameState, GameState]] = []
    while not s.backedPrincess or s.successionPoints < 20:
        draw_s = s.draw()
        next_s = draw_s.next_states()
        actions = [a for a,_ in next_s]
        if any(a.backPrincess for a in actions):
            chosen = next(a for a in actions if a.backPrincess)
        elif any(sum(a.toDomain) > 0 for a in actions):
            chosen = next(a for a in actions if sum(a.toDomain) > 0)
        else:
            chosen = random.choice(actions)
        s = next_s[actions.index(chosen)][1]
        transcript.append((chosen, draw_s, s))
    return transcript

if __name__ == '__main__':
    with OUTPUT.open('w') as outf:
        for i in range(10000):
            t = play_game()
            for a,s,next_s in t:
                outf.write(f'{i}'
                    + ' '.join(f'{j}' for j in s.flatten() + a.flatten()) 
                    + '\n')
            print(f'Game {i:2} - {len(t):2} rounds')