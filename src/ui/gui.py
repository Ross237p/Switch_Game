"""
Graphical User Interface for the Switch card game.
Beautiful, clickable card game interface using Tkinter.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import List, Optional
import time

from ..core.card import Card, Suit
from ..core.game_manager import GameManager
from ..config.game_config import GameConfig, DEFAULT_CONFIG
from .card_widget import CardWidget, DeckWidget, CARD_WIDTH, CARD_HEIGHT


class SwitchGUI:
    """Main GUI window for the Switch card game."""

    def __init__(self, config: GameConfig = None):
        """Initialize the GUI."""
        self.config = config or DEFAULT_CONFIG

        # Create main window
        self.root = tk.Tk()
        self.root.title("🎴 Switch Card Game")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a5f1a")
        self.root.resizable(False, False)

        # Game state
        self.game: Optional[GameManager] = None
        self.card_widgets: List[CardWidget] = []
        self.selected_card: Optional[CardWidget] = None
        self.deck_widget: Optional[DeckWidget] = None
        self.discard_widget: Optional[CardWidget] = None
        self.opponent_widgets: List[List[CardWidget]] = []

        # UI elements
        self.create_ui()

        # Start game
        self.start_new_game()

    def create_ui(self):
        """Create the user interface elements."""
        # Title
        title_label = tk.Label(
            self.root,
            text="🎴 SWITCH 🎴",
            font=("Arial", 32, "bold"),
            bg="#1a5f1a",
            fg="#FFD700"
        )
        title_label.pack(pady=10)

        # Game canvas
        self.canvas = tk.Canvas(
            self.root,
            width=1180,
            height=600,
            bg="#2d7a2d",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # Bind click events
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Info panel
        info_frame = tk.Frame(self.root, bg="#1a5f1a")
        info_frame.pack(fill=tk.X, padx=20)

        # Status label
        self.status_label = tk.Label(
            info_frame,
            text="Welcome to Switch!",
            font=("Arial", 14),
            bg="#1a5f1a",
            fg="#FFFFFF"
        )
        self.status_label.pack(side=tk.LEFT)

        # Buttons frame
        button_frame = tk.Frame(info_frame, bg="#1a5f1a")
        button_frame.pack(side=tk.RIGHT)

        # Draw button
        self.draw_button = tk.Button(
            button_frame,
            text="Draw Card",
            font=("Arial", 12),
            command=self.draw_card_clicked,
            bg="#4A90E2",
            fg="white",
            padx=15,
            pady=5
        )
        self.draw_button.pack(side=tk.LEFT, padx=5)

        # Help button
        help_button = tk.Button(
            button_frame,
            text="Help",
            font=("Arial", 12),
            command=self.show_help,
            bg="#666666",
            fg="white",
            padx=15,
            pady=5
        )
        help_button.pack(side=tk.LEFT, padx=5)

        # New Game button
        new_game_button = tk.Button(
            button_frame,
            text="New Game",
            font=("Arial", 12),
            command=self.start_new_game,
            bg="#E74C3C",
            fg="white",
            padx=15,
            pady=5
        )
        new_game_button.pack(side=tk.LEFT, padx=5)

    def start_new_game(self):
        """Start a new game."""
        # Ask for player name
        player_name = simpledialog.askstring(
            "New Game",
            "Enter your name:",
            initialvalue="You",
            parent=self.root
        )

        if player_name is None:
            player_name = "You"

        # Clear existing game
        self.clear_canvas()

        # Create new game
        self.game = GameManager(self.config, player_name)
        self.game.start_game()

        # Draw initial state
        self.update_display()
        self.update_status("Game started! Your turn.")

    def clear_canvas(self):
        """Clear all widgets from canvas."""
        for widget in self.card_widgets:
            widget.destroy()
        self.card_widgets = []

        for opponent_hand in self.opponent_widgets:
            for widget in opponent_hand:
                widget.destroy()
        self.opponent_widgets = []

        if self.deck_widget:
            for elem in self.deck_widget.elements:
                self.canvas.delete(elem)
            self.deck_widget = None

        if self.discard_widget:
            self.discard_widget.destroy()
            self.discard_widget = None

        self.selected_card = None

    def update_display(self):
        """Update the entire display."""
        self.clear_canvas()

        if not self.game:
            return

        # Draw opponents at top
        self.draw_opponents()

        # Draw center area (deck and discard pile)
        self.draw_center()

        # Draw player's hand at bottom
        self.draw_player_hand()

        # Update status
        self.update_game_status()

    def draw_opponents(self):
        """Draw opponent hands at the top."""
        opponents = [p for p in self.game.state.players if p != self.game.human_player]

        # Positions for 3 opponents
        positions = [
            (90, 20),   # Left opponent
            (500, 20),  # Center opponent
            (910, 20)   # Right opponent
        ]

        self.opponent_widgets = []

        for i, opponent in enumerate(opponents):
            if i >= len(positions):
                break

            x, y = positions[i]

            # Opponent name label
            name_text = self.canvas.create_text(
                x + 100, y - 15,
                text=f"{opponent.name}: {opponent.hand_size()} cards",
                font=("Arial", 12, "bold"),
                fill="#FFFFFF"
            )

            # Draw cards (face down)
            hand_widgets = []
            for j in range(min(opponent.hand_size(), 10)):  # Max 10 displayed
                card_x = x + (j * 20)  # Overlap cards
                # Use first card as placeholder (face down)
                if opponent.hand:
                    widget = CardWidget(
                        self.canvas,
                        opponent.hand[0],
                        card_x,
                        y,
                        face_up=False
                    )
                    hand_widgets.append(widget)

            self.opponent_widgets.append(hand_widgets)

    def draw_center(self):
        """Draw the deck and discard pile in the center."""
        center_x = 590
        center_y = 240

        # Draw deck on the left
        deck_x = center_x - 150
        self.deck_widget = DeckWidget(
            self.canvas,
            deck_x,
            center_y,
            len(self.game.state.deck)
        )

        # Deck label
        self.canvas.create_text(
            deck_x + CARD_WIDTH // 2 + 3, center_y - 15,
            text="DRAW PILE",
            font=("Arial", 11, "bold"),
            fill="#FFFFFF"
        )

        # Draw discard pile on the right
        discard_x = center_x + 50
        top_card = self.game.get_top_card()

        if top_card:
            self.discard_widget = CardWidget(
                self.canvas,
                top_card,
                discard_x,
                center_y,
                face_up=True
            )

            # Discard pile label
            self.canvas.create_text(
                discard_x + CARD_WIDTH // 2, center_y - 15,
                text="DISCARD PILE",
                font=("Arial", 11, "bold"),
                fill="#FFFFFF"
            )

            # Show active suit if Ace was played
            active_suit = self.game.get_active_suit()
            if active_suit:
                self.canvas.create_text(
                    discard_x + CARD_WIDTH // 2, center_y + CARD_HEIGHT + 25,
                    text=f"Active Suit: {active_suit}",
                    font=("Arial", 13, "bold"),
                    fill="#FFD700"
                )

        # Direction arrow
        direction = self.game.state.direction.name
        arrow = "→" if direction == "CLOCKWISE" else "←"
        self.canvas.create_text(
            center_x, center_y + CARD_HEIGHT + 60,
            text=f"Direction: {arrow}",
            font=("Arial", 12),
            fill="#FFFFFF"
        )

    def draw_player_hand(self):
        """Draw the player's hand at the bottom."""
        hand = self.game.human_player.hand
        playable = self.game.get_playable_cards()

        # Calculate starting position to center the hand
        hand_width = len(hand) * (CARD_WIDTH + 10)
        start_x = (1180 - hand_width) // 2
        y = 450

        # Label
        self.canvas.create_text(
            590, y - 20,
            text="YOUR HAND",
            font=("Arial", 14, "bold"),
            fill="#FFFFFF"
        )

        # Draw each card
        for i, card in enumerate(hand):
            x = start_x + (i * (CARD_WIDTH + 10))

            widget = CardWidget(
                self.canvas,
                card,
                x,
                y,
                face_up=True,
                clickable=card in playable
            )

            self.card_widgets.append(widget)

            # Highlight playable cards
            if card in playable:
                # Green glow for playable cards
                self.canvas.create_rectangle(
                    x - 2, y - 2,
                    x + CARD_WIDTH + 2, y + CARD_HEIGHT + 2,
                    outline="#00FF00",
                    width=2
                )

    def update_game_status(self):
        """Update the status display."""
        if not self.game:
            return

        status = self.game.get_game_status()

        # Check for pending effects
        if self.game.state.pending_effect:
            effect = self.game.state.pending_effect
            if effect.effect_type == "draw_two":
                self.update_status(f"⚠️ Draw penalty: {effect.value} cards (or stack a 2!)")
            elif effect.effect_type == "draw_king":
                self.update_status("⚠️ Black King attack! Draw 5 or defend with Red King!")
            elif effect.effect_type == "skip":
                self.update_status("❌ Your turn is skipped!")

        # Check for suit run
        elif self.game.state.suit_run_active:
            self.update_status(f"🎯 Suit run active! Play more {self.game.state.suit_run_suit} or click 'End Run'")

        # Normal status
        elif self.game.is_human_turn():
            playable = self.game.get_playable_cards()
            if playable:
                self.update_status(f"Your turn! Click a card to play ({len(playable)} playable)")
            else:
                self.update_status("Your turn! No playable cards - click Draw Pile")

    def on_canvas_click(self, event):
        """Handle canvas click events."""
        if not self.game or self.game.is_game_over():
            return

        # Check if it's human's turn
        if not self.game.is_human_turn():
            return

        # Check for suit run
        if self.game.state.suit_run_active:
            self.handle_suit_run_click(event)
            return

        # Check for pending effects
        if self.game.state.pending_effect:
            self.handle_pending_effect_click(event)
            return

        # Check if clicked on deck
        if self.deck_widget and self.deck_widget.is_clicked(event.x, event.y):
            self.draw_card_clicked()
            return

        # Check if clicked on a card in hand
        for widget in self.card_widgets:
            if widget.is_clicked(event.x, event.y):
                self.card_clicked(widget)
                return

    def card_clicked(self, widget: CardWidget):
        """Handle card click."""
        card = widget.card

        # Check if card is playable
        if not self.game.can_play_card(card):
            self.update_status("❌ That card cannot be played!")
            return

        # Check "Last Card" declaration
        if self.game.human_player.should_declare_last_card():
            response = messagebox.askyesno(
                "Last Card!",
                "You have 2 cards left! Declare 'Last Card'?",
                parent=self.root
            )
            if response:
                self.game.human_player.declare_last_card()
            else:
                # Forgot to declare - penalty
                self.game.state.check_last_card_declaration(self.game.human_player)
                self.update_display()
                return

        # Play the card
        chosen_suit = None

        # If Ace, ask for suit
        if card.is_ace:
            chosen_suit = self.choose_suit()
            if chosen_suit is None:
                return  # Canceled

        success, msg = self.game.play_card(card, chosen_suit)

        if success:
            self.update_status(msg)
            self.update_display()

            # Check for win
            if self.game.is_game_over():
                self.show_game_over()
                return

            # Handle suit run
            if self.game.state.suit_run_active:
                self.update_status(f"🎯 Suit run! Play more {self.game.state.suit_run_suit} or End Run")
                # Add End Run button
                self.show_end_run_button()
                return

            # End turn and play AI turns
            self.game.end_turn()
            self.root.after(500, self.play_ai_turns)
        else:
            self.update_status(f"❌ {msg}")

    def draw_card_clicked(self):
        """Handle draw card button click."""
        if not self.game or not self.game.is_human_turn():
            return

        if self.game.state.suit_run_active:
            self.update_status("❌ Cannot draw during suit run!")
            return

        success, msg = self.game.draw_card()
        self.update_status(msg)
        self.update_display()

        # Play AI turns if turn ended
        if not self.game.is_human_turn():
            self.root.after(500, self.play_ai_turns)

    def handle_pending_effect_click(self, event):
        """Handle clicks when there's a pending effect."""
        effect = self.game.state.pending_effect

        # Check if trying to defend/stack
        for widget in self.card_widgets:
            if widget.is_clicked(event.x, event.y):
                card = widget.card

                # Try to stack a 2
                if effect.effect_type == "draw_two" and card.is_two:
                    self.game.state.play_card(self.game.human_player, card)
                    self.update_display()
                    self.game.end_turn()
                    self.root.after(500, self.play_ai_turns)
                    return

                # Try to defend with Red King
                elif effect.effect_type == "draw_king" and card.is_red_king:
                    self.game.state.play_card(self.game.human_player, card)
                    self.update_display()
                    self.game.end_turn()
                    self.root.after(500, self.play_ai_turns)
                    return

        # Otherwise, must draw
        self.game.state.resolve_pending_effect(self.game.human_player)
        self.game.end_turn()
        self.update_display()
        self.root.after(500, self.play_ai_turns)

    def handle_suit_run_click(self, event):
        """Handle clicks during a suit run."""
        for widget in self.card_widgets:
            if widget.is_clicked(event.x, event.y):
                card = widget.card

                if card.suit != self.game.state.suit_run_suit:
                    self.update_status(f"❌ Must play {self.game.state.suit_run_suit} cards!")
                    return

                success, msg = self.game.continue_suit_run(card)
                self.update_display()

                if self.game.is_game_over():
                    self.show_game_over()
                    return

                if not self.game.state.suit_run_active:
                    # Run ended
                    self.game.end_turn()
                    self.root.after(500, self.play_ai_turns)

                return

    def show_end_run_button(self):
        """Show button to end suit run."""
        # This is shown in the draw button area
        self.draw_button.config(
            text="End Suit Run",
            command=self.end_suit_run_clicked,
            bg="#E74C3C"
        )

    def end_suit_run_clicked(self):
        """Handle end suit run button click."""
        self.game.continue_suit_run(None)  # Pass None to end run
        self.draw_button.config(
            text="Draw Card",
            command=self.draw_card_clicked,
            bg="#4A90E2"
        )
        self.update_display()
        self.root.after(500, self.play_ai_turns)

    def play_ai_turns(self):
        """Play all AI turns."""
        if self.game.is_game_over():
            self.show_game_over()
            return

        while not self.game.is_human_turn() and not self.game.is_game_over():
            player = self.game.current_player()
            self.update_status(f"{player.name} is playing...")
            self.root.update()

            time.sleep(0.8)  # Pause to show AI action

            messages = self.game.execute_ai_turn()
            for msg in messages:
                print(f"AI: {msg}")

            self.update_display()
            self.root.update()

        if self.game.is_game_over():
            self.show_game_over()
        else:
            self.update_game_status()

    def choose_suit(self) -> Optional[Suit]:
        """Show dialog to choose a suit."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Suit")
        dialog.geometry("300x200")
        dialog.configure(bg="#1a5f1a")
        dialog.transient(self.root)
        dialog.grab_set()

        chosen_suit = [None]  # Use list to modify in nested function

        tk.Label(
            dialog,
            text="Choose a suit:",
            font=("Arial", 14),
            bg="#1a5f1a",
            fg="#FFFFFF"
        ).pack(pady=20)

        button_frame = tk.Frame(dialog, bg="#1a5f1a")
        button_frame.pack()

        suits = [
            (Suit.SPADES, "♠ Spades", "#000000"),
            (Suit.HEARTS, "♥ Hearts", "#DC143C"),
            (Suit.DIAMONDS, "♦ Diamonds", "#DC143C"),
            (Suit.CLUBS, "♣ Clubs", "#000000")
        ]

        def choose(suit):
            chosen_suit[0] = suit
            dialog.destroy()

        for suit, text, color in suits:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 14, "bold"),
                fg=color,
                bg="#FFFFFF",
                width=12,
                command=lambda s=suit: choose(s)
            )
            btn.pack(pady=5)

        dialog.wait_window()
        return chosen_suit[0]

    def show_game_over(self):
        """Show game over dialog."""
        winner = self.game.get_winner()

        if winner == self.game.human_player:
            title = "🏆 Victory! 🏆"
            message = "Congratulations! You won!"
        else:
            title = "Game Over"
            message = f"{winner.name} wins this round!"

        response = messagebox.askyesno(
            title,
            message + "\n\nPlay again?",
            parent=self.root
        )

        if response:
            self.start_new_game()
        else:
            self.root.quit()

    def show_help(self):
        """Show help dialog."""
        help_text = """
🎴 HOW TO PLAY SWITCH 🎴

Goal: Be the first to play all your cards!

Basic Rules:
• Click a card to play it (must match suit or rank)
• Click the Draw Pile if you can't play
• Playable cards have a green outline

Special Cards:
A  - Wild card, choose any suit
2  - Next player draws 2 (stackable!)
7  - Play multiple cards of same suit
8  - Skip next player
J  - Reverse direction
K♠/K♣ - Next player draws 5
K♥/K♦ - Defend against Black King

Tips:
• Save Aces for when you're stuck
• Stack 2s to force big draws
• Use 7s when you have many of one suit
• Remember to declare "Last Card"!

Good luck! 🍀
        """

        messagebox.showinfo("Help", help_text, parent=self.root)

    def update_status(self, text: str):
        """Update the status label."""
        self.status_label.config(text=text)

    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the GUI."""
    gui = SwitchGUI()
    gui.run()


if __name__ == "__main__":
    main()
