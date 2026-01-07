"""
AI player strategies for the Switch card game.
Implements The Hoarder, The Aggressor, and The Rookie AI personalities.
"""

import random
from typing import Optional, List
from ..core.card import Card, Suit, Rank
from ..core.player import AIPlayer


class HoarderAI(AIPlayer):
    """
    AI Strategy: "The Hoarder"

    Behavior:
    - Saves power cards (Ace, 2, Kings) until necessary
    - Holds Red King defensively
    - Plays low-value cards first
    - Conservative suit run usage
    """

    def __init__(self, name: str = "The Hoarder"):
        super().__init__(name, strategy="hoarder")

    def choose_card_to_play(self, top_card: Card, active_suit: Optional[Suit],
                           game_state: dict) -> Optional[Card]:
        """
        Choose a card using hoarder strategy.

        Priority:
        1. Match suit/rank with lowest value card
        2. Play defensive cards only when attacked
        3. Use power cards only when hand size > 5
        """
        playable = self.get_playable_cards(top_card, active_suit)
        if not playable:
            return None

        # Check if under attack
        pending = game_state.get('pending_effect')
        is_under_attack = pending and pending.effect_type == 'draw_king'

        # If under attack and has Red King, use it
        if is_under_attack:
            red_kings = [c for c in playable if c.is_red_king]
            if red_kings:
                return red_kings[0]

        # Separate power cards from regular cards
        power_cards = [c for c in playable if c.is_power_card or c.is_king]
        regular_cards = [c for c in playable if not (c.is_power_card or c.is_king)]

        # If hand is large (>5), willing to use power cards
        if len(self.hand) > 5:
            # Sort all playable cards by rank (lowest first)
            playable.sort(key=lambda c: c.rank.order)
            return playable[0]

        # Otherwise, prefer regular cards, play lowest value
        if regular_cards:
            regular_cards.sort(key=lambda c: c.rank.order)
            return regular_cards[0]

        # If only power cards available and hand is small, still play one
        if power_cards:
            power_cards.sort(key=lambda c: c.rank.order)
            return power_cards[0]

        return None

    def choose_suit_for_ace(self, game_state: dict) -> Suit:
        """
        Choose suit conservatively - pick the suit with most cards.
        """
        suit_counts = {suit: len(self.get_cards_of_suit(suit)) for suit in Suit}
        return max(suit_counts, key=suit_counts.get)

    def should_continue_suit_run(self, suit: Suit, game_state: dict) -> bool:
        """
        Conservative suit run - only continue if have multiple cards and they're low value.
        """
        suit_cards = self.get_cards_of_suit(suit)

        # Don't continue if only one card left
        if len(suit_cards) <= 1:
            return False

        # Don't continue if next card is a power card (save it)
        if suit_cards[0].is_power_card or suit_cards[0].is_king:
            return False

        # Continue if have 3+ cards of that suit
        if len(suit_cards) >= 3:
            return True

        return False

    def should_forget_last_card_declaration(self) -> bool:
        """Hoarder never forgets (0% chance)."""
        return False


