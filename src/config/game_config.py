"""
Game configuration for the Switch card game.
Defines toggleable rules and game settings.
"""

from dataclasses import dataclass


@dataclass
class GameConfig:
    """
    Configuration settings for the Switch game.

    Attributes:
        cumulative_penalties: Allow stacking 2s for cumulative draw penalties
        black_king_attack: Enable Black Kings to force 5-card draw
        red_king_defense: Enable Red Kings to cancel Black King attacks
        suit_run_enabled: Enable 7s to allow multi-card suit runs
        power_card_finish: Allow finishing game on Ace or 2
        initial_hand_size: Number of cards dealt to each player at start
        num_ai_players: Number of AI opponents (1-3)
    """

    # Toggleable rules (as per design document)
    cumulative_penalties: bool = True
    black_king_attack: bool = True
    red_king_defense: bool = True
    suit_run_enabled: bool = True
    power_card_finish: bool = False

    # Game settings
    initial_hand_size: int = 7
    num_ai_players: int = 3

    def validate(self):
        """
        Validate configuration settings.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.initial_hand_size < 1 or self.initial_hand_size > 13:
            raise ValueError("Initial hand size must be between 1 and 13")

        if self.num_ai_players < 1 or self.num_ai_players > 3:
            raise ValueError("Number of AI players must be between 1 and 3")

        if self.red_king_defense and not self.black_king_attack:
            raise ValueError("Red King defense requires Black King attack to be enabled")

    def __str__(self) -> str:
        return (
            f"GameConfig(\n"
            f"  Cumulative Penalties: {self.cumulative_penalties}\n"
            f"  Black King Attack: {self.black_king_attack}\n"
            f"  Red King Defense: {self.red_king_defense}\n"
            f"  Suit Run (7s): {self.suit_run_enabled}\n"
            f"  Power Card Finish: {self.power_card_finish}\n"
            f"  Initial Hand Size: {self.initial_hand_size}\n"
            f"  AI Players: {self.num_ai_players}\n"
            f")"
        )


# Default configuration
DEFAULT_CONFIG = GameConfig()

# Alternative configurations for different game modes

# Easy mode - fewer special rules
EASY_MODE_CONFIG = GameConfig(
    cumulative_penalties=False,
    black_king_attack=False,
    red_king_defense=False,
    suit_run_enabled=False,
    power_card_finish=True
)

# Hardcore mode - all rules enabled, smaller starting hand
HARDCORE_MODE_CONFIG = GameConfig(
    cumulative_penalties=True,
    black_king_attack=True,
    red_king_defense=True,
    suit_run_enabled=True,
    power_card_finish=False,
    initial_hand_size=5
)

# Quick mode - larger starting hand for faster games
QUICK_MODE_CONFIG = GameConfig(
    cumulative_penalties=True,
    black_king_attack=True,
    red_king_defense=True,
    suit_run_enabled=True,
    power_card_finish=True,
    initial_hand_size=10
)
