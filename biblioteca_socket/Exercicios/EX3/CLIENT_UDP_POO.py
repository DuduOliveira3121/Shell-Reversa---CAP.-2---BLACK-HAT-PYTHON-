import socket

class ClientUDP:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port

    def start(self):
        while True:
            message = input(">>> ")
            if message.lower() == 'exit':
                break

            self.socket.sendto(message.encode(), (self.ip, self.port))
            data, addr = self.socket.recvfrom(4096)
            print(f"[{addr}] {data.decode()}")
    
    def exit(self):
        self.socket.close()
        print("[+] Client closed")

if __name__ == "__main__":
    client = ClientUDP('127.0.0.1', 4444)
    try:
        client.start()
    except KeyboardInterrupt:
        client.exit()