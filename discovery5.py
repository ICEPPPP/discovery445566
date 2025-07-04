import subprocess
import time

def run_command(cmd):
    """Executa um comando e retorna a saída em texto."""
    return subprocess.check_output(cmd, shell=True, text=True)

def scan_devices(timeout=300):
    print("[*] Iniciando escaneamento Bluetooth...")
    
    # Inicia scan
    subprocess.Popen("bluetoothctl scan on", shell=True)
    time.sleep(timeout)
    subprocess.run("bluetoothctl scan off", shell=True)

    # Pega dispositivos detectados
    output = run_command("bluetoothctl devices")
    devices = []
    for line in output.splitlines():
        if line.startswith("Device"):
            parts = line.split(" ", 2)
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
