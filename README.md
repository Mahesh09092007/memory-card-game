# 🧠 Memory Card Matching Game

A simple desktop mini-project built in **Python** using the **Tkinter** GUI
library. Flip cards two at a time and try to find every matching pair in
the fewest moves and the shortest time.

This project was built to practice three core programming concepts:

| Concept | Where it shows up |
|---|---|
| **Lists** | The shuffled deck of card symbols (`self.cards`), the list of Button widgets (`self.buttons`), and the list of currently flipped card indices (`self.flipped`) |
| **Buttons** | Every card on the board is a `tkinter.Button`; there's also a "New Game" button that resets the board |
| **State management** | The `MemoryGame` class tracks moves, matched pairs, flipped cards, and elapsed time, and updates the UI every time that state changes |

---

## 🎮 How to Play

1. Run the game (see [Installation](#-installation--running) below).
2. Click any face-down card to flip it over.
3. Click a second card. If the two symbols match, they stay face-up
   (turn green) and are removed from play.
4. If they don't match, both cards flip back face-down after a short
   delay.
5. Match all 8 pairs to win! Your move count and time are shown at the
   top, and a pop-up congratulates you when you finish.
6. Click **🔄 New Game** at any time to reshuffle and start over.

---

## 📂 Project Structure

```
memory-card-game/
├── main.py            # All game logic and UI (single-file app)
├── README.md           # Project documentation (this file)
├── requirements.txt    # Dependency notes (stdlib only)
└── .gitignore           # Common Python ignores
```

---

## 🛠️ Installation & Running

### Requirements
- Python 3.8 or newer
- `tkinter` (included with most Python installations)

**If tkinter is missing:**
- **Windows / macOS:** it's bundled with the official Python installer
  from [python.org](https://www.python.org/downloads/) — nothing extra
  to do.
- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt-get install python3-tk
  ```
- **Linux (Fedora):**
  ```bash
  sudo dnf install python3-tkinter
  ```

### Run the game
```bash
git clone https://github.com/<your-username>/memory-card-game.git
cd memory-card-game
python3 main.py
```

No `pip install` step is required — the project only uses Python's
standard library.

---

## 🧩 Concepts Explained

### 1. Lists
- `CARD_SYMBOLS` — a master list of possible card symbols (emojis).
- `self.cards` — built by taking half of `CARD_SYMBOLS`, duplicating it
  (`* 2`), and shuffling it with `random.shuffle()` so every symbol
  appears exactly twice, in a random position.
- `self.buttons` — a list of Tkinter `Button` widgets, one per board
  position, kept in the same order as `self.cards` so index `i` in
  `self.buttons` always corresponds to index `i` in `self.cards`.
- `self.flipped` — a small list (max length 2) holding the indices of
  the cards currently face-up while the player is deciding.

### 2. Buttons
- Each of the 16 cards is a `tkinter.Button`. Its `command` is bound
  with a lambda that captures its own index (`lambda i=index: ...`),
  which is the standard Tkinter pattern for wiring up many buttons in
  a loop without them all sharing the same (last) index.
- Button appearance (`text`, `bg`, `state`) is changed directly to
  reflect game state: face-down (`❓`), flipped (`🍎`, yellow
  background), or matched (green background, disabled).
- A separate "New Game" button calls `start_new_game()`, which resets
  all state and rebuilds the grid.

### 3. State Management
All game state lives as attributes on the `MemoryGame` class instance,
rather than as scattered global variables:

| Attribute | Purpose |
|---|---|
| `self.cards` | The shuffled symbol for every board position |
| `self.flipped` | Indices of cards currently face-up (0, 1, or 2 of them) |
| `self.matched` | A `set` of indices that have already been matched |
| `self.moves` | Number of pairs attempted so far |
| `self.seconds_elapsed` | Elapsed game time, updated once per second |

Every user action (a card click) triggers a **state transition**:
1. Update the relevant state variable(s).
2. Immediately reflect that change in the UI (recolor/re-text a
   button, update a label).
3. If the new state satisfies a condition (two cards flipped, all
   pairs matched), trigger the next step (`check_for_match`,
   `end_game`) — optionally after a delay via `root.after(...)`, which
   is Tkinter's non-blocking way of scheduling a future state change
   (used here so the second wrong card stays visible briefly before
   flipping back).

This "single source of truth" pattern — state lives in one place, and
the UI is always just a reflection of that state — is the same idea
behind state management in larger frameworks like React or Flutter,
just implemented by hand with plain Python.

---

## 🚀 Possible Improvements

- [ ] Add difficulty levels (4x4, 6x6 grids)
- [ ] Add sound effects for flips, matches, and wins
- [ ] Persist a "best score" (fewest moves / fastest time) to a file
- [ ] Add a countdown/limited-moves challenge mode
- [ ] Replace emoji cards with custom images

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

Built as a mini-project to practice Python GUI programming with
Tkinter — specifically lists, event-driven buttons, and manual state
management.
