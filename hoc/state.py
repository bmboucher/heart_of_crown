from dataclasses import dataclass, replace, field
from .cards import NUM_CARDS, Cards, InitialDeck, print_cards, purchase_options, TerritoryPriority
from random import randrange
from .action import Action
from typing import Callable, List, Tuple

STATE_SIZE = 3*NUM_CARDS + 2

@dataclass(frozen=True)
class GameState:
    drawPile: List[int] = field(default_factory=lambda:InitialDeck)
    discardPile: List[int] = field(default_factory=lambda:[0]*NUM_CARDS)
    hand: List[int] = field(default_factory=lambda:[0]*NUM_CARDS)
    backedPrincess: bool = False
    successionPoints: int = 0

    @property
    def status(self) -> str:
        if self.backedPrincess:
            return f'Princess backed, {self.successionPoints} succession points'
        else:
            return 'No princess backed'

    @property
    def finished(self) -> bool:
        return self.backedPrincess and self.successionPoints >= 20

    def flatten(self) -> List[int]:
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
        hand: List[int] = [0]*NUM_CARDS
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

    def cleanup(self, new_cards: List[int] = None) -> 'GameState':
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

    def available_actions(self) -> List[Action]:
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

    def next_states(self) -> List[Tuple[Action, 'GameState']]:
        return [(a, self.apply_action(a)) for a in self.available_actions()]

class Game:
    def __init__(self):
        self.state = GameState()
        self.transcript: List[Tuple[GameState, Action, int]] = []

    def run(self, strategy:Callable[[GameState], Action], max_rounds: int = None):
        rounds = 0
        while not self.state.finished:
            self.state = self.state.draw()
            action = strategy(self.state)
            next_state = self.state.apply_action(action)
            self.transcript.append((self.state, action, 
                next_state.successionPoints - self.state.successionPoints))
            self.state = next_state
            rounds += 1
            if max_rounds and rounds >= max_rounds:
                break

    @property
    def princessRound(self) -> int:
        rounds = [i for i, (_, action, _) in enumerate(self.transcript)
                    if action.backPrincess]
        return None if len(rounds) == 0 else rounds[0]

    @property
    def summary(self) -> str:
        return f'{self.princessRound} / {len(self.transcript)}'