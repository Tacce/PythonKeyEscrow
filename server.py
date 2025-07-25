import socket
import threading
import json
from secret_sharing import reconstruct_secret

# Parametri server
HOST = 'localhost'
PORT = 5000
THRESHOLD = 3  # Numero minimo di share per ricostruire il segreto

# Lista condivisa delle share ricevute
received_shares = []
lock = threading.Lock()

# Segreto da ricostruire (inizialmente vuoto)
secret = None

def handle_client(conn, addr):
    print(f"[+] Connessione da {addr}")
    try:
        data = conn.recv(1024).decode()
        share = json.loads(data)

        with lock:
            received_shares.append((share["x"], share["y"]))
            print(f"[+] Share ricevuta da {addr}: {share}")
            print(f"[~] Share totali ricevute: {len(received_shares)}")

            if len(received_shares) == THRESHOLD:
                print("[*] Soglia raggiunta. Ricostruzione del segreto...")
                secret = reconstruct_secret(received_shares[:THRESHOLD])
                print(f"[✓] Segreto ricostruito: {secret}")
                # (Opzionale) invia conferma a tutti
                conn.sendall(f"Segreto ricostruito: {secret}".encode())
                print("")
            else:
                conn.sendall("[✓] Share ricevuta. In attesa di altri peer.".encode())
    except Exception as e:
        print(f"[!] Errore da {addr}: {e}")
    finally:
        conn.close()

def start_server():
    print(f"[S] Server in ascolto su {HOST}:{PORT} (soglia = {THRESHOLD})")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while secret is None:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
