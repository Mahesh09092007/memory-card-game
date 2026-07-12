"""
Memory Card Matching Game
--------------------------
A desktop mini-project built with Python's Tkinter library.

Core concepts demonstrated:
    1. Lists            -> the deck of cards, list of Button widgets, list of flipped cards
    2. Buttons           -> every card is a Tkinter Button; Restart/New Game is a Button too
    3. State management  -> tracking which cards are flipped, matched, move count, timer,
                             and updating the UI (widget "state") in response to that data

Author: (your name here)
"""

import tkinter as tk
from tkinter import messagebox
import random


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
GRID_ROWS = 4
GRID_COLS = 4
TOTAL_CARDS = GRID_ROWS * GRID_COLS          # 16 cards -> 8 matching pairs
FLIP_BACK_DELAY_MS = 800                     # how long a wrong pair stays visible

# Symbols used on the cards. We only need TOTAL_CARDS // 2 unique symbols
# because each one is duplicated to form a pair.
CARD_SYMBOLS = ["🍎", "🍌", "🍇", "🍒", "🍉", "🍋", "🍑", "🥝",
                "🍓", "🥥", "🍍", "🥑", "🍈", "🍐", "🥕", "🌽"]

CARD_FACE_DOWN = "❓"
CARD_BG_DEFAULT = "#3b5998"
CARD_BG_MATCHED = "#4caf50"
CARD_BG_FLIPPED = "#f5c518"


