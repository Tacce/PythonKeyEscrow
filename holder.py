import json
import socket
from secret_sharing import generate_shares

CONFIG_FILE = "peers.json"
SECRET = 1234
T = 3  # soglia
N = 5  # numero di peer

def send_share_to_peer(peer, share):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((peer["host"], peer["port"]))
        payload = {
            "id": peer["id"],
            "x": share[0],
            "y": share[1]
        }
        s.sendall(json.dumps(payload).encode())
        print(f"[✓] Share inviata a peer {peer['id']} ({peer['host']}:{peer['port']})")
    
if __name__ == "__main__":
    with open(CONFIG_FILE, "r") as f:
        peers = json.load(f)

    assert len(peers) == N, "Il numero di peer nella configurazione deve essere uguale a N"

    shares = generate_shares(SECRET, T, N)
    print("[*] Share generate. Inizio distribuzione...")

    is_shared = [False] * N

    while not all(is_shared):
        for i, (peer, share) in enumerate(zip(peers, shares)):
            if not is_shared[i]:
                try:
                    send_share_to_peer(peer, share)
                    is_shared[i] = True
                except Exception as e:
                    print(f"[!] Errore nel contattare peer {peer['id']}: {e}")


print(is_shared)