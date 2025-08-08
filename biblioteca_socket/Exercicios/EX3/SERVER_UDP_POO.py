import socket

class ServerUDP:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.socket.bind((ip, port))

    def start(self):
        while True:
            data, addr = self.socket.recvfrom(4096)
            message = data.decode()
            print(f"[{addr}] {message}")
            self.socket.sendto(b"Message received", addr)

    def exit(self):
        self.socket.close()
        print("[+] Closing the server")

if __name__ == '__main__':
    server = ServerUDP('0.0.0.0', 4444)
    try:
        server.start()
    except KeyboardInterrupt:
        server.exit()