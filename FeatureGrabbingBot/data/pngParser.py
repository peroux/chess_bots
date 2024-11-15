import os

# Ensure there's a directory to store the split PGN files
file_path = 'C:\\Users\\Peter\\Documents\\GitHub\\chess-engine\\data\\peterchero.pgn'
output_dir = 'C:\\Users\\Peter\\Documents\\GitHub\\chess-engine\\data\\pgn'
os.makedirs(output_dir, exist_ok=True)

# Load the entire file into memory
with open(file_path, 'r') as file:
    content = file.read()

# Split the content by double newlines which generally separate games in PGN files
games = content.strip().split('\n\n\n')

# Iterate over each game and save it as a separate .pgn file
for idx, game in enumerate(games, start=1):
    game_content = game.strip()
    if game_content:  # Avoid any empty segments
        file_path = os.path.join(output_dir, f'game_{idx}.pgn')
        with open(file_path, 'w') as game_file:
            game_file.write(game_content)
            print(f'Saved {file_path}')