class MemoryGame:
    """
    Encapsulates all STATE and behaviour of the memory matching game.

    Keeping state inside a class (instead of loose global variables) is a
    simple but important state-management pattern: every piece of data the
    game needs to remember between clicks lives as an attribute of `self`,
    and every UI update is a direct, deliberate reaction to a change in
    that state.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Memory Card Matching Game")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2f")

        # ---------------- STATE VARIABLES ----------------
        self.cards = []          # LIST: shuffled symbols, one per board position
        self.buttons = []        # LIST: Tkinter Button widgets, parallel to self.cards
        self.flipped = []        # LIST: indices of the (max 2) cards currently face-up
        self.matched = set()     # SET: indices of cards that are already matched
        self.moves = 0           # number of pairs the player has attempted
        self.seconds_elapsed = 0
        self.timer_running = False
        self.timer_job = None    # handle returned by root.after, used to cancel the timer

        # ---------------- UI: HEADER ----------------
        header = tk.Frame(root, bg="#1e1e2f")
        header.pack(pady=(15, 5))

        title_label = tk.Label(
            header, text="🧠 Memory Card Matching Game",
            font=("Helvetica", 20, "bold"), bg="#1e1e2f", fg="white"
        )
        title_label.pack()

        # ---------------- UI: STATUS BAR ----------------
        status_frame = tk.Frame(root, bg="#1e1e2f")
        status_frame.pack(pady=5)

        self.moves_label = tk.Label(
            status_frame, text="Moves: 0", font=("Helvetica", 12),
            bg="#1e1e2f", fg="white", padx=15
        )
        self.moves_label.grid(row=0, column=0)

        self.timer_label = tk.Label(
            status_frame, text="Time: 0s", font=("Helvetica", 12),
            bg="#1e1e2f", fg="white", padx=15
        )
        self.timer_label.grid(row=0, column=1)

        self.pairs_label = tk.Label(
            status_frame, text=f"Pairs: 0/{TOTAL_CARDS // 2}", font=("Helvetica", 12),
            bg="#1e1e2f", fg="white", padx=15
        )
        self.pairs_label.grid(row=0, column=2)

        # ---------------- UI: CARD GRID ----------------
        self.grid_frame = tk.Frame(root, bg="#1e1e2f")
        self.grid_frame.pack(pady=10, padx=10)

        # ---------------- UI: CONTROLS ----------------
        controls = tk.Frame(root, bg="#1e1e2f")
        controls.pack(pady=(0, 15))

        self.restart_button = tk.Button(
            controls, text="🔄 New Game", font=("Helvetica", 12, "bold"),
            bg="#e94560", fg="white", activebackground="#c73650",
            relief="flat", padx=15, pady=6, command=self.start_new_game
        )
        self.restart_button.pack()

        # Kick things off
        self.start_new_game()

    # -----------------------------------------------------------------
    # GAME SETUP
    # -----------------------------------------------------------------
    def start_new_game(self):
        """Resets every piece of state and rebuilds the board from scratch."""
        # Cancel any timer left running from a previous game
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)

        # --- Reset state ---
        symbols = CARD_SYMBOLS[: TOTAL_CARDS // 2] * 2   # duplicate each symbol -> pairs
        random.shuffle(symbols)                          # LIST shuffled randomly
        self.cards = symbols
        self.flipped = []
        self.matched = set()
        self.moves = 0
        self.seconds_elapsed = 0
        self.timer_running = True

        # --- Reset labels ---
        self.moves_label.config(text="Moves: 0")
        self.timer_label.config(text="Time: 0s")
        self.pairs_label.config(text=f"Pairs: 0/{TOTAL_CARDS // 2}")

        # --- Rebuild the button grid ---
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.buttons = []

        for index in range(TOTAL_CARDS):
            row, col = divmod(index, GRID_COLS)
            btn = tk.Button(
                self.grid_frame, text=CARD_FACE_DOWN,
                font=("Helvetica", 18, "bold"), width=4, height=2,
                bg=CARD_BG_DEFAULT, fg="white", relief="raised",
                activebackground=CARD_BG_FLIPPED,
                command=lambda i=index: self.on_card_click(i)
            )
            btn.grid(row=row, column=col, padx=6, pady=6)
            self.buttons.append(btn)

        self.update_timer()

    # -----------------------------------------------------------------
    # EVENT HANDLING / STATE TRANSITIONS
    # -----------------------------------------------------------------
    def on_card_click(self, index):
        """
        Called whenever a card Button is clicked.
        This is the heart of the game's state machine.
        """
        # Ignore clicks on already-matched cards, already-flipped cards,
        # or clicks while two cards are already showing (waiting to resolve).
        if index in self.matched or index in self.flipped or len(self.flipped) == 2:
            return

        self.reveal_card(index)
        self.flipped.append(index)

        if len(self.flipped) == 2:
            self.moves += 1
            self.moves_label.config(text=f"Moves: {self.moves}")
            self.root.after(FLIP_BACK_DELAY_MS, self.check_for_match)

    def reveal_card(self, index):
        """Flip a single card face-up in the UI."""
        self.buttons[index].config(text=self.cards[index], bg=CARD_BG_FLIPPED)

    def check_for_match(self):
        """Compares the two currently flipped cards and updates state accordingly."""
        first, second = self.flipped

        if self.cards[first] == self.cards[second]:
            # It's a match!
            self.matched.add(first)
            self.matched.add(second)
            self.buttons[first].config(bg=CARD_BG_MATCHED, state="disabled")
            self.buttons[second].config(bg=CARD_BG_MATCHED, state="disabled")
            self.pairs_label.config(text=f"Pairs: {len(self.matched)//2}/{TOTAL_CARDS//2}")
        else:
            # Not a match -> flip both back face-down
            self.buttons[first].config(text=CARD_FACE_DOWN, bg=CARD_BG_DEFAULT)
            self.buttons[second].config(text=CARD_FACE_DOWN, bg=CARD_BG_DEFAULT)

        self.flipped = []  # reset selection state for the next turn

        if len(self.matched) == TOTAL_CARDS:
            self.end_game()

    # -----------------------------------------------------------------
    # TIMER
    # -----------------------------------------------------------------
    def update_timer(self):
        """Ticks once per second while the game is in progress."""
        if self.timer_running:
            self.timer_label.config(text=f"Time: {self.seconds_elapsed}s")
            self.seconds_elapsed += 1
            self.timer_job = self.root.after(1000, self.update_timer)

    # -----------------------------------------------------------------
    # END OF GAME
    # -----------------------------------------------------------------
    def end_game(self):
        self.timer_running = False
        messagebox.showinfo(
            "🎉 You Won!",
            f"You matched all pairs in {self.moves} moves "
            f"and {self.seconds_elapsed} seconds!\n\nClick 'New Game' to play again."
        )


def main():
    root = tk.Tk()
    MemoryGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
