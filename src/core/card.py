"""
Card module for the Switch card game.
Defines the Card class and related enumerations.
"""

from enum import Enum
from typing import Optional


class Suit(Enum):
    """Card suits."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

    def __str__(self):
        return self.value

    @property
    def is_red(self) -> bool:
        """Check if suit is red (Hearts or Diamonds)."""
        return self in (Suit.HEARTS, Suit.DIAMONDS)

    @property
    def is_black(self) -> bool:
        """Check if suit is black (Clubs or Spades)."""
        return self in (Suit.CLUBS, Suit.SPADES)


class Rank(Enum):
    """Card ranks with their values."""
    ACE = (1, "A", 15)      # (order, display, score)
    TWO = (2, "2", 2)
    THREE = (3, "3", 3)
    FOUR = (4, "4", 4)
    FIVE = (5, "5", 5)
    SIX = (6, "6", 6)
    SEVEN = (7, "7", 7)
    EIGHT = (8, "8", 8)
    NINE = (9, "9", 9)
    TEN = (10, "10", 10)
    JACK = (11, "J", 10)
    QUEEN = (12, "Q", 10)
    KING = (13, "K", 10)

    def __init__(self, order: int, display: str, score: int):
        self.order = order
        self.display = display
        self.score = score

    def __str__(self):
        return self.display

    def __lt__(self, other):
        if not isinstance(other, Rank):
            return NotImplemented
        return self.order < other.order


class Card:
    """
    Represents a playing card in the Switch game.

    Attributes:
        suit: The suit of the card
        rank: The rank of the card
    """

    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        """String representation of the card (e.g., 'A♠', '7♥')."""
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        return f"Card({self.suit.name}, {self.rank.name})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))

    # Special card type checks
    @property
    def is_ace(self) -> bool:
        """Check if card is an Ace (wild card)."""
        return self.rank == Rank.ACE

    @property
    def is_two(self) -> bool:
        """Check if card is a Two (draw two)."""
        return self.rank == Rank.TWO

    @property
    def is_seven(self) -> bool:
        """Check if card is a Seven (suit run)."""
        return self.rank == Rank.SEVEN

    @property
    def is_eight(self) -> bool:
        """Check if card is an Eight (skip)."""
        return self.rank == Rank.EIGHT

    @property
    def is_jack(self) -> bool:
        """Check if card is a Jack (reverse)."""
        return self.rank == Rank.JACK

    @property
    def is_king(self) -> bool:
        """Check if card is a King."""
        return self.rank == Rank.KING

    @property
    def is_black_king(self) -> bool:
        """Check if card is a Black King (attack)."""
        return self.is_king and self.suit.is_black

    @property
    def is_red_king(self) -> bool:
        """Check if card is a Red King (defense)."""
        return self.is_king and self.suit.is_red

    @property
    def is_power_card(self) -> bool:
        """Check if card is a power card (Ace or Two)."""
        return self.is_ace or self.is_two

    @property
    def is_special(self) -> bool:
        """Check if card has special effects."""
        return (self.is_ace or self.is_two or self.is_seven or
                self.is_eight or self.is_jack or self.is_king)

    @property
    def score_value(self) -> int:
        """Get the scoring value of the card."""
        return self.rank.score

    def matches_suit(self, other: 'Card') -> bool:
        """Check if this card matches the suit of another card."""
        return self.suit == other.suit

    def matches_rank(self, other: 'Card') -> bool:
        """Check if this card matches the rank of another card."""
        return self.rank == other.rank

    def can_play_on(self, other: 'Card', active_suit: Optional[Suit] = None) -> bool:
        """
        Check if this card can be played on another card.

        Args:
            other: The card to play on
            active_suit: The current active suit (if Ace was played)

        Returns:
            True if this card can be played on the other card
        """
        # Ace can be played on anything
        if self.is_ace:
            return True

        # If there's an active suit (from a previous Ace), match that
        if active_suit is not None:
            return self.suit == active_suit or self.is_ace

        # Otherwise, match suit or rank
        return self.matches_suit(other) or self.matches_rank(other)
