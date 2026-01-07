"""
Player module for the Switch card game.
Defines player classes and their behaviors.
"""

from typing import List, Optional
from .card import Card, Suit


class Player:
    """
    Base class for a player in the Switch game.

    Attributes:
        name: The player's name
        hand: List of cards in the player's hand
        has_declared_last_card: Whether the player has declared "Last Card"
    """

    def __init__(self, name: str):
        """
        Initialize a player.

        Args:
            name: The player's name
        """
        self.name = name
        self.hand: List[Card] = []
        self.has_declared_last_card = False
        self.score = 0

    def add_card(self, card: Card):
        """
        Add a card to the player's hand.

        Args:
            card: The card to add
        """
        self.hand.append(card)
        # Reset last card declaration if hand size increases
        if len(self.hand) > 2:
            self.has_declared_last_card = False

    def add_cards(self, cards: List[Card]):
        """
        Add multiple cards to the player's hand.

        Args:
            cards: List of cards to add
        """
        for card in cards:
            self.add_card(card)

    def remove_card(self, card: Card) -> bool:
        """
        Remove a card from the player's hand.

        Args:
            card: The card to remove

        Returns:
            True if the card was removed, False if not found
        """
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False

    def has_card(self, card: Card) -> bool:
        """
        Check if the player has a specific card.

        Args:
            card: The card to check for

        Returns:
            True if the player has the card
        """
        return card in self.hand

    def get_playable_cards(self, top_card: Card, active_suit: Optional[Suit] = None) -> List[Card]:
        """
        Get all cards that can be played on the top card.

        Args:
            top_card: The current top card of the discard pile
            active_suit: The active suit (if an Ace was played)

        Returns:
            List of playable cards
        """
        return [card for card in self.hand if card.can_play_on(top_card, active_suit)]

    def get_cards_of_suit(self, suit: Suit) -> List[Card]:
        """
        Get all cards of a specific suit in the player's hand.

        Args:
            suit: The suit to filter by

        Returns:
            List of cards of that suit
        """
        return [card for card in self.hand if card.suit == suit]

    def get_cards_of_rank(self, rank) -> List[Card]:
        """
        Get all cards of a specific rank in the player's hand.

        Args:
            rank: The rank to filter by

        Returns:
            List of cards of that rank
        """
        return [card for card in self.hand if card.rank == rank]

    def has_red_king(self) -> bool:
        """Check if the player has a Red King (defense card)."""
        return any(card.is_red_king for card in self.hand)

    def has_two(self) -> bool:
        """Check if the player has a Two (draw two card)."""
        return any(card.is_two for card in self.hand)

    def hand_size(self) -> int:
        """Get the number of cards in the player's hand."""
        return len(self.hand)

    def is_hand_empty(self) -> bool:
        """Check if the player's hand is empty."""
        return len(self.hand) == 0

    def should_declare_last_card(self) -> bool:
        """Check if the player should declare 'Last Card'."""
        return len(self.hand) == 2 and not self.has_declared_last_card

    def declare_last_card(self):
        """Declare 'Last Card'."""
        self.has_declared_last_card = True

    def reset_last_card_declaration(self):
        """Reset the last card declaration."""
        self.has_declared_last_card = False

    def calculate_hand_score(self) -> int:
        """
        Calculate the total score value of all cards in hand.

        Returns:
            Total score of cards in hand
        """
        return sum(card.score_value for card in self.hand)

    def sort_hand(self):
        """Sort the player's hand by suit and rank."""
        self.hand.sort(key=lambda card: (card.suit.name, card.rank.order))

    def __str__(self) -> str:
        return f"{self.name} ({len(self.hand)} cards)"

    def __repr__(self) -> str:
        return f"Player(name={self.name}, hand_size={len(self.hand)})"


class HumanPlayer(Player):
    """
    Represents a human player.
    """

    def __init__(self, name: str = "You"):
        super().__init__(name)
        self.is_human = True


class AIPlayer(Player):
    """
    Base class for AI players.

    Attributes:
        strategy: The AI's strategy type
    """

    def __init__(self, name: str, strategy: str = "random"):
        super().__init__(name)
        self.is_human = False
        self.strategy = strategy

    def choose_card_to_play(self, top_card: Card, active_suit: Optional[Suit],
                           game_state: dict) -> Optional[Card]:
        """
        Choose a card to play based on the AI's strategy.
        This method should be overridden by specific AI implementations.

        Args:
            top_card: The current top card of the discard pile
            active_suit: The active suit (if an Ace was played)
            game_state: Dictionary containing current game state information

        Returns:
            The card to play, or None if no card can be played
        """
        raise NotImplementedError("Subclasses must implement choose_card_to_play")

    def choose_suit_for_ace(self, game_state: dict) -> Suit:
        """
        Choose a suit when playing an Ace.
        This method should be overridden by specific AI implementations.

        Args:
            game_state: Dictionary containing current game state information

        Returns:
            The chosen suit
        """
        raise NotImplementedError("Subclasses must implement choose_suit_for_ace")

    def should_continue_suit_run(self, suit: Suit, game_state: dict) -> bool:
        """
        Decide whether to continue a suit run (after playing a 7).
        This method should be overridden by specific AI implementations.

        Args:
            suit: The suit of the run
            game_state: Dictionary containing current game state information

        Returns:
            True to continue the run, False to stop
        """
        raise NotImplementedError("Subclasses must implement should_continue_suit_run")
