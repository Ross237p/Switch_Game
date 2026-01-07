# Switch - Card Game

A Python implementation of the classic card game **Switch** (also known as Crazy Eights or Last Card). Play against 3 AI opponents with unique strategies in this exciting shedding-style card game!

## 🎮 Game Overview

**Switch** is a card game where the goal is to be the first player to empty your hand. Players take turns matching cards by suit or rank, using special cards strategically to force opponents to draw cards while emptying their own hand.

## ✨ Features

- **Single Player vs 3 AI**: Play against three AI opponents with distinct personalities
  - **The Hoarder**: Saves power cards, plays defensively
  - **The Aggressor**: Plays offensively, uses attacks immediately
  - **The Rookie**: Makes suboptimal decisions, unpredictable play

- **Special Cards**:
  - **Ace**: Wild card - play on anything and choose the suit
  - **2**: Draw Two - next player draws 2 cards (stackable!)
  - **7**: Suit Run - play multiple cards of the same suit
  - **8**: Skip - next player loses their turn
  - **Jack**: Reverse - reverses the direction of play
  - **Black Kings (♠/♣)**: Attack - next player draws 5 cards
  - **Red Kings (♥/♦)**: Defense - cancel Black King attacks

- **Configurable Rules**: Toggle various game mechanics on/off
- **Command-Line Interface**: Simple and intuitive text-based UI
- **Smart AI Strategies**: Each AI has unique decision-making patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Switch_Game
```

2. No additional dependencies required! The game uses only Python standard library.

### Running the Game

Simply run:

```bash
python main.py
```

Or make it executable:

```bash
chmod +x main.py
./main.py
```

## 🎯 How to Play

### Basic Rules

1. Match the top card by **suit** or **rank**
2. If you can't play, **draw one card**
3. Declare "Last Card" when you have 2 cards remaining
4. First player to empty their hand **wins**!

### Special Card Effects

| Card | Effect |
|------|--------|
| **A** | Wild card - choose any suit |
| **2** | Next player draws 2 cards (can be stacked) |
| **7** | Play multiple cards of the same suit in sequence |
| **8** | Skip the next player's turn |
| **J** | Reverse the direction of play |
| **K♠/K♣** | Next player must draw 5 cards |
| **K♥/K♦** | Cancel a Black King attack |

### Game Controls

During your turn:
- **[number]** - Play the card at that position
- **d** - Draw a card
- **h** - Show help/rules
- **q** - Quit game

## 🏗️ Project Structure

```
Switch_Game/
├── main.py                 # Main entry point
├── GAME_DESIGN.md         # Complete game design document
├── README.md              # This file
└── src/
    ├── core/              # Core game logic
    │   ├── card.py        # Card, Suit, and Rank definitions
    │   ├── deck.py        # Deck and DiscardPile classes
    │   ├── player.py      # Player classes (Human and AI)
    │   ├── game_state.py  # Game state and rules engine
    │   └── game_manager.py # Game flow orchestration
    ├── ai/                # AI strategies
    │   └── strategies.py  # AI player implementations
    ├── config/            # Configuration
    │   └── game_config.py # Game settings and toggleable rules
    └── ui/                # User interface
        └── cli.py         # Command-line interface
```

## ⚙️ Configuration

The game supports various configurable rules in `src/config/game_config.py`:

```python
GameConfig(
    cumulative_penalties=True,   # Allow stacking 2s
    black_king_attack=True,      # Black Kings force 5-card draw
    red_king_defense=True,       # Red Kings can defend
    suit_run_enabled=True,       # 7s enable multi-card plays
    power_card_finish=False,     # Can/cannot finish on Ace or 2
    initial_hand_size=7,         # Starting hand size
    num_ai_players=3             # Number of AI opponents (1-3)
)
```

### Preset Configurations

- **Default Mode**: All special rules enabled
- **Easy Mode**: Fewer special rules, simpler gameplay
- **Hardcore Mode**: All rules enabled, smaller starting hand (5 cards)
- **Quick Mode**: Larger starting hand (10 cards), power card finish allowed

## 🎲 Strategy Tips

1. **Save your Aces** - Use them to change suits when stuck
2. **Hold Red Kings defensively** - Protect against Black King attacks
3. **Stack 2s aggressively** - Force opponents to draw many cards
4. **Use 7s wisely** - Play suit runs when you have 4+ cards of one suit
5. **Remember "Last Card"** - Don't forget to declare or you'll draw a penalty!

## 🧪 Testing

Run tests with:

```bash
python -m pytest tests/
```

(Note: Test suite to be implemented)

## 📝 Game Design

For complete game rules, mechanics, and design decisions, see [GAME_DESIGN.md](GAME_DESIGN.md).

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Improve AI strategies
- Add new game modes
- Enhance the UI

## 📄 License

This project is open source and available under the MIT License.

## 🎉 Credits

Game design based on the classic card game "Switch" (also known as Crazy Eights).

Implementation by [Your Name]

---

**Enjoy the game! 🎴**
