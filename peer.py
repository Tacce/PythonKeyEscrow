import socket
import json
import argparse

CONFIG_FILE = "peers.json"


def send_share(host, port, x, y):
    share = {"x": x, "y": y}
    data = json.dumps(share)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode())

        response = s.recv(1024).decode()
        print(f"[SERVER] {response}")

def receive_share(port, server_host, server_port):
    print(f"[.] Peer in ascolto su porta {port} per ricevere la share...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', port))
        s.listen(1)

        conn, addr = s.accept()
        with conn:
            print(f"[✓] Connessione ricevuta da {addr}")
            data = conn.recv(1024).decode()
            share = json.loads(data)
            print(f"[→] Share ricevuta: {share}")

            # Invia la share al server centrale
            send_share(server_host, server_port, share["x"], share["y"])
            print("[→] Share inviata al server centrale. Chiusura.")

def main():
    parser = argparse.ArgumentParser(description="Peer for key escrow")
    parser.add_argument("--id", type=int, required=False, help="Peer ID in the configuration file")
    args = parser.parse_args()
    
    with open(CONFIG_FILE, "r") as f:
        peers = json.load(f)

    peer = next((p for p in peers if p.get("id") == args.id), None)
    if peer is None:
        print("Peer con l'ID specificato non trovato nel file di configurazione.")
        return

    receive_share(peer["port"], "localhost", 5000)

if __name__ == "__main__":
    main()

