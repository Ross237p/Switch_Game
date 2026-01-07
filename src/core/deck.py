"""
Deck module for the Switch card game.
Handles card deck creation, shuffling, and dealing.
"""

import random
from typing import List, Optional
from .card import Card, Suit, Rank


class Deck:
    """
    Represents a deck of playing cards.

    Attributes:
        cards: List of cards in the deck
    """

    def __init__(self):
        """Initialize a standard 52-card deck."""
        self.cards: List[Card] = []
        self._create_deck()

    def _create_deck(self):
        """Create a standard 52-card deck."""
        self.cards = [
            Card(suit, rank)
            for suit in Suit
            for rank in Rank
        ]

    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        """
        Draw a card from the top of the deck.

        Returns:
            The drawn card, or None if the deck is empty
        """
        if self.cards:
            return self.cards.pop()
        return None

    def draw_multiple(self, count: int) -> List[Card]:
        """
        Draw multiple cards from the deck.

        Args:
            count: Number of cards to draw

        Returns:
            List of drawn cards (may be fewer than requested if deck is empty)
        """
        drawn_cards = []
        for _ in range(count):
            card = self.draw()
            if card is None:
                break
            drawn_cards.append(card)
        return drawn_cards

    def add_card(self, card: Card):
        """
        Add a card to the bottom of the deck.

        Args:
            card: The card to add
        """
        self.cards.insert(0, card)

    def add_cards(self, cards: List[Card]):
        """
        Add multiple cards to the bottom of the deck.

        Args:
            cards: List of cards to add
        """
        for card in cards:
            self.add_card(card)

    def is_empty(self) -> bool:
        """Check if the deck is empty."""
        return len(self.cards) == 0

    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the deck."""
        return len(self.cards)

    def __len__(self) -> int:
        """Return the number of cards in the deck."""
        return len(self.cards)

    def __str__(self) -> str:
        return f"Deck({len(self.cards)} cards)"

    def __repr__(self) -> str:
        return f"Deck(cards={len(self.cards)})"


class DiscardPile:
    """
    Represents the discard pile in the Switch game.

    Attributes:
        cards: List of cards in the discard pile (top card is at the end)
    """

    def __init__(self):
        """Initialize an empty discard pile."""
        self.cards: List[Card] = []

    def add_card(self, card: Card):
        """
        Add a card to the top of the discard pile.

        Args:
            card: The card to add
        """
        self.cards.append(card)

    def top_card(self) -> Optional[Card]:
        """
        Get the top card of the discard pile without removing it.

        Returns:
            The top card, or None if the pile is empty
        """
        if self.cards:
            return self.cards[-1]
        return None

    def take_all_except_top(self) -> List[Card]:
        """
        Take all cards except the top card (for reshuffling into deck).

        Returns:
            List of cards taken from the pile
        """
        if len(self.cards) <= 1:
            return []

        cards_to_take = self.cards[:-1]
        self.cards = [self.cards[-1]]
        return cards_to_take

    def is_empty(self) -> bool:
        """Check if the discard pile is empty."""
        return len(self.cards) == 0

    def __len__(self) -> int:
        """Return the number of cards in the discard pile."""
        return len(self.cards)

    def __str__(self) -> str:
        top = self.top_card()
        if top:
            return f"DiscardPile(top: {top}, total: {len(self.cards)})"
        return "DiscardPile(empty)"

    def __repr__(self) -> str:
        return f"DiscardPile(cards={len(self.cards)})"
