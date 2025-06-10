import subprocess
import time
import threading

dispositivos = {}

def read_output(process):
    while True:
        line = process.stdout.readline()
        if not line:
            break
        line = line.strip()
        if line.startswith("Device"):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                mac, name = parts[1], parts[2]
                if mac not in dispositivos:
                    dispositivos[mac] = name
                    print(f"[Novo dispositivo encontrado] {name} ({mac})")

def scan_live(timeout=300):
    process = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    thread = threading.Thread(target=read_output, args=(process,), daemon=True)
    thread.start()

    process.stdin.write("scan on\n")
    process.stdin.flush()

    print(f"Escaneando por {timeout//60} minutos ({timeout} segundos)...")
    time.sleep(timeout)

    process.stdin.write("scan off\n")
    process.stdin.flush()

    time.sleep(1)  # Dá um tempinho pra saída terminar

    process.stdin.write("exit\n")
    process.stdin.flush()

    thread.join(timeout=2)
    process.terminate()

def choose_device():
    if not dispositivos:
        print("[-] Nenhum dispositivo encontrado.")
        return None

    print("\nDispositivos encontrados:")
    lista = list(dispositivos.items())
    for i, (mac, name) in enumerate(lista):
        print(f"{i+1}. {name} ({mac})")

    while True:
        escolha = input("\nEscolha um número para desconectar (ou 'sair' para sair): ")
        if escolha.lower() == "sair":
            return None
        if escolha.isdigit():
            num = int(escolha)
            if 1 <= num <= len(lista):
                return lista[num - 1][0]
        print("Escolha inválida. Tente novamente.")

def disconnect_device(mac):
    print(f"[*] Tentando desconectar {mac}...")
    try:
        subprocess.run(f"bluetoothctl disconnect {mac}", shell=True, check=True)
        print("[+] Dispositivo desconectado com sucesso.")
    except subprocess.CalledProcessError:
        print("[-] Falha ao desconectar.")

if __name__ == "__main__":
    scan_live(timeout=300)  # 5 minutos
    selected = choose_device()
    if selected:
        disconnect_device(selected)
    else:
        print("Saindo sem desconectar nenhum dispositivo.")
