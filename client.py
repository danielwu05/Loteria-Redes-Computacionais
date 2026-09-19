from clientObj import Client
import sys

host = "localhost"
port = 9090


def main():
    c = Client(host, port)
    c.start()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except Exception as e:
        print(f"Erro inesperado no cliente: {e}")
        sys.exit(1)
    
