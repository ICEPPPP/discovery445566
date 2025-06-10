import subprocess
import time

def scan_devices(scan_time=10):
    print("[*] Escaneando dispositivos Bluetooth por", scan_time, "segundos...")
    proc = subprocess.Popen("bluetoothctl", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Inicia o scan
    proc.stdin.write("scan on\n")
    proc.stdin.flush()
    time.sleep(scan_time)
    proc.stdin.write("scan off\n")
    proc.stdin.write("devices\n")
    proc.stdin.flush()

    # Espera a saída
    time.sleep(1)
    output = proc.stdout.read()
    proc.terminate()

    # Filtra dispositivos
    devices = []
    for line in output.splitlines():
        if line.startswith("Device"):
            parts = line.strip().split(" ", 2)
            if len(parts) >= 3:
                mac = parts[1]
                name = parts[2]
                devices.append((mac, name))
    return devices

def choose_device(devices):
    if not devices:
        print("[-] Nenhum dispositivo encontrado.")
        return None
    print("\nDispositivos encontrados:")
    for i, (mac, name) in enumerate(devices):
        print(f"{i + 1}. {name} ({mac})")
    while True:
        try:
            choice = int(input("\nEscolha o número do dispositivo para desconectar: "))
            if 1 <= choice <= len(devices):
                return devices[choice - 1][0]  # Retorna apenas o MAC
        except ValueError:
            pass
        print("Escolha inválida. Tente novamente.")

def disconnect_device(mac):
    print(f"\n[*] Desconectando {mac}...")
    try:
        subprocess.run(f"bluetoothctl disconnect {mac}", shell=True, check=True)
        print("[+] Dispositivo desconectado com sucesso.")
    except subprocess.CalledProcessError:
        print("[-] Falha ao desconectar o dispositivo.")

if __name__ == "__main__":
    devices = scan_devices(scan_time=10)
    selected_mac = choose_device(devices)
    if selected_mac:
        disconnect_device(selected_mac)
