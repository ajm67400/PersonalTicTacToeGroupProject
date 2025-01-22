import socket


class Server:
    def __init__(self):
        self.server_turn = True
        self.game_over = False
        self.winner = ''
        self.board_string = ""
        self.board = [' ' for _ in range(9)]
        self._update_board()
        self._host_game(port=6555)


    def _host_game(self, port):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            print(f"Waiting for guest to join..")
            self.client_socket, client_addr = self.server_socket.accept()


            print(f"Guest joined on port {client_addr[1]}")
            print(f"You are playing as X")
            self._game_loop()
        except Exception as e:
            print(f"Error in game: {e}")


    def _game_loop(self):
        # when game first starts show starting board
        self._show_board(is_client=True)


        while not self.game_over:
            self._move(not self.server_turn)


        # game is over
        # show ending board for both players
        self._show_board()
        self._show_board(is_client=True)
        print(f"Game Over! ", end='')
        if self.winner is not None:
            print(f"{self.winner} wins!")
        else:
            print(f"It's a tie!")


        # end the connection
        self._send_client_msg(f"game_over:{self.winner}")
        self.client_socket.close()
        self.server_socket.close()


    def _move(self, is_client: bool):
        self._show_board(is_client=is_client)


        move_input = self._get_move_input(is_client=is_client)
        move_index = int(move_input)
        self.board[move_index] = 'O' if is_client else 'X'
        self._update_board()


        self._check_win(is_client=is_client)
        self.server_turn = not self.server_turn


    def _get_move_input(self, is_client=False):
        avail_moves = self._get_available_moves()
        move = None
        if is_client:
            move = None
            while move is None:
                self._send_client_msg(f"move_requested")
                print(f"Waiting for opponent 'O's move...")
                move = self.client_socket.recv(1).decode("utf-8")
                if move not in avail_moves:
                    print(f"'{move}' is not a valid option. Valid moves: {avail_moves}")
                    move = None
        else:
            while move is None:
                move = input("Choose a square to place your move: ").strip()
                if move not in avail_moves:
                    print(f"'{move}' is not a valid option. Valid moves: {avail_moves}")
                    move = None
        return move


    def _show_board(self, is_client=False):
        if is_client:
            self._send_client_msg(f"board:{self.board_string}")
        else:
            print(self.board_string)


    def _update_board(self):
        self.board_string = ""
        for i in range(3):
            row = []
            for j in range(3):
                index = i * 3 + j
                if self.board[index] == ' ':
                    row.append(str(index))
                else:
                    row.append(self.board[index])
            self.board_string += " | ".join(row) + "\n"
            if i < 2:
                self.board_string += "---------\n"
        return self.board_string


    def _get_available_moves(self):
        return [str(idx) for idx, sq in enumerate(self.board) if sq == ' ']


    def _check_win(self, is_client: bool):
        char = 'O' if is_client else 'X'


        won = all(s == char for s in (self.board[0], self.board[3], self.board[6])) or \
            all(s == char for s in (self.board[1], self.board[4], self.board[7])) or\
            all(s == char for s in (self.board[2], self.board[5], self.board[8])) or\
            all(s == char for s in (self.board[0], self.board[1], self.board[2])) or\
            all(s == char for s in (self.board[3], self.board[4], self.board[5])) or\
            all(s == char for s in (self.board[6], self.board[7], self.board[8])) or\
            all(s == char for s in (self.board[0], self.board[4], self.board[8])) or\
            all(s == char for s in (self.board[2], self.board[4], self.board[6]))


        if won:
            self.game_over = True
            self.winner = char
        elif len(self._get_available_moves()) == 0:
            self.game_over = True
            self.winner = None # it's a tie, no winner


    def _send_client_msg(self, msg: str):
        self.client_socket.send(msg.encode("utf-8"))








game = Server()