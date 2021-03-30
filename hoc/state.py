from dataclasses import dataclass, replace, field
from tkinter import N
from .cards import NUM_CARDS, Cards, InitialDeck, print_cards, purchase_options, describe_cards, TerritoryPriority
from random import randrange
from .action import Action

@dataclass(frozen=True)
class GameState:
    drawPile: list[int] = field(default_factory=lambda:InitialDeck)
    discardPile: list[int] = field(default_factory=lambda:[0]*NUM_CARDS)
    hand: list[int] = field(default_factory=lambda:[0]*NUM_CARDS)
    backedPrincess: bool = False
    successionPoints: int = 0

    @property
    def status(self) -> str:
        if self.backedPrincess:
            return f'Princess backed, {self.successionPoints} succession points'
        else:
            return 'No princess backed'

    def flatten(self) -> list[int]:
        return self.drawPile + self.hand + self.discardPile \
                + [1 if self.backedPrincess else 0, self.successionPoints]

    def print(self) -> None:
        if sum(self.drawPile) > 0:
            print('Draw pile')
            print_cards(self.drawPile)
        if sum(self.discardPile) > 0:
            print('Discard pile')
            print_cards(self.discardPile)
        if sum(self.hand) > 0:
            print('Hand')
            print_cards(self.hand)

    def draw(self) -> 'GameState':
        hand: list[int] = [0]*NUM_CARDS
        if sum(self.drawPile) < 5:
            hand = self.drawPile.copy()
            draw = self.discardPile.copy()
            discard = [0]*NUM_CARDS
        else:
            draw = self.drawPile.copy()
            discard = self.discardPile.copy()
        for _ in range(5 - sum(hand)):
            selected = randrange(sum(draw))
            card_idx = next(i for i in range(NUM_CARDS) 
                            if sum(draw[:(i+1)]) > selected)
            draw[card_idx] -= 1
            hand[card_idx] += 1

        return replace(self, drawPile=draw, discardPile=discard, hand=hand)

    def cleanup(self, new_cards: list[int] = None) -> 'GameState':
        new_discard = self.discardPile.copy()
        for i in range(NUM_CARDS):
            new_discard[i] += self.hand[i]
            if new_cards:
                new_discard[i] += new_cards[i]
        return replace(self, discardPile=new_discard, hand=[0]*NUM_CARDS)

    def back_princess(self) -> 'GameState':
        return replace(self, backedPrincess=True)

    def add_succession_points(self, pts: int) -> 'GameState':
        return replace(self, successionPoints = self.successionPoints + pts)

    def apply_action(self, action: Action) -> 'GameState':
        delta = [new_cards - removed_cards for new_cards, removed_cards in
                 zip(action.purchases, action.toDomain)]
        sucPts = sum(n * Cards[i].successionPoints
                     for i, n in enumerate(action.toDomain))
        s = self.cleanup(delta).add_succession_points(sucPts)
        if action.backPrincess:
            s = s.back_princess()
        return s

    @property
    def coins(self) -> int:
        return sum(n * Cards[i].coins for i, n in enumerate(self.hand))

    def available_actions(self) -> list[Action]:
        coins = self.coins
        actions = [Action(purchases=new_cards)
            for new_cards in purchase_options(coins)]
        if not self.backedPrincess:
            if coins >= 6:
                toDomain = [0]*NUM_CARDS
                for j in TerritoryPriority:
                    toDomain[j] = min(self.hand[j], 3 - sum(toDomain))
                actions.append(Action(backPrincess=True, toDomain=toDomain))
        else:
            toDomain = [n if Cards[i].succession 
                             and Cards[i].successionPoints > 0 
                          else 0 for i,n in enumerate(self.hand)]
            if sum(toDomain) > 0:
                actions.append(Action(toDomain=toDomain))
        return actions

    def next_states(self) -> list[tuple[Action, 'GameState']]:
        return [(a, self.apply_action(a)) for a in self.available_actions()]