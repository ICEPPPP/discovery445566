import subprocess
import time

def run_command(cmd):
    """Executa um comando e retorna a saída em texto."""
    return subprocess.check_output(cmd, shell=True, text=True)

def scan_devices(timeout=10):
    print("[*] Iniciando escaneamento Bluetooth...")

    # Usa o bluetoothctl em modo interativo para controle total
    process = subprocess.Popen(["bluetoothctl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Liga o scan
    process.stdin.write("scan on\n")
    process.stdin.flush()
    print(f"[*] Escaneando por {timeout} segundos...")
    time.sleep(timeout)

    # Para o scan
    process.stdin.write("scan off\n")
    process.stdin.write("devices\n")
    process.stdin.flush()
    time.sleep(1)

    # Captura a saída
    output = process.stdout.read()
    process.stdin.write("exit\n")
    process.stdin.flush()
    process.terminate()

    # Parse da saída
    devices = []
    for line in output.splitlines():
        if line.startswith("Device"):
            parts = line.strip().split(" ", 2)
            if len(parts) == 3:
                mac, name = parts[1], parts[2]
                devices.append((mac, name))
    return devices

def choose_device(devices):
    if not devices:
        print("[-] Nenhum dispositivo encontrado.")
        return None
    print("\nDispositivos encontrados:")
    for i, (mac, name) in enumerate(devices):
        print(f"{i+1}. {name} ({mac})")
    while True:
        try:
            escolha = int(input("\nEscolha um número para desconectar: "))
            if 1 <= escolha <= len(devices):
                return devices[escolha - 1][0]
        except ValueError:
            pass
        print("Escolha inválida. Tente novamente.")

def disconnect_device(mac):
    print(f"[*] Desconectando {mac}...")
    try:
        subprocess.run(f"bluetoothctl disconnect {mac}", shell=True, check=True)
        print("[+] Dispositivo desconectado com sucesso.")
    except subprocess.CalledProcessError:
        print("[-] Falha ao desconectar.")

if __name__ == "__main__":
    devices = scan_devices(timeout=10)
    selected = choose_device(devices)
    if selected:
        disconnect_device(selected)
