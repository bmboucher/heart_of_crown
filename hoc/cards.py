from dataclasses import dataclass

@dataclass
class Card:
    name: str
    cost: int
    coins: int = 0
    succession: bool = False
    successionPoints: int = 0
    forSale: bool = True

Cards = [
    Card('Farming Village', 1, coins=1, successionPoints=-2),
    Card('City',            3, coins=2),
    Card('Large City',      6, coins=3),
    Card('Apprentice Maid', 2, succession=True, successionPoints=-2, forSale=False),
    Card('Royal Maid',      3, succession=True, successionPoints=2),
    Card('Senator',         5, succession=True, successionPoints=3),
    Card('Duke',            8, succession=True, successionPoints=6)
]

NUM_CARDS = len(Cards)
InitialDeck = [7, 0, 0, 3, 0, 0, 0]
TerritoryPriority = [2, 1, 0] # Large city > city > farming village

def cards_to_str(counts: list[int]) -> list[str]:
    return [f'{n} {Cards[i].name}' for i,n in enumerate(counts) if n > 0]

def print_cards(counts: list[int]) -> None:
    print('\n'.join(f'  {s}' for s in cards_to_str(counts)))

def describe_cards(counts: list[int]) -> str:
    if sum(counts) == 0:
        return 'no cards'
    else:
        return ', '.join(cards_to_str(counts))

def purchase_options(coins: int, idx: int = 0) -> list[list[int]]:
    max_cards = coins // Cards[idx].cost if Cards[idx].forSale else 0
    opts: list[list[int]] = []
    if idx == len(Cards) - 1:
        return list([n] for n in range(max_cards + 1))
    else:
        for j in range(max_cards + 1):
            opts += [[j] + l for l in purchase_options(
                     coins - j * Cards[idx].cost, idx + 1)]
    return opts