import chess
import chess.engine

STOCKFISH_PATH = r"/opt/homebrew/bin/stockfish"

def main():
    # Create a board
    board = chess.Board()

    # Start engine
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    # Set Stockfish skill level (0-20)
    try:
        engine.configure({"Skill Level": 5})
    except chess.engine.EngineError:
        pass

    print("Welcome! You are White. Enter moves in SAN (e.g. e4, Nf3, exd5, 0-0).")
    print("Type 'quit' to exit.\n")

    while not board.is_game_over():
        print(board)
        print("FEN:", board.fen())
        print()
    
        # Human move (white)
        move_san = input("Your move: ").strip()

if __name__ == "__main__":
    main()
