from dataclasses import dataclass, field
from .cards import NUM_CARDS, describe_cards

@dataclass
class Action:
    purchases: list[int] = field(default_factory=lambda:[0]*NUM_CARDS)
    backPrincess: bool = False
    toDomain: list[int] = field(default_factory=lambda:[0]*NUM_CARDS)

    def __str__(self) -> str:
        if self.backPrincess:
            return 'Back a princess'
        elif sum(self.toDomain) > 0:
            return f'Place {describe_cards(self.toDomain)} in domain'
        else:
            return f'Buy {describe_cards(self.purchases)}'