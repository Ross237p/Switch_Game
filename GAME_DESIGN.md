# Game Design Document: Switch

## 1. Executive Summary
**Title:** Switch
**Genre:** Card Game - Shedding/Last Card Out
**Players:** 1 Player vs. 3 AI Opponents
**Core Loop:** Players take turns matching cards by suit or rank, using special cards strategically to force opponents to draw cards while emptying their own hand.

## 2. Core Rules

### Setup
- Standard 52-card deck
- Deal 7 cards to each player
- Remaining cards form the draw pile
- Top card flipped to start the discard pile
- Play proceeds clockwise

### Basic Play
- On your turn, play a card matching the top card by suit or rank
- If you cannot play, draw one card from the pile
- If the drawn card is playable, you may play it immediately
- Otherwise, turn ends

### Win Condition
- First player to empty their hand wins
- Must declare "Last Card" before playing second-to-last card (penalty: draw 1 card if forgotten)

## 3. Special Cards

### Ace (Wild Card)
- Can be played on any card regardless of suit or rank
- Player must declare the new suit
- Example: 6♥ on pile → play A♠ → declare Spades as new suit

### 2 (Draw Two)
- Next player draws 2 cards and loses their turn
- **Stackable:** Can play another 2 to add to penalty (becomes 4 cards)
- Stacking continues until a player cannot add another 2
- That player draws the accumulated total

### 7 (Suit Run)
- Allows player to play multiple cards of the same suit in sequence
- All cards must share the 7's suit
- Player continues playing cards of that suit until they choose to stop or run out

### 8 (Skip)
- Next player loses their turn
- Play passes to the following player

### Jack (Reverse)
- Reverses direction of play
- Clockwise → Counter-clockwise (or vice versa)

### Black King ♠/♣ (Attack)
- Next player must draw 5 cards and lose their turn
- Can be defended

### Red King ♥/♦ (Defense)
- Cancels a Black King attack
- Play immediately passes to next player
- No cards are drawn

## 4. Configuration Options

### Toggleable Rules
- **Cumulative Penalties** (Default: ON) - Allow stacking 2s
- **Black King Attack** (Default: ON) - Black Kings force 5-card draw
- **Red King Defense** (Default: ON) - Red Kings cancel Black King
- **7 Suit Run** (Default: ON) - 7s enable multi-card plays
- **Power Card Finish** (Default: OFF) - Can/cannot end game on Ace or 2

## 5. Gameplay Mechanics

### A. The "Last Card" Declaration
- Must be declared before playing second-to-last card
- Failure to declare results in penalty: draw 1 card
- Turn continues after penalty

### B. Suit Run (7) Mechanic
**Trigger:** Player plays a 7

**Process:**
1. Player may now play additional cards of the 7's suit
2. Cards are played one at a time in sequence
3. Player decides when to stop or plays all cards of that suit
4. Turn ends when player stops or has no more cards of that suit

**Power Card Restriction:**
- If "Power Card Finish" is disabled and the final card in the run is an Ace or 2:
  - The card cannot be played
  - Player must draw 1 card
  - Turn ends

### C. Attack/Defense (King) Mechanic

**Attack Sequence:**
1. Player A plays Black King (♠ or ♣)
2. Penalty queued: 5 cards

**Player B's Options:**
- **Option 1 (Defense):** Play Red King (♥ or ♦)
  - Attack canceled
  - Play passes to Player C
  - No cards drawn

- **Option 2 (No Defense):** No Red King available
  - Draw 5 cards
  - Turn ends

### D. Cumulative Draw (2s) Mechanic

**Example Sequence:**
1. Player A plays 2 (Penalty: 2 cards)
2. Player B plays 2 (Penalty: 4 cards)
3. Player C plays 2 (Penalty: 6 cards)
4. Player D has no 2
5. Player D draws 6 cards, turn ends

