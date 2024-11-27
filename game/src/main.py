import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move
from piece import *
import chess
from move_calculator import eval_acpl_move, find_closest_match, load_engine_and_data

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.board = self.game.board
        self.engine, self.centipawn_loss_dict, self.acpl_std_error, self.best_move_dict = load_engine_and_data()



    def mainloop(self):
        # Choose player's color
        user_color = input("Do you want to play as White or Black? (W/B): ").strip().upper()
        if user_color == 'W':
            player_color = 'white'
            bot_color = 'black'
        else:
            player_color = 'black'
            bot_color = 'white'

        screen = self.screen
        game = self.game
        board = self.board
        dragger = self.game.dragger
        move_num = 1  # Start move numbering

        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                # Handle player input only if it's their turn
                if (board.chess_board.turn == chess.WHITE and player_color == 'white') or \
                (board.chess_board.turn == chess.BLACK and player_color == 'black'):

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)
                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        # Convert to chess square
                        square = board._coords_to_chess_square(clicked_row, clicked_col)
                        piece = board.chess_board.piece_at(square)

                        if piece and piece.color == (chess.WHITE if player_color == 'white' else chess.BLACK):
                            # Get the piece from your board representation
                            piece_obj = board.squares[clicked_row][clicked_col].piece
                            # Calculate moves for highlighting
                            board.calc_moves(piece_obj, clicked_row, clicked_col)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece_obj)

                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE

                        game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)

                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE

                            # create move using chess library coordinates
                            from_square = board._coords_to_chess_square(dragger.initial_row, dragger.initial_col)
                            to_square = board._coords_to_chess_square(released_row, released_col)
                            promotion = None

                            # Check for pawn promotion
                            piece = board.squares[dragger.initial_row][dragger.initial_col].piece
                            if isinstance(piece, Pawn) and (released_row == 0 or released_row == 7):
                                # Get the promotion choice from the player
                                promotion_choice = Game.get_promotion_choice(screen, game, event.pos)
                                promotion_map = {
                                    'queen': chess.QUEEN,
                                    'rook': chess.ROOK,
                                    'bishop': chess.BISHOP,
                                    'knight': chess.KNIGHT
                                }
                                promotion = promotion_map[promotion_choice]

                            # Create the move
                            chess_move = chess.Move(from_square, to_square, promotion=promotion)

                            # Valid move?
                            if chess_move in board.chess_board.legal_moves:
                                # Perform the move
                                board.chess_board.push(chess_move)
                                # Update the board state
                                board._update_board_state()
                                # Play sound
                                if board.chess_board.is_capture(chess_move):
                                    game.play_sound(True)
                                else:
                                    game.play_sound(False)
                                move_num += 1
                            else:
                                # Invalid move, reset piece position or show an error
                                pass

                        dragger.undrag_piece()

                    elif event.type == pygame.KEYDOWN:
                        # changing themes
                        if event.key == pygame.K_t:
                            game.change_theme()

                        # reset the game
                        if event.key == pygame.K_r:
                            game.reset()
                            board.chess_board.reset()
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger

            # Draw the game state
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            pygame.display.update()

            # Check for game over
            if board.chess_board.is_game_over():
                print("Game over.")
                print("Result: ", board.chess_board.result())
                running = False
                continue

            # Bot's turn
            if (board.chess_board.turn == chess.WHITE and bot_color == 'white') or \
            (board.chess_board.turn == chess.BLACK and bot_color == 'black'):
                print("Bot is thinking...")
                moves, acpl_list = eval_acpl_move(board.chess_board, self.engine, depth=13, num_lines=10)
                bot_move = find_closest_match(move_num, moves, acpl_list, self.centipawn_loss_dict, self.acpl_std_error, self.best_move_dict)
                board.chess_board.push(bot_move)
                board._update_board_state()
                print(f"Bot plays: {bot_move}")
                # Play sound
                if board.chess_board.is_capture(bot_move):
                    game.play_sound(True)
                else:
                    game.play_sound(False)
                move_num += 1

        # When the loop ends, quit the engine
        self.engine.quit()
        pygame.quit()
        sys.exit()


main = Main()
main.mainloop()