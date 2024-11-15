import os
import ast
import chess
import chess.pgn
import chess.engine
import pandas as pd
from datetime import datetime
import math
from tqdm import tqdm

# directory_path = "C:\\Users\\Peter\\Documents\\GitHub\\chess-engine\\FeatureGrabbingBot\\data\\pgn" # Windows path
directory_path = "/Users/peterheroux/Documents/GitHub/chess_bots/FeatureGrabbingBot/data/pgn"  # Mac path

# Initialize an empty list to hold all the game data
games_data = []

engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")

start = datetime.now()

def evaluate_position(board, engine, limit):
    info = engine.analyse(board, limit)
    score = info['score'].white().score(mate_score=1000)
    return score

for filename in tqdm(os.listdir(directory_path), desc='Processing files'):
    file_path = os.path.join(directory_path, filename)
    if os.path.isfile(file_path):  # Ensure it's a file and not a subdirectory
        with open(file_path, 'r') as pgn:
            # Use chess.pgn to parse the PGN file
            while True:
                game = chess.pgn.read_game(pgn)
                if game is None:
                    break  # No more games in the file

                headers = game.headers
                game_data = {
                    'Event': headers.get('Event', ''),
                    'Site': headers.get('Site', ''),
                    'Date': headers.get('Date', ''),
                    'White': headers.get('White', ''),
                    'Black': headers.get('Black', ''),
                    'Result': headers.get('Result', ''),
                    'WhiteElo': headers.get('WhiteElo', ''),
                    'BlackElo': headers.get('BlackElo', ''),
                    'ECO': headers.get('ECO', ''),
                    'Opening': headers.get('ECO', ''),
                    'Termination': headers.get('Termination', ''),
                    # Add other headers as needed
                }

                # Extract moves in UCI notation
                moves = [move.uci() for move in game.mainline_moves()]
                game_data['Moves'] = moves  # Store moves in the game data

                # Append the game data to the list
                games_data.append(game_data)

# Evaluate the game
for game_data in tqdm(games_data, desc='Evaluating games'):
    board = chess.Board()
    evals = []
    moves = game_data['Moves']
    for idx, move_uci in enumerate(moves):
        # Step 1: Get the engine's best move and evaluation after that move
        info_before_move = engine.analyse(board, chess.engine.Limit(time=0.1))
        best_move = info_before_move['pv'][0]

        # Make a copy of the board to test the engine's best move
        board_best = board.copy()
        board_best.push(best_move)
        eval_after_best_move = evaluate_position(board_best, engine, chess.engine.Limit(time=0.2))

        # Step 2: Make the player's move and evaluate the position
        player_move = chess.Move.from_uci(move_uci)
        board.push(player_move)
        eval_after_player_move = evaluate_position(board, engine, chess.engine.Limit(time=0.2))

        # Determine whose move it was
        player = 'White' if idx % 2 == 0 else 'Black'

        # Step 3: Calculate centipawn loss
        if player == 'White':
            centipawn_loss = eval_after_best_move - eval_after_player_move
        else:
            centipawn_loss = eval_after_player_move - eval_after_best_move

        centipawn_loss = max(0, centipawn_loss)  # Ensure non-negative

        # Store the evaluations and centipawn loss
        evals.append({
            'player': player,
            'move_number': idx + 1,
            'move': move_uci,
            'best_move': best_move.uci(),
            'player_evaluation': eval_after_player_move,
            'best_evaluation': eval_after_best_move,
            'centipawn_loss': centipawn_loss,
        })

    game_data['Evaluation'] = evals

# Now process the evaluations to calculate average centipawn loss per player
for game_data in games_data:
    white_centipawn_losses = []
    black_centipawn_losses = []

    for eval_entry in game_data['Evaluation']:
        if eval_entry['player'] == 'White':
            white_centipawn_losses.append(eval_entry['centipawn_loss'])
        else:
            black_centipawn_losses.append(eval_entry['centipawn_loss'])

    # Calculate average centipawn loss
    if white_centipawn_losses:
        white_avg_cpl = round(sum(white_centipawn_losses) / len(white_centipawn_losses))
    else:
        white_avg_cpl = 0

    if black_centipawn_losses:
        black_avg_cpl = round(sum(black_centipawn_losses) / len(black_centipawn_losses))
    else:
        black_avg_cpl = 0

    print(f"{game_data['White']} vs {game_data['Black']}: White average centipawn loss: {white_avg_cpl}")
    print(f"{game_data['White']} vs {game_data['Black']}: Black average centipawn loss: {black_avg_cpl}")

# Optionally, save the DataFrame to a CSV file
df = pd.DataFrame(games_data)
df.to_csv('combined_games_data.csv', index=False)

# Display the DataFrame
print(df.head())