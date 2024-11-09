import pygame
import chess
import chess.engine
import sys
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 900  # Size of the chessboard window
DIMENSION = 8  # Chessboard is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # For animations
IMAGES = {}

# Load images
def load_images():
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(os.path.join('FeatureGrabbingBot', 'images', piece + '.png')), (SQ_SIZE, SQ_SIZE)
        )


# Main driver for the code
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()
    screen.fill(pygame.Color('white'))
    gs = chess.Board()
    load_images()
    running = True
    sq_selected = ()  # No square is selected initially
    player_clicks = []  # Keep track of player clicks
    game_over = False

    while running:
        human_turn = gs.turn == chess.WHITE

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            # Mouse handler
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = pygame.mouse.get_pos()  # (x, y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    sq = chess.square(col, 7 - row)
                    if sq_selected == sq:
                        # Deselect the square
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = sq
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        move = chess.Move(player_clicks[0], player_clicks[1])
                        if move in gs.legal_moves:
                            gs.push(move)
                            sq_selected = ()
                            player_clicks = []
                            # AI move
                            if gs.is_game_over():
                                game_over = True
                            else:
                                move = get_ai_move(gs)
                                gs.push(move)
                                if gs.is_game_over():
                                    game_over = True
                        else:
                            player_clicks = [sq_selected]

        draw_game_state(screen, gs)
        if game_over:
            draw_text(screen, 'Game Over')
        clock.tick(MAX_FPS)
        pygame.display.flip()

# Draw the current game state
def draw_game_state(screen, gs):
    draw_board(screen)  # Draw squares on the board
    draw_pieces(screen, gs)  # Draw pieces on top of those squares

# Draw the squares on the board
def draw_board(screen):
    colors = [pygame.Color(235, 236, 208), pygame.Color(119, 154, 88)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )

def get_image_key(piece):
    color = 'w' if piece.color == chess.WHITE else 'b'
    symbol = piece.symbol().upper()
    return color + symbol


# Draw the pieces on the board
def draw_pieces(screen, gs):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            square = chess.square(c, 7 - r)
            piece = gs.piece_at(square)
            if piece:
                key = get_image_key(piece)
                piece_image = IMAGES[key]
                screen.blit(piece_image, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Get AI move (random legal move)
def get_ai_move(gs):
    move = chess.engine.SimpleEngine.popen_uci('stockfish')
    result = move.play(gs, chess.engine.Limit(time=0.1))
    move.quit()
    return result.move

# Display text on the screen
def draw_text(screen, text):
    font = pygame.font.SysFont('Helvetica', 32, True, False)
    text_object = font.render(text, False, pygame.Color('Gray'))
    text_location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - text_object.get_width() / 2,
        HEIGHT / 2 - text_object.get_height() / 2
    )
    screen.blit(text_object, text_location)

if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()
