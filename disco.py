import subprocess
import time
import threading

# Dicionário para armazenar dispositivos únicos
dispositivos = {}

def read_output(process):
    """Lê a saída do bluetoothctl linha a linha e coleta dispositivos encontrados."""
    while True:
        line = process.stdout.readline()
        if not line:
            break
        line = line.strip()
        if line:
            print(f"[bluetoothctl] {line}")  # Mostra toda saída em tempo real
        if line.startswith("Device"):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                mac, name = parts[1], parts[2]
                if mac not in dispositivos:
                    dispositivos[mac] = name
                    print(f"[✓] Novo dispositivo: {name} ({mac})")

def scan_live(timeout=300):
    """Inicia bluetoothctl com scan ativo por tempo determinado."""
    print(f"[*] Iniciando escaneamento Bluetooth por {timeout//60} minutos...")

    # Executa bluetoothctl com saída desbufferizada
    process = subprocess.Popen(
        ["stdbuf", "-oL", "bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Thread para ler saída em paralelo
    thread = threading.Thread(target=read_output, args=(process,), daemon=True)
    thread.start()

    # Liga o scan
    process.stdin.write("scan on\n")
    process.stdin.flush()

    # Espera o tempo de scan
    time.sleep(timeout)

    # Desliga o scan e sai
    process.stdin.write("scan off\n")
    process.stdin.write("exit\n")
    process.stdin.flush()

    thread.join(timeout=2)
    process.terminate()

def choose_device():
    """Exibe dispositivos e permite ao usuário escolher um para desconectar."""
    if not dispositivos:
        print("[-] Nenhum dispositivo encontrado.")
        return None

    print("\n[✓] Dispositivos encontrados:")
    lista = list(dispositivos.items())
    for i, (mac, name) in enumerate(lista):
        print(f"{i+1}. {name} ({mac})")

    while True:
        escolha = input("\nDigite o número do dispositivo para desconectar (ou 'sair'): ")
        if escolha.lower() == "sair":
            return None
        if escolha.isdigit():
            num = int(escolha)
            if 1 <= num <= len(lista):
                return lista[num - 1][0]
        print("Entrada inválida. Tente novamente.")

def disconnect_device(mac):
    """Desconecta o dispositivo pelo MAC."""
    print(f"[*] Tentando desconectar {mac}...")
    try:
        subprocess.run(f"bluetoothctl disconnect {mac}", shell=True, check=True)
        print("[+] Dispositivo desconectado com sucesso.")
    except subprocess.CalledProcessError:
        print("[-] Falha ao desconectar.")

if __name__ == "__main__":
    scan_live(timeout=300)  # 5 minutos
    selected_mac = choose_device()
    if selected_mac:
        disconnect_device(selected_mac)
    else:
        print("[!] Nenhum dispositivo selecionado. Encerrando.")
