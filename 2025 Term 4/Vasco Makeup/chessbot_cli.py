import chess
import chess.engine

STOCKFISH_PATH = r"/opt/homebrew/bin/stockfish"

def main():
    # Create a board
    board = chess.Board()

    # Start the engine
    engine = chess.engine.SimpleEngine.popen(STOCKFISH_PATH)

    # Set Stockfish skill level (0–20)
    try:
        engine.configure({"Skill Level": 5})
    except chess.engine.EngineError:
        pass

    print("Welcome! You are White. Enter moves in SAN (e.g. e4, Nf3, exd5, O-O).")
    print("Type 'quit' to exit.\n")

    while not board.is_game_over():
        print(board)
        print("FEN:", board.fen())
        print()

        # Human move (white)
        move_san = input("Your move: ").strip()
        if move_san.lower() in ["quit", "exit"]:
            break

        try:
            move = board.parse_san(move_san)
        except ValueError:
            print("Invalid move format or illegal move. Try again.\n")
            continue

        board.push(move)

        if board.is_game_over():
            break

        # Engine move (black)
        print("\nThinking...")
        # Limit the engine either by time or by depth
        result = engine.play(board, chess.engine.Limit(time=0.5))
        board.push(result.move)
        print("Engine plays:", board.san(result.move), "\n")

    print(board)
    print("Game over:", board.result(), "-", board.outcome())
    engine.quit()

if __name__ == "__main__":
    main()
