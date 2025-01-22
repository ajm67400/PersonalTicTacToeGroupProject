import socket

class Client:
    def __init__(self, port=6555):
        self.listening = True
        self._join_game("localhost", port)
        self._start_listening()

    def _join_game(self, host, port):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            print(f"Joined {host}:{port}")
        except Exception as e:
            print(f"Failed to connect. Is the server running?")

    def _start_listening(self):
        try:
            print(f"You are playing as 'O'")
            print(f"Your opponent is 'X'")
            print(f"Waiting for first opponent move...")
            while self.listening:
                self._handle_server_messages()
        except Exception as e:
            print(f"Error occurred during handling of server messages: {e}")

    def _handle_server_messages(self):
        msg = self.client.recv(1028).decode("utf-8")
        if "game_over:" in msg:
            winner = msg.split("game_over:")[1].strip()
            print(f"Game Over! ", end='')
            if winner == "None":
                print(f"It's a tie!")
            else:
                print(f"{winner} wins!")
            self.listening = False
            return
        if "board:" in msg:
            board_string = msg.split("board:")[1].split("move")[0]
            print(board_string)
        if "move_requested" in msg:
            # no need to validate. if move invalid, server requests move again
            move = input("Choose a square to place your move: ").strip()
            self._send_server_msg(f"{move}")  
            print(f"Waiting for opponent 'X's move...")

    def _send_server_msg(self, msg: str):
        self.client.sendall(msg.encode("utf-8"))


game = Client()
