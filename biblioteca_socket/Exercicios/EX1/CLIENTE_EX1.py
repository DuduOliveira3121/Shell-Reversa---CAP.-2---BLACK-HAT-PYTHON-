import socket

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect(('127.0.0.1', 5000))

while True:
    mensagem = input("Digite algo: ")
 
    c.send(mensagem.encode())

    if mensagem.lower() == 'sair':
        break

    resposta = c.recv(1024).decode()
    print(f"Eco do servidor: {resposta}")
 
c.close()