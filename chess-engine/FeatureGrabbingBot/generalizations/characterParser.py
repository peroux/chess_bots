import os
import chess.pgn
import pandas as pd

directory_path = "C:\\Users\\Peter\\Documents\\GitHub\\chess-engine\\FeatureGrabbingBot\\data\\pgn"

# Initialize an empty list to hold all the game data
games_data = []

for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    if os.path.isfile(file_path):  # Ensure it's a file and not a subdirectory
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            # Use chess.pgn to parse the PGN file
            while True:
                game = chess.pgn.read_game(f)
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
                    'Opening': headers.get('Opening', ''),
                    'Termination': headers.get('Termination', ''),
                    # Add other headers as needed
                }
                # Optionally, add the moves as a string
                # moves = game.mainline_moves()
                # san_moves = [game.board().san(move) for move in moves]
                # game_data['Moves'] = ' '.join(san_moves)
                # Append the game data to the list
                games_data.append(game_data)

# Now you have a list of dictionaries with game data
# You can process this data as needed

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(games_data)

# Display the DataFrame
print(df.head())

# Optionally, save the DataFrame to a CSV file
df.to_csv('games_data.csv', index=False)