class AggressorAI(AIPlayer):
    """
    AI Strategy: "The Aggressor"

    Behavior:
    - Plays offensive cards immediately
    - Uses 2s and Black Kings at first opportunity
    - Maximizes suit runs to empty hand quickly
    - Changes suits frequently with Aces
    """

    def __init__(self, name: str = "The Aggressor"):
        super().__init__(name, strategy="aggressor")

    def choose_card_to_play(self, top_card: Card, active_suit: Optional[Suit],
                           game_state: dict) -> Optional[Card]:
        """
        Choose a card using aggressive strategy.

        Priority:
        1. Play Black King if available
        2. Play 2 if available
        3. Play 7 with longest suit run
        4. Play Ace to most common suit in hand
        """
        playable = self.get_playable_cards(top_card, active_suit)
        if not playable:
            return None

        # Priority 1: Black King (attack)
        black_kings = [c for c in playable if c.is_black_king]
        if black_kings:
            return black_kings[0]

        # Priority 2: Two (draw two)
        twos = [c for c in playable if c.is_two]
        if twos:
            return twos[0]

        # Priority 3: Seven (suit run) - pick the 7 with most cards of that suit
        sevens = [c for c in playable if c.is_seven]
        if sevens:
            best_seven = max(sevens, key=lambda c: len(self.get_cards_of_suit(c.suit)))
            return best_seven

        # Priority 4: Ace (to force suit change)
        aces = [c for c in playable if c.is_ace]
        if aces:
            return aces[0]

        # Otherwise, play highest value card to get rid of it
        playable.sort(key=lambda c: c.rank.order, reverse=True)
        return playable[0]

    def choose_suit_for_ace(self, game_state: dict) -> Suit:
        """
        Choose the suit with most cards to maximize options.
        """
        suit_counts = {suit: len(self.get_cards_of_suit(suit)) for suit in Suit}
        return max(suit_counts, key=suit_counts.get)

    def should_continue_suit_run(self, suit: Suit, game_state: dict) -> bool:
        """
        Aggressive suit run - continue as long as possible.
        """
        suit_cards = self.get_cards_of_suit(suit)

        # Continue if have any cards left of that suit
        if len(suit_cards) > 0:
            return True

        return False

    def should_forget_last_card_declaration(self) -> bool:
        """Aggressor never forgets (0% chance)."""
        return False


class RookieAI(AIPlayer):
    """
    AI Strategy: "The Rookie"

    Behavior:
    - Makes suboptimal decisions
    - 10% chance to forget "Last Card" declaration
    - Poor Ace suit choices
    - Doesn't maximize suit runs
    """

    def __init__(self, name: str = "The Rookie"):
        super().__init__(name, strategy="rookie")

    def choose_card_to_play(self, top_card: Card, active_suit: Optional[Suit],
                           game_state: dict) -> Optional[Card]:
        """
        Choose a card using rookie strategy (random/suboptimal).

        Priority:
        1. Play any matching card (random selection)
        2. Occasionally plays high-value cards early
        """
        playable = self.get_playable_cards(top_card, active_suit)
        if not playable:
            return None

        # Just pick a random card most of the time
        return random.choice(playable)

    def choose_suit_for_ace(self, game_state: dict) -> Suit:
        """
        Choose suit randomly (poor choice).
        """
        return random.choice(list(Suit))

    def should_continue_suit_run(self, suit: Suit, game_state: dict) -> bool:
        """
        Random decision on suit run continuation (doesn't maximize).
        """
        suit_cards = self.get_cards_of_suit(suit)

        if len(suit_cards) == 0:
            return False

        # 50% chance to continue even if it would be beneficial
        return random.random() < 0.5

    def should_forget_last_card_declaration(self) -> bool:
        """Rookie has 10% chance to forget."""
        return random.random() < 0.1


def create_ai_player(ai_type: str, name: Optional[str] = None) -> AIPlayer:
    """
    Factory function to create AI players.

    Args:
        ai_type: Type of AI ("hoarder", "aggressor", or "rookie")
        name: Optional custom name for the AI

    Returns:
        An AI player instance

    Raises:
        ValueError: If ai_type is invalid
    """
    ai_type = ai_type.lower()

    if ai_type == "hoarder":
        return HoarderAI(name or "The Hoarder")
    elif ai_type == "aggressor":
        return AggressorAI(name or "The Aggressor")
    elif ai_type == "rookie":
        return RookieAI(name or "The Rookie")
    else:
        raise ValueError(f"Invalid AI type: {ai_type}. Must be 'hoarder', 'aggressor', or 'rookie'")


def create_default_ai_opponents(count: int = 3) -> List[AIPlayer]:
    """
    Create default AI opponents for a game.

    Args:
        count: Number of AI opponents (1-3)

    Returns:
        List of AI players
    """
    if count < 1 or count > 3:
        raise ValueError("Number of AI opponents must be between 1 and 3")

    ai_players = []

    # Always include these in order
    ai_types = [
        ("hoarder", "The Hoarder"),
        ("aggressor", "The Aggressor"),
        ("rookie", "The Rookie")
    ]

    for i in range(count):
        ai_type, name = ai_types[i]
        ai_players.append(create_ai_player(ai_type, name))

    return ai_players
