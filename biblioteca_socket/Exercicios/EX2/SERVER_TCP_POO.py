import socket

class ServerTCP:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.conn = None
        self.addr = None

    def connect(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)

        print(f"[*] Listening on port {self.port}", flush = True)
        self.conn, self.addr = self.socket.accept()
        print(f"[*] Connected with {self.addr}")

    def loop_communication(self):
        while True:
            word = self.conn.recv(1024).decode()

            if not word:
                break

            if word.lower() == 'exit':
                print(f"[*] Disconnecting")
                break

            self.conn.send(word.encode())

    def exit(self):
        if self.conn:
            self.conn.close()
            self.socket.close()
        print("[*] Connection closed.")

if __name__ == '__main__':
    servidor = ServerTCP('0.0.0.0', 4444)
    servidor.connect()
    servidor.loop_communication()
    servidor.exit()