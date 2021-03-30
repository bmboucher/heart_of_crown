from dataclasses import dataclass, field
from .cards import NUM_CARDS, describe_cards
from typing import List

ACTION_SIZE=2*NUM_CARDS+1

@dataclass
class Action:
    purchases: List[int] = field(default_factory=lambda:[0]*NUM_CARDS)
    backPrincess: bool = False
    toDomain: List[int] = field(default_factory=lambda:[0]*NUM_CARDS)

    def __str__(self) -> str:
        if self.backPrincess:
            return 'Back a princess'
        elif sum(self.toDomain) > 0:
            return f'Place {describe_cards(self.toDomain)} in domain'
        else:
            return f'Buy {describe_cards(self.purchases)}'

    def flatten(self) -> List[int]:
        return self.purchases + self.toDomain + [1 if self.backPrincess else 0]