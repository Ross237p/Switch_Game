"""
Command-line interface for the Switch card game.
"""

import sys
from typing import Optional
from ..core.card import Suit
from ..core.game_manager import GameManager
from ..config.game_config import GameConfig, DEFAULT_CONFIG


class CLI:
    """Command-line interface for Switch."""

    def __init__(self):
        self.game: Optional[GameManager] = None

    def clear_screen(self):
        """Clear the terminal screen."""
        print("\n" * 2)

    def print_separator(self):
        """Print a visual separator."""
        print("=" * 60)

    def print_header(self):
        """Print the game header."""
        self.print_separator()
        print("                    🎴 SWITCH 🎴")
        self.print_separator()
        print()

    def display_game_state(self):
        """Display the current game state."""
        if not self.game:
            return

        status = self.game.get_game_status()

        # Top card
        top_card = status['top_card']
        active_suit = status['active_suit']

        print(f"Top Card: {top_card}", end="")
        if active_suit:
            print(f" (Active suit: {active_suit})", end="")
        print()

        # Deck info
        print(f"Cards in deck: {status['deck_size']}")
        print(f"Direction: {status['direction']}")
        print()

        # Pending effects
        if status['pending_effect']:
            print(f"⚠️  Pending effect: {status['pending_effect']}")
            print()

        # Opponents
        print("Opponents:")
        for name, hand_size in status['opponent_hands'].items():
            print(f"  {name}: {hand_size} cards")
        print()

        # Your hand
        print("Your hand:")
        for i, card in enumerate(status['human_hand'], 1):
            print(f"  {i}. {card}")
        print()

    def display_playable_cards(self):
        """Display which cards can be played."""
        playable = self.game.get_playable_cards()

        if not playable:
            print("❌ No playable cards. You must draw.")
            return []

        print("Playable cards:")
        playable_indices = []

        human_hand = self.game.human_player.hand
        for i, card in enumerate(human_hand, 1):
            if card in playable:
                print(f"  {i}. {card} ✓")
                playable_indices.append(i)
            else:
                print(f"  {i}. {card}")

        return playable_indices

    def get_player_action(self) -> str:
        """Get action input from player."""
        print()
        print("Actions:")
        print("  [number] - Play card")
        print("  d - Draw card")
        print("  h - Help")
        print("  q - Quit")
        print()

        action = input("Choose action: ").strip().lower()
        return action

    def choose_suit(self) -> Suit:
        """Let player choose a suit for an Ace."""
        print()
        print("Choose a suit:")
        print("  1. ♠ Spades")
        print("  2. ♥ Hearts")
        print("  3. ♦ Diamonds")
        print("  4. ♣ Clubs")
        print()

        while True:
            choice = input("Choose suit (1-4): ").strip()

            if choice == "1":
                return Suit.SPADES
            elif choice == "2":
                return Suit.HEARTS
            elif choice == "3":
                return Suit.DIAMONDS
            elif choice == "4":
                return Suit.CLUBS
            else:
                print("Invalid choice. Please enter 1-4.")

    def show_help(self):
        """Display help information."""
        print()
        self.print_separator()
        print("GAME RULES")
        self.print_separator()
        print()
        print("Goal: Be the first to play all your cards!")
        print()
        print("Basic Rules:")
        print("  - Match the top card by suit or rank")
        print("  - Draw if you can't play")
        print("  - Declare 'Last Card' when you have 2 cards left")
        print()
        print("Special Cards:")
        print("  A (Ace)     - Wild card, choose any suit")
        print("  2           - Next player draws 2 (stackable)")
        print("  7           - Play multiple cards of the same suit")
        print("  8           - Skip next player")
        print("  J (Jack)    - Reverse direction")
        print("  K♠/K♣       - Next player draws 5")
        print("  K♥/K♦       - Defend against Black King")
        print()
        self.print_separator()
        print()
        input("Press Enter to continue...")

    def handle_suit_run(self):
        """Handle a suit run sequence."""
        print()
        print(f"🎯 Suit run active! Play cards of {self.game.state.suit_run_suit}")
        print()

        while self.game.state.suit_run_active:
            suit_cards = self.game.human_player.get_cards_of_suit(
                self.game.state.suit_run_suit
            )

            if not suit_cards:
                print("No more cards of this suit.")
                self.game.state.end_suit_run()
                self.game.end_turn()
                break

            print(f"Cards of {self.game.state.suit_run_suit}:")
            for i, card in enumerate(suit_cards, 1):
                print(f"  {i}. {card}")
            print()

            action = input("Enter card number to continue run, or 'e' to end: ").strip().lower()

            if action == 'e':
                self.game.state.end_suit_run()
                self.game.end_turn()
                print("Suit run ended.")
                break

            try:
                card_index = int(action) - 1
                if 0 <= card_index < len(suit_cards):
                    card = suit_cards[card_index]
                    success, msg = self.game.continue_suit_run(card)
                    print(msg)

                    if self.game.is_game_over():
                        break
                else:
                    print("Invalid card number.")
            except ValueError:
                print("Invalid input.")

    def play_turn(self):
        """Play a human player's turn."""
        self.clear_screen()
        self.print_header()

        # Check for pending effects
        if self.game.state.pending_effect:
            effect = self.game.state.pending_effect
            print(f"⚠️  You are affected by: {effect.effect_type}")

            if effect.effect_type == "draw_two":
                # Check if player has a 2 to stack
                if self.game.human_player.has_two():
                    stack = input(f"Draw {effect.value} cards or stack a 2? (d/s): ").strip().lower()
                    if stack == 's':
                        twos = [c for c in self.game.human_player.hand if c.is_two]
                        if twos:
                            success, msg = self.game.play_card(twos[0])
                            print(msg)
                            return
                # Draw cards
                self.game.state.resolve_pending_effect(self.game.human_player)
                self.game.end_turn()
                input("Press Enter to continue...")
                return

            elif effect.effect_type == "draw_king":
                # Check if player has Red King
                if self.game.human_player.has_red_king():
                    defend = input(f"Draw 5 cards or defend with Red King? (d/r): ").strip().lower()
                    if defend == 'r':
                        red_kings = [c for c in self.game.human_player.hand if c.is_red_king]
                        if red_kings:
                            success, msg = self.game.play_card(red_kings[0])
                            print(msg)
                            self.game.end_turn()
                            return
                # Draw cards
                self.game.state.resolve_pending_effect(self.game.human_player)
                self.game.end_turn()
                input("Press Enter to continue...")
                return

            elif effect.effect_type == "skip":
                print("Your turn is skipped!")
                self.game.state.resolve_pending_effect(self.game.human_player)
                self.game.end_turn()
                input("Press Enter to continue...")
                return

        # Normal turn
        self.display_game_state()
        playable_indices = self.display_playable_cards()

        action = self.get_player_action()

        # Handle action
        if action == 'q':
            if input("Are you sure you want to quit? (y/n): ").lower() == 'y':
                sys.exit(0)

        elif action == 'h':
            self.show_help()

        elif action == 'd':
            success, msg = self.game.draw_card()
            print(msg)
            input("Press Enter to continue...")

        else:
            try:
                card_num = int(action)
                if card_num in playable_indices:
                    card = self.game.human_player.hand[card_num - 1]

                    # Choose suit if Ace
                    chosen_suit = None
                    if card.is_ace:
                        chosen_suit = self.choose_suit()

                    success, msg = self.game.play_card(card, chosen_suit)
                    print(msg)

                    # Handle suit run
                    if self.game.state.suit_run_active:
                        self.handle_suit_run()
                    else:
                        input("Press Enter to continue...")
                else:
                    print("Cannot play that card!")
                    input("Press Enter to continue...")
            except (ValueError, IndexError):
                print("Invalid input!")
                input("Press Enter to continue...")

    def play_ai_turns(self):
        """Play all AI turns until it's the human's turn again."""
        while not self.game.is_human_turn() and not self.game.is_game_over():
            player = self.game.current_player()
            print(f"\n{player.name}'s turn...")

            messages = self.game.execute_ai_turn()
            for msg in messages:
                print(f"  {msg}")

            if not self.game.is_game_over():
                import time
                time.sleep(1)  # Pause to show AI actions

    def run_game(self):
        """Run the main game loop."""
        # Setup
        self.print_header()
        print("Welcome to Switch!")
        print()

        player_name = input("Enter your name (or press Enter for 'You'): ").strip()
        if not player_name:
            player_name = "You"

        self.game = GameManager(DEFAULT_CONFIG, player_name)
        self.game.start_game()

        print()
        print("Game started! Good luck!")
        input("Press Enter to begin...")

        # Main game loop
        while not self.game.is_game_over():
            if self.game.is_human_turn():
                self.play_turn()
            else:
                self.play_ai_turns()

        # Game over
        self.clear_screen()
        self.print_header()
        print("🎉 GAME OVER! 🎉")
        print()

        winner = self.game.get_winner()
        if winner == self.game.human_player:
            print("🏆 Congratulations! You won! 🏆")
        else:
            print(f"😔 {winner.name} wins this time!")

        print()
        print("Thanks for playing!")


def main():
    """Main entry point for the CLI."""
    cli = CLI()
    try:
        cli.run_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)


if __name__ == "__main__":
    main()
