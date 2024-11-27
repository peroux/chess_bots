import chess  # Import python-chess library
import pygame
import sys
import os

from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound

class Board:

    def __init__(self):
        self.chess_board = chess.Board()  # Initialize the python-chess board
        self.last_move = None
        self._create_squares()
        self._load_pieces()

    def _create_squares(self):
        self.squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]

    def _load_pieces(self):
        # Load pieces from python-chess board into your board representation
        for square in chess.SQUARES:
            piece = self.chess_board.piece_at(square)
            if piece:
                row, col = self._chess_square_to_coords(square)
                self.squares[row][col].piece = self._create_piece(piece)

    def _create_piece(self, piece):
        color = 'white' if piece.color == chess.WHITE else 'black'
        piece_type = piece.piece_type

        if piece_type == chess.PAWN:
            return Pawn(color)
        elif piece_type == chess.ROOK:
            return Rook(color)
        elif piece_type == chess.KNIGHT:
            return Knight(color)
        elif piece_type == chess.BISHOP:
            return Bishop(color)
        elif piece_type == chess.QUEEN:
            return Queen(color)
        elif piece_type == chess.KING:
            return King(color)

    def _chess_square_to_coords(self, square):
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)
        return row, col

    def _coords_to_chess_square(self, row, col):
        return chess.square(col, 7 - row)

    def move(self, piece, move):
        # Convert your move to a python-chess move
        from_square = self._coords_to_chess_square(move.initial.row, move.initial.col)
        to_square = self._coords_to_chess_square(move.final.row, move.final.col)
        promotion = None

        # Handle pawn promotion (promote to queen by default)
        if isinstance(piece, Pawn) and (move.final.row == 0 or move.final.row == 7):
            promotion = chess.QUEEN

        chess_move = chess.Move(from_square, to_square, promotion=promotion)

        # Validate and push the move
        if chess_move in self.chess_board.legal_moves:
            self.chess_board.push(chess_move)
            self._update_board_state()
            # Play move sound if needed
            if move.final.piece:
                sound = Sound(os.path.join('game/assets/sounds/capture.wav'))
                sound.play()
            self.last_move = move
            return True
        else:
            # Invalid move
            return False

    def _update_board_state(self):
        # Update your board representation based on the python-chess board
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col].piece = None  # Clear the square

        for square in chess.SQUARES:
            piece = self.chess_board.piece_at(square)
            if piece:
                row, col = self._chess_square_to_coords(square)
                self.squares[row][col].piece = self._create_piece(piece)

    def valid_move(self, piece, move):
        # Convert your move to a python-chess move
        from_square = self._coords_to_chess_square(move.initial.row, move.initial.col)
        to_square = self._coords_to_chess_square(move.final.row, move.final.col)
        promotion = None

        # Handle pawn promotion (promote to queen by default)
        if isinstance(piece, Pawn) and (move.final.row == 0 or move.final.row == 7):
            promotion = chess.QUEEN

        chess_move = chess.Move(from_square, to_square, promotion=promotion)
        return chess_move in self.chess_board.legal_moves

    def is_in_check(self, color):
        # Use python-chess to determine if the player is in check
        if color == 'white':
            return self.chess_board.is_check() if self.chess_board.turn == chess.WHITE else False
        else:
            return self.chess_board.is_check() if self.chess_board.turn == chess.BLACK else False

    def calc_moves(self, piece, row, col, bool=True):
        # Generate legal moves for highlighting purposes
        piece.moves = []  # Clear existing moves
        from_square = self._coords_to_chess_square(row, col)

        for chess_move in self.chess_board.legal_moves:
            if chess_move.from_square == from_square:
                to_row, to_col = self._chess_square_to_coords(chess_move.to_square)
                initial = Square(row, col)
                final_piece = self.squares[to_row][to_col].piece
                final = Square(to_row, to_col, final_piece)
                move = Move(initial, final)
                piece.add_move(move)
