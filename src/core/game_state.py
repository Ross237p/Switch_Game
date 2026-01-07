"""
Game state and rules engine for the Switch card game.
Manages game flow, turn order, and special card effects.
"""

from enum import Enum
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .card import Card, Suit
from .deck import Deck, DiscardPile
from .player import Player
from ..config.game_config import GameConfig


class Direction(Enum):
    """Direction of play."""
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1

    def reverse(self) -> 'Direction':
        """Reverse the direction."""
        if self == Direction.CLOCKWISE:
            return Direction.COUNTER_CLOCKWISE
        return Direction.CLOCKWISE


class GamePhase(Enum):
    """Current phase of the game."""
    SETUP = "setup"
    PLAYING = "playing"
    SUIT_RUN = "suit_run"
    GAME_OVER = "game_over"


@dataclass
class PendingEffect:
    """Represents a pending effect to be applied."""
    effect_type: str  # "draw", "skip", "reverse"
    value: int = 0  # For draw effects, number of cards to draw
    can_defend: bool = False  # For attacks, whether defense is possible


class GameState:
    """
    Manages the complete state of a Switch game.

    Attributes:
        config: Game configuration
        players: List of players in the game
        deck: The draw pile
        discard_pile: The discard pile
        current_player_index: Index of the current player
        direction: Current direction of play
        phase: Current game phase
        active_suit: Active suit (set by Ace wild card)
        pending_effect: Effect waiting to be resolved
        suit_run_active: Whether a suit run is currently active
        suit_run_suit: The suit of the active run
        winner: The winning player (if game is over)
    """

    def __init__(self, config: GameConfig, players: List[Player]):
        """
        Initialize game state.

        Args:
            config: Game configuration
            players: List of players (1 human + AI players)
        """
        self.config = config
        self.players = players
        self.deck = Deck()
        self.discard_pile = DiscardPile()

        self.current_player_index = 0
        self.direction = Direction.CLOCKWISE
        self.phase = GamePhase.SETUP

        self.active_suit: Optional[Suit] = None
        self.pending_effect: Optional[PendingEffect] = None

        self.suit_run_active = False
        self.suit_run_suit: Optional[Suit] = None

        self.winner: Optional[Player] = None
        self.game_log: List[str] = []

    def setup_game(self):
        """Set up a new game."""
        # Shuffle deck
        self.deck.shuffle()

        # Deal cards to players
        for player in self.players:
            cards = self.deck.draw_multiple(self.config.initial_hand_size)
            player.add_cards(cards)
            player.sort_hand()

        # Flip top card to start discard pile
        first_card = self.deck.draw()
        if first_card:
            self.discard_pile.add_card(first_card)
            self.log(f"Game started. First card: {first_card}")

            # Handle special first card
            if first_card.is_ace:
                # Auto-select suit based on first card's suit
                self.active_suit = first_card.suit
                self.log(f"Starting with Ace - suit set to {self.active_suit}")

        self.phase = GamePhase.PLAYING

    def current_player(self) -> Player:
        """Get the current player."""
        return self.players[self.current_player_index]

    def next_player_index(self) -> int:
        """Calculate the next player's index based on direction."""
        num_players = len(self.players)
        if self.direction == Direction.CLOCKWISE:
            return (self.current_player_index + 1) % num_players
        else:
            return (self.current_player_index - 1) % num_players

    def advance_turn(self):
        """Move to the next player's turn."""
        self.current_player_index = self.next_player_index()

    def top_card(self) -> Optional[Card]:
        """Get the top card of the discard pile."""
        return self.discard_pile.top_card()

    def can_play_card(self, card: Card) -> bool:
        """
        Check if a card can be legally played.

        Args:
            card: The card to check

        Returns:
            True if the card can be played
        """
        top = self.top_card()
        if not top:
            return True

        # During suit run, can only play cards of the run's suit
        if self.suit_run_active:
            return card.suit == self.suit_run_suit

        # Check if card can be played on top card
        return card.can_play_on(top, self.active_suit)

    def play_card(self, player: Player, card: Card) -> bool:
        """
        Play a card from a player's hand.

        Args:
            player: The player playing the card
            card: The card to play

        Returns:
            True if the card was played successfully
        """
        if not self.can_play_card(card):
            return False

        # Remove card from player's hand
        if not player.remove_card(card):
            return False

        # Add card to discard pile
        self.discard_pile.add_card(card)
        self.log(f"{player.name} plays {card}")

        # Clear active suit if not an Ace
        if not card.is_ace:
            self.active_suit = None

        # Process special card effects
        self._process_card_effect(card, player)

        return True

    def _process_card_effect(self, card: Card, player: Player):
        """
        Process the effect of a played card.

        Args:
            card: The card that was played
            player: The player who played the card
        """
        # Ace - Wild card (suit change handled separately)
        if card.is_ace:
            # Suit will be set via set_active_suit method
            pass

        # Two - Draw two (cumulative if enabled)
        elif card.is_two:
            if self.config.cumulative_penalties:
                # Add to existing penalty or create new one
                if self.pending_effect and self.pending_effect.effect_type == "draw_two":
                    self.pending_effect.value += 2
                else:
                    self.pending_effect = PendingEffect("draw_two", 2)
                self.log(f"Draw penalty increased to {self.pending_effect.value}")
            else:
                self.pending_effect = PendingEffect("draw_two", 2)
                self.log(f"Next player must draw 2 cards")

        # Seven - Suit run
        elif card.is_seven and self.config.suit_run_enabled:
            self.suit_run_active = True
            self.suit_run_suit = card.suit
            self.phase = GamePhase.SUIT_RUN
            self.log(f"{player.name} starts a suit run with {card.suit}")

        # Eight - Skip
        elif card.is_eight:
            self.pending_effect = PendingEffect("skip", 0)
            self.log(f"Next player will be skipped")

        # Jack - Reverse
        elif card.is_jack:
            self.direction = self.direction.reverse()
            direction_str = "clockwise" if self.direction == Direction.CLOCKWISE else "counter-clockwise"
            self.log(f"Direction reversed to {direction_str}")

        # Black King - Attack
        elif card.is_black_king and self.config.black_king_attack:
            self.pending_effect = PendingEffect("draw_king", 5, can_defend=True)
            self.log(f"Black King attack! Next player must draw 5 or defend")

        # Red King - Defense (only valid as response to Black King)
        elif card.is_red_king and self.config.red_king_defense:
            if self.pending_effect and self.pending_effect.effect_type == "draw_king":
                self.pending_effect = None
                self.log(f"{player.name} defends with Red King!")
            else:
                # Red King has no effect if not defending
                pass

    def set_active_suit(self, suit: Suit):
        """
        Set the active suit (when playing an Ace).

        Args:
            suit: The suit to set as active
        """
        self.active_suit = suit
        self.log(f"Active suit set to {suit}")

    def end_suit_run(self):
        """End the current suit run."""
        self.suit_run_active = False
        self.suit_run_suit = None
        self.phase = GamePhase.PLAYING
        self.log("Suit run ended")

    def draw_cards(self, player: Player, count: int) -> List[Card]:
        """
        Draw cards for a player, reshuffling discard pile if needed.

        Args:
            player: The player drawing cards
            count: Number of cards to draw

        Returns:
            List of cards drawn
        """
        drawn_cards = []

        for _ in range(count):
            # If deck is empty, reshuffle discard pile
            if self.deck.is_empty():
                self._reshuffle_discard_pile()

            # Draw a card
            card = self.deck.draw()
            if card:
                drawn_cards.append(card)
            else:
                # No more cards available
                break

        player.add_cards(drawn_cards)
        self.log(f"{player.name} draws {len(drawn_cards)} card(s)")

        return drawn_cards

    def _reshuffle_discard_pile(self):
        """Reshuffle the discard pile back into the deck."""
        cards_to_reshuffle = self.discard_pile.take_all_except_top()
        if cards_to_reshuffle:
            self.deck.add_cards(cards_to_reshuffle)
            self.deck.shuffle()
            self.log(f"Reshuffled {len(cards_to_reshuffle)} cards from discard pile")

    def resolve_pending_effect(self, player: Player, defense_card: Optional[Card] = None) -> bool:
        """
        Resolve a pending effect on a player.

        Args:
            player: The player to apply the effect to
            defense_card: Optional defense card (e.g., Red King or another 2)

        Returns:
            True if the effect was resolved (player's turn ends)
        """
        if not self.pending_effect:
            return False

        effect = self.pending_effect

        # Check for defense
        if defense_card:
            if effect.effect_type == "draw_two" and defense_card.is_two:
                # Stack another 2
                effect.value += 2
                self.log(f"{player.name} stacks a 2! Penalty now {effect.value}")
                return False  # Effect continues, turn doesn't end

            elif effect.effect_type == "draw_king" and defense_card.is_red_king:
                # Defend against Black King
                self.pending_effect = None
                self.log(f"{player.name} defends with Red King!")
                return False  # Defense successful, turn doesn't end

        # Apply the effect
        if effect.effect_type in ("draw_two", "draw_king"):
            self.draw_cards(player, effect.value)
            self.pending_effect = None
            return True  # Turn ends after drawing

        elif effect.effect_type == "skip":
            self.log(f"{player.name} is skipped")
            self.pending_effect = None
            return True  # Turn ends (skipped)

        return False

    def check_winner(self) -> Optional[Player]:
        """
        Check if there is a winner.

        Returns:
            The winning player, or None if game continues
        """
        for player in self.players:
            if player.is_hand_empty():
                self.winner = player
                self.phase = GamePhase.GAME_OVER
                self.log(f"{player.name} wins!")
                return player
        return None

    def check_last_card_declaration(self, player: Player) -> bool:
        """
        Check if player should declare 'Last Card' and apply penalty if forgotten.

        Args:
            player: The player to check

        Returns:
            True if penalty was applied
        """
        if player.should_declare_last_card():
            # Apply penalty
            self.log(f"{player.name} forgot to declare 'Last Card'! Draw 1 card")
            self.draw_cards(player, 1)
            return True
        return False

    def get_game_state_dict(self) -> dict:
        """
        Get a dictionary representation of the current game state.
        Useful for AI decision-making.

        Returns:
            Dictionary with game state information
        """
        return {
            'top_card': self.top_card(),
            'active_suit': self.active_suit,
            'pending_effect': self.pending_effect,
            'direction': self.direction,
            'current_player': self.current_player(),
            'players': self.players,
            'deck_size': len(self.deck),
            'discard_size': len(self.discard_pile),
            'suit_run_active': self.suit_run_active,
            'suit_run_suit': self.suit_run_suit,
            'phase': self.phase
        }

    def log(self, message: str):
        """
        Add a message to the game log.

        Args:
            message: The message to log
        """
        self.game_log.append(message)

    def get_recent_log(self, count: int = 5) -> List[str]:
        """
        Get recent log messages.

        Args:
            count: Number of recent messages to retrieve

        Returns:
            List of recent log messages
        """
        return self.game_log[-count:]
