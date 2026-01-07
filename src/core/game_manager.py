"""
Game manager for the Switch card game.
Orchestrates game flow and manages player turns.
"""

from typing import List, Optional, Tuple
from .card import Card, Suit
from .player import Player, HumanPlayer
from .game_state import GameState, GamePhase
from ..config.game_config import GameConfig
from ..ai.strategies import create_default_ai_opponents


class GameManager:
    """
    Manages the overall game flow and player interactions.

    Attributes:
        config: Game configuration
        state: Current game state
        human_player: The human player
    """

    def __init__(self, config: GameConfig = None, player_name: str = "You"):
        """
        Initialize the game manager.

        Args:
            config: Game configuration (uses default if None)
            player_name: Name for the human player
        """
        self.config = config or GameConfig()
        self.config.validate()

        # Create players
        self.human_player = HumanPlayer(player_name)
        ai_opponents = create_default_ai_opponents(self.config.num_ai_players)

        # Create game state
        all_players = [self.human_player] + ai_opponents
        self.state = GameState(self.config, all_players)

    def start_game(self):
        """Start a new game."""
        self.state.setup_game()

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.state.phase == GamePhase.GAME_OVER

    def get_winner(self) -> Optional[Player]:
        """Get the winning player."""
        return self.state.winner

    def current_player(self) -> Player:
        """Get the current player."""
        return self.state.current_player()

    def is_human_turn(self) -> bool:
        """Check if it's the human player's turn."""
        return self.current_player() == self.human_player

    def get_top_card(self) -> Optional[Card]:
        """Get the current top card."""
        return self.state.top_card()

    def get_active_suit(self) -> Optional[Suit]:
        """Get the active suit (if Ace was played)."""
        return self.state.active_suit

    def get_playable_cards(self) -> List[Card]:
        """Get the human player's playable cards."""
        top = self.get_top_card()
        if not top:
            return []
        return self.human_player.get_playable_cards(top, self.state.active_suit)

    def can_play_card(self, card: Card) -> bool:
        """Check if a card can be legally played."""
        return self.state.can_play_card(card)

    def play_card(self, card: Card, chosen_suit: Optional[Suit] = None) -> Tuple[bool, str]:
        """
        Play a card for the current player.

        Args:
            card: The card to play
            chosen_suit: The suit to declare (if playing an Ace)

        Returns:
            Tuple of (success, message)
        """
        player = self.current_player()

        # Check if player has the card
        if not player.has_card(card):
            return False, "You don't have that card"

        # Check if card can be played
        if not self.can_play_card(card):
            return False, "That card cannot be played"

        # Check for "Last Card" declaration
        if player.should_declare_last_card():
            if player.is_human:
                # Human must explicitly declare
                player.declare_last_card()
            else:
                # AI might forget (Rookie has 10% chance)
                if hasattr(player, 'should_forget_last_card_declaration'):
                    if player.should_forget_last_card_declaration():
                        self.state.check_last_card_declaration(player)
                    else:
                        player.declare_last_card()
                else:
                    player.declare_last_card()

        # Play the card
        self.state.play_card(player, card)

        # Handle Ace - set chosen suit
        if card.is_ace and chosen_suit:
            self.state.set_active_suit(chosen_suit)

        # Check if player wins
        if player.is_hand_empty():
            winner = self.state.check_winner()
            if winner:
                return True, f"{winner.name} wins!"

        # If this started a suit run, don't end turn yet
        if self.state.suit_run_active:
            return True, f"Suit run started with {card.suit}"

        # Check if player has more cards of same rank (for rank chaining)
        if not self.state.rank_chain_active:
            same_rank_cards = player.get_cards_of_rank(card.rank)
            if same_rank_cards:
                # Start rank chain
                self.state.start_rank_chain(card.rank, player)
                return True, f"Rank chain available! Play more {card.rank}s or end chain"

        return True, "Card played successfully"

    def continue_suit_run(self, card: Optional[Card] = None) -> Tuple[bool, str]:
        """
        Continue or end a suit run.

        Args:
            card: Card to play in the run, or None to end the run

        Returns:
            Tuple of (success, message)
        """
        if not self.state.suit_run_active:
            return False, "No suit run is active"

        player = self.current_player()

        # End the run
        if card is None:
            self.state.end_suit_run()
            self.end_turn()
            return True, "Suit run ended"

        # Continue the run
        if card.suit != self.state.suit_run_suit:
            return False, f"Card must be of suit {self.state.suit_run_suit}"

        # Check power card finish rule
        if not self.config.power_card_finish and card.is_power_card:
            if player.hand_size() == 1:  # This would be the last card
                # Cannot finish on power card - draw penalty
                self.state.draw_cards(player, 1)
                self.state.end_suit_run()
                self.end_turn()
                return False, "Cannot finish on a power card! Drew 1 card"

        # Play the card
        success, msg = self.play_card(card)
        if not success:
            return False, msg

        # Check if player won
        if player.is_hand_empty():
            return True, f"{player.name} wins!"

        # Check if player has more cards of this suit
        if len(player.get_cards_of_suit(self.state.suit_run_suit)) == 0:
            self.state.end_suit_run()
            self.end_turn()
            return True, "Suit run ended (no more cards)"

        return True, "Continue suit run or end"

    def continue_rank_chain(self, card: Optional[Card] = None) -> Tuple[bool, str]:
        """
        Continue or end a rank chain.

        Args:
            card: Card to play in the chain, or None to end the chain

        Returns:
            Tuple of (success, message)
        """
        if not self.state.rank_chain_active:
            return False, "No rank chain is active"

        player = self.current_player()

        # End the chain
        if card is None:
            self.state.end_rank_chain()
            self.end_turn()
            return True, "Rank chain ended"

        # Continue the chain
        if card.rank != self.state.rank_chain_rank:
            return False, f"Card must be of rank {self.state.rank_chain_rank}"

        # Play the card
        success, msg = self.play_card(card)
        if not success:
            return False, msg

        # Check if player won
        if player.is_hand_empty():
            return True, f"{player.name} wins!"

        # Check if player has more cards of this rank
        if len(player.get_cards_of_rank(self.state.rank_chain_rank)) == 0:
            self.state.end_rank_chain()
            self.end_turn()
            return True, "Rank chain ended (no more cards)"

        return True, "Continue rank chain or end"

    def draw_card(self) -> Tuple[bool, str]:
        """
        Draw a card for the current player.
        Drawing a card always ends your turn.

        Returns:
            Tuple of (success, message)
        """
        player = self.current_player()

        # Draw one card
        cards = self.state.draw_cards(player, 1)
        if not cards:
            return False, "No cards left to draw"

        card = cards[0]

        # Drawing always ends your turn
        self.end_turn()
        return True, f"Drew {card} - turn ends"

    def end_turn(self):
        """End the current player's turn and advance to next player."""
        player = self.current_player()

        # Resolve any pending effects on the next player
        self.state.advance_turn()
        next_player = self.current_player()

        # Check for pending effects
        if self.state.pending_effect:
            effect = self.state.pending_effect

            # Skip effect
            if effect.effect_type == "skip":
                self.state.resolve_pending_effect(next_player)
                self.state.advance_turn()
                return

            # Draw effects - AI will try to defend/stack
            if effect.effect_type in ("draw_two", "draw_king"):
                # Let AI handle defense in their turn
                pass

    def execute_ai_turn(self) -> List[str]:
        """
        Execute an AI player's turn.

        Returns:
            List of action messages
        """
        messages = []
        player = self.current_player()

        if player.is_human:
            return ["Not an AI player"]

        # Handle pending effects
        if self.state.pending_effect:
            effect = self.state.pending_effect

            # Try to defend or stack
            if effect.effect_type == "draw_two" and player.has_two():
                # AI might stack a 2
                twos = player.get_cards_of_rank(player.hand[0].rank.TWO)
                if twos and hasattr(player, 'choose_card_to_play'):
                    # Aggressor always stacks, others might
                    if player.strategy == "aggressor" or (player.strategy == "hoarder" and len(player.hand) > 5):
                        card = twos[0]
                        self.state.play_card(player, card)
                        messages.append(f"{player.name} stacks a 2!")
                        self.end_turn()
                        return messages

            elif effect.effect_type == "draw_king" and player.has_red_king():
                # Try to defend
                red_kings = [c for c in player.hand if c.is_red_king]
                if red_kings:
                    card = red_kings[0]
                    self.state.play_card(player, card)
                    messages.append(f"{player.name} defends with Red King!")
                    self.end_turn()
                    return messages

            # Couldn't defend - take the penalty
            self.state.resolve_pending_effect(player)
            self.end_turn()
            return messages

        # Normal turn - choose a card to play
        top_card = self.get_top_card()
        game_state_dict = self.state.get_game_state_dict()

        card_to_play = player.choose_card_to_play(top_card, self.state.active_suit, game_state_dict)

        if card_to_play:
            # Choose suit if playing Ace
            chosen_suit = None
            if card_to_play.is_ace:
                chosen_suit = player.choose_suit_for_ace(game_state_dict)
                messages.append(f"{player.name} plays {card_to_play} and declares {chosen_suit}")
            else:
                messages.append(f"{player.name} plays {card_to_play}")

            success, msg = self.play_card(card_to_play, chosen_suit)

            # Handle suit run
            if self.state.suit_run_active:
                self._handle_ai_suit_run(player, messages, game_state_dict)

            if not self.state.suit_run_active:
                self.end_turn()

        else:
            # No playable card - draw
            messages.append(f"{player.name} draws a card")
            self.draw_card()

        return messages

    def _handle_ai_suit_run(self, player, messages: List[str], game_state_dict: dict):
        """Handle AI decision-making during a suit run."""
        suit = self.state.suit_run_suit

        while self.state.suit_run_active:
            # Check if AI wants to continue
            should_continue = player.should_continue_suit_run(suit, game_state_dict)

            if not should_continue:
                self.state.end_suit_run()
                self.end_turn()
                messages.append(f"{player.name} ends suit run")
                break

            # Get cards of the run suit
            suit_cards = player.get_cards_of_suit(suit)
            if not suit_cards:
                self.state.end_suit_run()
                self.end_turn()
                messages.append(f"{player.name} has no more cards of {suit}")
                break

            # Play the next card
            next_card = suit_cards[0]  # AI strategies should handle sorting

            # Check power card finish rule
            if not self.config.power_card_finish and next_card.is_power_card:
                if player.hand_size() == 1:
                    self.state.draw_cards(player, 1)
                    self.state.end_suit_run()
                    self.end_turn()
                    messages.append(f"{player.name} cannot finish on power card! Drew 1 card")
                    break

            self.state.play_card(player, next_card)
            messages.append(f"{player.name} continues with {next_card}")

            # Check if won
            if player.is_hand_empty():
                self.state.check_winner()
                messages.append(f"{player.name} wins!")
                break

    def get_game_status(self) -> dict:
        """
        Get current game status information.

        Returns:
            Dictionary with game status
        """
        return {
            'current_player': self.current_player().name,
            'top_card': str(self.get_top_card()) if self.get_top_card() else None,
            'active_suit': str(self.get_active_suit()) if self.get_active_suit() else None,
            'human_hand_size': self.human_player.hand_size(),
            'human_hand': [str(card) for card in self.human_player.hand],
            'opponent_hands': {p.name: p.hand_size() for p in self.state.players if p != self.human_player},
            'deck_size': len(self.state.deck),
            'direction': 'clockwise' if self.state.direction.name == 'CLOCKWISE' else 'counter-clockwise',
            'pending_effect': str(self.state.pending_effect) if self.state.pending_effect else None,
            'suit_run_active': self.state.suit_run_active,
            'phase': self.state.phase.value,
            'is_game_over': self.is_game_over(),
            'winner': self.get_winner().name if self.get_winner() else None,
        }

    def get_recent_log(self, count: int = 5) -> List[str]:
        """Get recent game log messages."""
        return self.state.get_recent_log(count)