**Rules:**
- Each 2 adds 2 to the penalty counter
- Chain continues until a player cannot stack
- That player draws the total accumulated penalty

### E. Wild Card (Ace) Mechanic

**Trigger:** Player plays an Ace

**Process:**
1. Player declares new suit (♠ ♥ ♦ ♣)
2. Ace is placed on discard pile
3. Next player must match the declared suit or play a special card

## 6. AI Behavior Profiles

### AI 1: "The Hoarder"
**Strategy:**
- Saves power cards (Ace, 2, Kings) until necessary
- Holds Red King defensively
- Plays low-value cards first
- Conservative suit run usage

**Decision Priority:**
1. Match suit/rank with lowest value card
2. Play defensive cards only when attacked
3. Use power cards only when hand size > 5

### AI 2: "The Aggressor"
**Strategy:**
- Plays offensive cards immediately
- Uses 2s and Black Kings at first opportunity
- Maximizes suit runs to empty hand quickly
- Changes suits frequently with Aces

**Decision Priority:**
1. Play Black King if available
2. Play 2 if available
3. Play 7 with longest suit run
4. Play Ace to most common suit in hand

### AI 3: "The Rookie"
**Strategy:**
- Makes suboptimal decisions
- 10% chance to forget "Last Card" declaration (draws penalty)
- Poor Ace suit choices
- Doesn't maximize suit runs

**Decision Priority:**
1. Play any matching card (random selection)
2. Occasionally plays high-value cards early
3. Random suit declaration on Aces
4. 10% chance to skip "Last Card" declaration

## 7. Game Flow

### Turn Structure
1. Check for pending effects (skip, draw penalty, attack)
2. Player evaluates hand
3. Player plays valid card OR draws from pile
4. Special card effects resolve
5. Check for "Last Card" declaration requirement
6. Check win condition
7. Next player's turn

### Priority of Effects
1. **Skip (8)** - Player loses turn entirely
2. **Draw penalties (2 or Black King)** - Must resolve before playing
3. **Reverse (Jack)** - Changes turn order
4. **Suit change (Ace)** - Affects next player's options
5. **Suit run (7)** - Allows current player extended turn

## 8. Edge Cases & Rules Clarifications

### Multiple Special Cards in Suit Run
- If playing 7♠ and hand contains 8♠, J♠, 2♠:
  - All can be played in the run
  - Effects queue and resolve after run completes
  - Order matters: 2♠ then 8♠ means next player draws 2 then skips

### Ace After Draw Penalty
- If you draw cards from a penalty, you may play an Ace if drawn
- Ace cancels suit requirement, not the penalty itself

### Last Two Cards Both Special
- If second-to-last card is a 7, can still play suit run
- If last card after "Last Card" declaration is illegal due to Power Card rule, must draw penalty

### Reverse with 2 Players Remaining
- Jack simply passes turn back to other player
- Effectively acts as a skip

## 9. Scoring System (Optional)

### Points Calculation
At end of each round, remaining cards in opponent hands:
- Number cards (2-10): Face value
- Jack, Queen, King: 10 points each
- Ace: 15 points each

Winner scores total of all opponent cards.

### Match Formats
- **Single Round:** First to empty hand wins
- **First to 100:** Play multiple rounds until a player reaches 100 points
- **Best of 5:** Win 3 rounds to win match

## 10. Strategy Guide

### Key Tactics
- **Defense Management:** Hold Red King when Black Kings haven't been played yet
- **Suit Control:** Use Aces to force opponents into suits they're weak in
- **Penalty Baiting:** Play 2s early to force draws when opponents have large hands
- **Run Timing:** Save 7s for when you have 4+ cards of that suit
- **Card Counting:** Track which special cards have been played

### Common Mistakes
- Playing power cards too early
- Forgetting "Last Card" declaration
- Poor Ace suit choices (declaring suit you have none of)
- Not defending against Black King when holding Red King
- Ending suit run prematurely
