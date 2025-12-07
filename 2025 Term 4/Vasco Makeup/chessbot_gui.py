import tkinter as tk
import chess
import chess.engine

# Change this if needed (check with: which stockfish)
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

SQUARE_SIZE = 64  # pixels
BOARD_COLOR_LIGHT = "#f0d9b5"
BOARD_COLOR_DARK = "#b58863"
BOARD_COLOR_HIGHLIGHT = "#f6f669"

# Unicode chess pieces
PIECE_UNICODE = {
    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
}


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("python-chess + Stockfish")

        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        # Optional: lower the skill to make it friendlier
        try:
            self.engine.configure({"Skill Level": 5})
        except chess.engine.EngineError:
            pass

        self.selected_square = None  # currently selected from-square (chess.SQUARE or None)
        self.engine_thinking = False

        self.canvas = tk.Canvas(
            root,
            width=8 * SQUARE_SIZE,
            height=8 * SQUARE_SIZE,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.status_label = tk.Label(root, text="You are White. Click a piece to move.")
        self.status_label.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.new_game_button = tk.Button(button_frame, text="New Game", command=self.new_game)
        self.new_game_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = tk.Button(button_frame, text="Quit", command=self.on_quit)
        self.quit_button.pack(side=tk.LEFT, padx=5)

        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

    def new_game(self):
        self.board.reset()
        self.selected_square = None
        self.engine_thinking = False
        self.set_status("New game started. You are White.")
        self.draw_board()

    def on_quit(self):
        try:
            self.engine.quit()
        except Exception:
            pass
        self.root.destroy()

    def set_status(self, text):
        self.status_label.config(text=text)

    def on_click(self, event):
        if self.engine_thinking:
            return  # Ignore clicks while engine is moving

        if self.board.is_game_over():
            self.set_status(f"Game over: {self.board.result()}")
            return

        # We only allow the human to move as White
        if self.board.turn != chess.WHITE:
            self.set_status("It's not your turn.")
            return

        file = event.x // SQUARE_SIZE  # 0..7 (a..h)
        rank = 7 - (event.y // SQUARE_SIZE)  # 0..7 (1..8) - invert y
        square = chess.square(file, rank)

        if self.selected_square is None:
            # First click: select a piece (ideally a White piece)
            piece = self.board.piece_at(square)
            if piece is None or piece.color != chess.WHITE:
                self.set_status("Select one of your (White) pieces.")
                return
            self.selected_square = square
            self.set_status(f"Selected {chess.square_name(square)}. Now click destination.")
        else:
            # Second click: attempt move
            from_sq = self.selected_square
            to_sq = square
            move = chess.Move(from_sq, to_sq)

            # Handle promotions (very simple: auto-queen)
            if chess.square_rank(from_sq) == 6 and chess.square_rank(to_sq) == 7 and self.board.piece_at(from_sq).piece_type == chess.PAWN:
                move.promotion = chess.QUEEN

            if move in self.board.legal_moves:
                san = self.board.san(move)      # <-- get SAN *before* push
                self.board.push(move)
                self.selected_square = None
                self.draw_board()

                if self.board.is_game_over():
                    self.set_status(f"Game over: {self.board.result()}")
                else:
                    self.set_status(f"You played {san}. Engine is thinking...")
                    self.root.after(100, self.engine_move)

            else:
                # Invalid move
                self.set_status("Illegal move. Try again.")
                self.selected_square = None

        self.draw_board()

    def engine_move(self):
        if self.board.is_game_over():
            return

        self.engine_thinking = True
        try:
            # Limit engine time so GUI doesn't freeze too long
            result = self.engine.play(self.board, chess.engine.Limit(time=0.3))
            san = self.board.san(result.move)
            self.board.push(result.move)
            self.set_status(f"Engine played {san}. Your turn.")
        except Exception as e:
            self.set_status(f"Engine error: {e}")
        finally:
            self.engine_thinking = False
            self.draw_board()
            if self.board.is_game_over():
                self.set_status(f"Game over: {self.board.result()}")

    def draw_board(self):
        self.canvas.delete("all")

        # Draw squares
        for rank in range(8):
            for file in range(8):
                x1 = file * SQUARE_SIZE
                y1 = (7 - rank) * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                square = chess.square(file, rank)

                if (file + rank) % 2 == 0:
                    fill = BOARD_COLOR_LIGHT
                else:
                    fill = BOARD_COLOR_DARK

                # Highlight selected square
                if self.selected_square == square:
                    fill = BOARD_COLOR_HIGHLIGHT

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="black")

                piece = self.board.piece_at(square)
                if piece:
                    symbol = PIECE_UNICODE[piece.symbol()]
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=symbol,
                        font=("Arial", 36),
                    )


if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()
