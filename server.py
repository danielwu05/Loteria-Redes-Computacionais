from serverObj import Server
import threading
import sys


def main():

    host = "localhost"
    port = 9090

    s = Server(host, port)
    s.start()

    t1 = threading.Thread(target=s.process_input, daemon=True)
    t2 = threading.Thread(target=s.send_results, daemon=True)

    t1.start()
    t2.start()

    try:
        while t1.is_alive() and t2.is_alive():
            t1.join(0.5)
    except KeyboardInterrupt:
        print("\n shutting down server")
    finally:
        s.close_server()
        sys.exit(0)


if __name__ == "__main__":
    main()
