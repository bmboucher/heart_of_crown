from .state import GameState
from .action import Action
import random

def play_game():
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
    print('\n'.join(f'{draw_s.coins:2} coins -> {str(c):45} {s.status}' for c,draw_s,s in transcript))
    return transcript

if __name__ == '__main__':
    for i in range(10):
        print(f'=== GAME {i} ===\n')
        play_game()
        print()