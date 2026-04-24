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
            self.socket.connect((self.args.target, self.args.port))
            
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
            print('[!] Conexao recusada')
        except Exception as e:
            print(f'[!] Erro: {e}')
        finally:
            self.socket.close()

    def listen(self):
        try:
            self.socket.bind((self.args.target, self.args.port))
            self.socket.listen(5)
            
            while True:
                client_socket, addr = self.socket.accept()
                client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except Exception as e:
            print(f'[!] Erro no servidor: {e}')
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
                    else:
                        break

                with open(self.args.upload, 'wb') as f:
                    f.write(file_buffer)
                message = f'Arquivo salvo {self.args.upload}'
                client_socket.send(message.encode())

            elif self.args.command:
                cmd_buffer = b''
                while True:
                    try:
                        # Envia prompt
                        client_socket.send(b'BHP: #> ')
                        
                        # Recebe comando até encontrar \n
                        while True:
                            data = client_socket.recv(64)
                            if not data:
                                return
                            cmd_buffer += data
                            if b'\n' in cmd_buffer:
                                break
                        
                        # Executa comando
                        cmd_str = cmd_buffer.decode('utf-8', errors='ignore').strip()
                        response = execute(cmd_str)
                        
                        # Envia resposta (mesmo se vazia)
                        if response:
                            client_socket.send(response.encode('utf-8', errors='ignore'))
                        
                        # Limpa buffer de comando
                        cmd_buffer = b''
                        
                    except Exception as e:
                        break
        except Exception as e:
            pass
        finally:
            client_socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Black Hat Python - Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Exemplos:
            netcat.py -t 127.0.0.1 -p 5555 -l -c # Servidor shell
            netcat.py -t 127.0.0.1 -p 5555 -l -e="whoami" # Servidor executa comando
            netcat.py -t 127.0.0.1 -p 5555 # Cliente conecta
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='Shell interativo')
    parser.add_argument('-e', '--execute', help='Executar comando')
    parser.add_argument('-l', '--listen', action='store_true', help='Modo servidor')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Porta (padrao: 5555)')
    parser.add_argument('-t', '--target', default='127.0.0.1', help='IP alvo (padrao: 127.0.0.1)')
    parser.add_argument('-u', '--upload', help='Receber arquivo')
    args = parser.parse_args()
    
    if args.listen:
        buffer = b''
    else:
        buffer = sys.stdin.read().encode() if not sys.stdin.isatty() else b''

    nc = NetCat(args, buffer)
    nc.run()