import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 5000))
s.listen(5)

print("[*] Estou ouvindo na porta 5000", flush = True)
conn, addr = s.accept()
print(f"[*] Conectado com {addr}")

while True:
    palavra = conn.recv(1024).decode()

    if not palavra:
        break

    print(f"O cliente disse: {palavra}")

    if palavra.lower() == 'sair':
        print("[*] Encerrando conexão")
        break

    conn.send(palavra.encode())

conn.close()