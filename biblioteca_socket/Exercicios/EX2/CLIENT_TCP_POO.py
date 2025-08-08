import socket

class ClientTCP:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

    def connect(self):
            print(f"[*] Connecting to {self.ip}:{self.port}...")
            self.socket.connect((self.ip, self.port))
            print("[+] Connected successfully.")

    def loop_communication(self):
        while True:
            message = input("Input something: ")

            self.socket.send(message.encode())

            if message.lower() == 'exit':
                break

            response = self.socket.recv(1024).decode()
            print(f"Echo of Server: {response}")

    def exit(self):
        self.socket.close()
        print("[*] Connection closed.")

if __name__ == '__main__':
    cliente = ClientTCP('127.0.0.1', 4444)  # ou o IP do servidor real
    cliente.connect()
    cliente.loop_communication()
    cliente.exit()