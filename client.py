import socket
import threading
import sys


class GameClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 9090):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = False

    def connect(self) -> bool:
        """Conecta o socket ao servidor remoto."""
        try:
            self.socket.connect((self.host, self.port))
            self.is_running = True
            print("Conectado ao servidor. Digite os comandos ou apostas.")
            return True
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")
            return False

    def listen_server(self):
        """Thread responsável por receber mensagens do servidor."""
        while self.is_running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    print("\nServidor desconectou")
                    self.is_running = False
                    break

                mensagem = data.decode("utf-8", errors="replace")
                print(mensagem, end="", flush=True)
            except Exception:
                break
        self.close()

    def input_handler(self):
        """Thread responsável por capturar entrada do teclado e enviar."""
        while self.is_running:
            try:
                user_input = sys.stdin.readline()
                if not user_input:
                    self.socket.shutdown(socket.SHUT_WR)
                    self.is_running = False
                    break

                self.socket.sendall(user_input.encode("utf-8"))
            except Exception:
                break
        self.close()
              

    def start(self):
        """Inicializa as threads de escuta e envio."""
        if not self.connect():
            return

        t_input = threading.Thread(target=self.input_handler, daemon=True)
        t_listen = threading.Thread(target=self.listen_server, daemon=True)

        t_input.start()
        t_listen.start()

        try:
            while self.is_running:
                t_listen.join(timeout=0.5)
        except KeyboardInterrupt:
            pass
        finally:
            self.close()

    def close(self):
        """Fecha a conexão do socket com segurança."""
        self.is_running = False
        try:
            self.socket.close()
        except Exception:
            pass


if __name__ == "__main__":
    client = GameClient(host="127.0.0.1", port=9090)
    client.start()