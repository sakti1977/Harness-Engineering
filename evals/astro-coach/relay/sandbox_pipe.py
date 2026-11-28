# Runs inside the sandbox: 127.0.0.1:<port> <-> the relay's Unix socket. Usage: sandbox_pipe.py <socket> <port>
import socket, sys, threading
UNIX, PORT = sys.argv[1], int(sys.argv[2])

def pipe(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except OSError:
        pass
    finally:
        try:
            b.shutdown(socket.SHUT_WR)
        except OSError:
            pass

def handle(c):
    u = socket.socket(socket.AF_UNIX)
    u.connect(UNIX)
    t = threading.Thread(target=pipe, args=(u, c), daemon=True)
    t.start()
    pipe(c, u)
    t.join()
    c.close(); u.close()

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", PORT))
srv.listen(64)
while True:
    c, _ = srv.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
