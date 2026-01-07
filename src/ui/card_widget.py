"""
Card rendering for the GUI version of Switch.
Creates visual representations of cards using Tkinter.
"""

import tkinter as tk
from tkinter import font
from typing import Tuple
from ..core.card import Card, Suit, Rank


# Color scheme
CARD_BG = "#FFFFFF"
CARD_BORDER = "#000000"
RED_COLOR = "#DC143C"
BLACK_COLOR = "#000000"
CARD_BACK_COLOR = "#1E3A8A"
CARD_BACK_PATTERN = "#3B82F6"

# Card dimensions
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_CORNER_RADIUS = 8


class CardWidget:
    """
    Visual representation of a card using Tkinter canvas.
    """

    def __init__(self, canvas: tk.Canvas, card: Card, x: int, y: int,
                 face_up: bool = True, clickable: bool = False):
        """
        Create a card widget.

        Args:
            canvas: The canvas to draw on
            card: The card to display
            x, y: Position on canvas
            face_up: Whether to show the card face or back
            clickable: Whether the card can be clicked
        """
        self.canvas = canvas
        self.card = card
        self.x = x
        self.y = y
        self.face_up = face_up
        self.clickable = clickable
        self.selected = False

        self.elements = []  # Store canvas element IDs
        self.draw()

    def draw(self):
        """Draw the card on the canvas."""
        # Clear existing elements
        for elem in self.elements:
            self.canvas.delete(elem)
        self.elements = []

        if self.face_up:
            self._draw_face()
        else:
            self._draw_back()

    def _draw_face(self):
        """Draw the card face."""
        # Card background
        y_offset = -10 if self.selected else 0

        # Outer border
        rect = self.canvas.create_rectangle(
            self.x, self.y + y_offset,
            self.x + CARD_WIDTH, self.y + CARD_HEIGHT + y_offset,
            fill=CARD_BG,
            outline=CARD_BORDER,
            width=2
        )
        self.elements.append(rect)

        # Determine color
        color = RED_COLOR if self.card.suit.is_red else BLACK_COLOR

        # Rank (top-left)
        rank_text = self.canvas.create_text(
            self.x + 10, self.y + 15 + y_offset,
            text=str(self.card.rank),
            font=("Arial", 16, "bold"),
            fill=color
        )
        self.elements.append(rank_text)

        # Suit symbol (top-left, below rank)
        suit_text = self.canvas.create_text(
            self.x + 10, self.y + 35 + y_offset,
            text=str(self.card.suit),
            font=("Arial", 20),
            fill=color
        )
        self.elements.append(suit_text)

        # Large centered suit symbol
        center_suit = self.canvas.create_text(
            self.x + CARD_WIDTH // 2, self.y + CARD_HEIGHT // 2 + y_offset,
            text=str(self.card.suit),
            font=("Arial", 36),
            fill=color
        )
        self.elements.append(center_suit)

        # Rank (bottom-right, rotated)
        rank_text_bottom = self.canvas.create_text(
            self.x + CARD_WIDTH - 10, self.y + CARD_HEIGHT - 15 + y_offset,
            text=str(self.card.rank),
            font=("Arial", 16, "bold"),
            fill=color,
            angle=180
        )
        self.elements.append(rank_text_bottom)

        # Suit symbol (bottom-right, rotated)
        suit_text_bottom = self.canvas.create_text(
            self.x + CARD_WIDTH - 10, self.y + CARD_HEIGHT - 35 + y_offset,
            text=str(self.card.suit),
            font=("Arial", 20),
            fill=color,
            angle=180
        )
        self.elements.append(suit_text_bottom)

        # Highlight if selected
        if self.selected:
            highlight = self.canvas.create_rectangle(
                self.x - 2, self.y + y_offset - 2,
                self.x + CARD_WIDTH + 2, self.y + CARD_HEIGHT + y_offset + 2,
                outline="#FFD700",
                width=3
            )
            self.elements.insert(0, highlight)

    def _draw_back(self):
        """Draw the card back."""
        # Card background
        rect = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + CARD_WIDTH, self.y + CARD_HEIGHT,
            fill=CARD_BACK_COLOR,
            outline=CARD_BORDER,
            width=2
        )
        self.elements.append(rect)

        # Pattern (diagonal lines)
        for i in range(0, CARD_WIDTH + CARD_HEIGHT, 15):
            line = self.canvas.create_line(
                self.x + i, self.y,
                self.x, self.y + i,
                fill=CARD_BACK_PATTERN,
                width=2
            )
            self.elements.append(line)

        # Logo text
        logo = self.canvas.create_text(
            self.x + CARD_WIDTH // 2, self.y + CARD_HEIGHT // 2,
            text="🎴",
            font=("Arial", 32),
            fill=CARD_BACK_PATTERN
        )
        self.elements.append(logo)

    def set_position(self, x: int, y: int):
        """Move the card to a new position."""
        dx = x - self.x
        dy = y - self.y
        self.x = x
        self.y = y

        for elem in self.elements:
            self.canvas.move(elem, dx, dy)

    def set_selected(self, selected: bool):
        """Set whether the card is selected."""
        if self.selected != selected:
            self.selected = selected
            self.draw()

    def is_clicked(self, event_x: int, event_y: int) -> bool:
        """Check if a click position is on this card."""
        return (self.x <= event_x <= self.x + CARD_WIDTH and
                self.y <= event_y <= self.y + CARD_HEIGHT)

    def destroy(self):
        """Remove the card from the canvas."""
        for elem in self.elements:
            self.canvas.delete(elem)
        self.elements = []


class DeckWidget:
    """Visual representation of the deck."""

    def __init__(self, canvas: tk.Canvas, x: int, y: int, count: int = 0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.count = count
        self.elements = []
        self.draw()

    def draw(self):
        """Draw the deck."""
        for elem in self.elements:
            self.canvas.delete(elem)
        self.elements = []

        # Draw 3 offset card backs to show stack
        for i in range(3):
            offset = i * 2
            rect = self.canvas.create_rectangle(
                self.x + offset, self.y + offset,
                self.x + CARD_WIDTH + offset, self.y + CARD_HEIGHT + offset,
                fill=CARD_BACK_COLOR,
                outline=CARD_BORDER,
                width=2
            )
            self.elements.append(rect)

        # Count text
        if self.count > 0:
            count_text = self.canvas.create_text(
                self.x + CARD_WIDTH // 2 + 4, self.y + CARD_HEIGHT + 20,
                text=f"{self.count} cards",
                font=("Arial", 12),
                fill="#FFFFFF"
            )
            self.elements.append(count_text)

    def update_count(self, count: int):
        """Update the deck count."""
        self.count = count
        self.draw()

    def is_clicked(self, event_x: int, event_y: int) -> bool:
        """Check if the deck was clicked."""
        return (self.x <= event_x <= self.x + CARD_WIDTH + 6 and
                self.y <= event_y <= self.y + CARD_HEIGHT + 6)
