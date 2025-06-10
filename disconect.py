import pexpect
import time

def scan_devices(timeout=10):
    print("[*] Iniciando bluetoothctl...")
    bt = pexpect.spawn("bluetoothctl", encoding='utf-8', timeout=timeout)
    bt.expect("#")  # Espera o prompt inicial
    bt.sendline("scan on")

    print(f"[*] Escaneando dispositivos por {timeout} segundos...\n")
    time.sleep(timeout)

    bt.sendline("scan off")
    bt.sendline("devices")
    time.sleep(1)

    bt.expect("#")
    output = bt.before
    bt.sendline("exit")

    # Parseando dispositivos
    devices = []
    for line in output.splitlines():
        if line.startswith("Device"):
            parts = line.strip().split(" ", 2)
            if len(parts) == 3:
                mac = parts[1]
                name = parts[2]
                devices.append((mac, name))

    return devices

def choose_device(devices):
    if not devices:
        print("[-] Nenhum dispositivo encontrado.")
        return None
    print("Dispositivos encontrados:")
    for i, (mac, name) in enumerate(devices):
        print(f"{i+1}. {name} ({mac})")
    while True:
        try:
            choice = int(input("\nEscolha um número para desconectar: "))
            if 1 <= choice <= len(devices):
                return devices[choice - 1][0]
        except ValueError:
            pass
        print("Entrada inválida. Tente novamente.")

def disconnect_device(mac):
    print(f"\n[*] Tentando desconectar {mac}...")
    try:
        result = pexpect.run(f"bluetoothctl disconnect {mac}", encoding='utf-8')
        print(result)
    except Exception as e:
        print("Erro ao desconectar:", e)

if __name__ == "__main__":
    devices = scan_devices(timeout=10)
    selected_mac = choose_device(devices)
    if selected_mac:
        disconnect_device(selected_mac)
