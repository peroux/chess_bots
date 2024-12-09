import chess
import chess.engine
import ast
import random
import os
import sys
from config import resource_path

def load_engine_and_data():
    os.path.join('game/assets/sounds/move.wav')
    # engine = chess.engine.SimpleEngine.popen_uci(resource_path('game/stockfish/17/bin/stockfish'))
    engine = chess.engine.SimpleEngine.popen_uci(resource_path('game\lc0-v0.31.2-windows-gpu-nvidia-cuda\lc0.exe'))
    
    # Load your data
    with open(resource_path('game/data/henrydata.csv'), "r") as dataset:
        dataset.readline()  # Skip the header
        dataset.readline()  # Skip the username
        
        centipawn_loss_dict_line = dataset.readline() # process the centipawn_loss_dict
        centipawn_loss_dict = ast.literal_eval(centipawn_loss_dict_line)
        centipawn_loss_dict = ast.literal_eval(centipawn_loss_dict)
        
        dataset.readline()  # Skip the movecount
        
        acpl_std_error_line = dataset.readline() # process the acpl_std_error
        acpl_std_error = ast.literal_eval(acpl_std_error_line)
        acpl_std_error = ast.literal_eval(acpl_std_error)
        
        best_move_line = dataset.readline() # process the best_move_dict
        best_move_dict = ast.literal_eval(best_move_line)
        best_move_dict = ast.literal_eval(best_move_dict)
    
    return engine, centipawn_loss_dict, acpl_std_error, best_move_dict

def eval_acpl_move(board, engine, depth, num_lines):
    analysed_variations = engine.analyse(
        board, limit=chess.engine.Limit(depth=depth), multipv=num_lines
    )
    
    # Get the best move's evaluation
    best_variation = analysed_variations[0]
    best_score = best_variation["score"].relative.score(mate_score=1000)
    
    moves = []
    cpl = []
    
    for variation in analysed_variations:
        move = variation["pv"][0]
        move_score = variation["score"].relative.score(mate_score=1000)
        
        # Calculate centipawn loss relative to the best move
        centipawn_loss = abs(best_score - move_score)
        
        moves.append(move)
        cpl.append(centipawn_loss)
    
    return moves, cpl

def find_closest_match(move_num, moves, acpl_list, centipawn_loss_dict, acpl_std_error, best_move_dict):
    if move_num in centipawn_loss_dict:
        data_acpl = centipawn_loss_dict[move_num]
        data_std_error = acpl_std_error[move_num]
        best_move_odds = best_move_dict[move_num]
    else:
        print(f"Move number {move_num} not found in data.")
        return moves[len(moves) // 2]
    
    if random.random() < best_move_odds:
        return moves[0]

    lower_bound = float(data_acpl) - float(data_std_error)
    upper_bound = float(data_acpl) + float(data_std_error)
    closest_moves = []

    for move, acpl in zip(moves, acpl_list):
        if lower_bound <= float(acpl) <= upper_bound:
            closest_moves.append(move)
    
    if closest_moves:
        return random.choice(closest_moves)
    else:
        # If no moves within range, select move with ACPL closest to data_acpl
        acpl_diffs = [abs(acpl - data_acpl) for acpl in acpl_list]
        min_diff_index = acpl_diffs.index(min(acpl_diffs))
        return moves[min_diff_index]

# def main():
#     board = chess.Board()
#     move_num = 1  # Start from move number 1
#     user_color = input("Do you want to play as White or Black? (W/B): ").strip().upper()
#     if user_color == 'W':
#         user_turn = True
#     else:
#         user_turn = False

#     while not board.is_game_over():
#         print("\nCurrent board:")
#         print(board)
#         print()

#         if user_turn:
#             # User's turn
#             legal_moves = [move.uci() for move in board.legal_moves]
#             user_move = input("Your move (in UCI format, e.g., e2e4): ").strip()
#             while user_move not in legal_moves:
#                 print("Invalid move. Please enter a legal move in UCI format.")
#                 user_move = input("Your move: ").strip()
#             board.push_uci(user_move)
#         else:
#             # Bot's turn
#             print("Bot is thinking...")
#             moves, acpl_list = eval_acpl_move(board, engine, depth=20, num_lines=10)
#             bot_move = find_closest_match(move_num, moves, acpl_list, centipawn_loss_dict, acpl_std_error)
#             board.push(bot_move)
#             print(f"Bot plays: {bot_move}")

#             move_num += 1
        
#         user_turn = not user_turn

#     print("\nGame over.")
#     print(board.result())

# if __name__ == "__main__":
#     main()
#     engine.quit()