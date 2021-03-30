from .state import GameState

s = GameState()

n = 1
while not s.backedPrincess or s.successionPoints < 20:
    print(f'\n=== ROUND {n} ===\n')
    s = s.draw()
    s.print()
    next_s = s.next_states()
    print('OPTIONS:')
    for i, (d, _) in enumerate(next_s):
        print(f'   [{i:2}] {d}')
    j = int(input('SELECTION > '))
    if j < 0 or j >= len(next_s):
        raise RuntimeError('Invalid selection')
    selected, s = next_s[j]
    print(f'Selected "{selected}"')
    n = n + 1