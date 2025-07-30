import json
import socket
import ssl
from secret_sharing import generate_shares

CONFIG_FILE = "peers.json"
SECRET = 1234
T = 3  # soglia
N = 5  # numero di peer

def send_share_to_peer(peer, share):
    try:
        # Configura il contesto SSL per il client (holder)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("PKI/ca-cert.pem")
        context.load_cert_chain("PKI/holder-cert.pem", "PKI/holder-key.pem")
        
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED  
        
        server_hostname = f"peer{peer['id']}.localhost"

        with socket.create_connection((peer["host"], peer["port"]), timeout=10) as sock:
            with context.wrap_socket(sock, server_side=False, server_hostname=server_hostname) as ssock:
                payload = {
                    "x": share[0],
                    "y": share[1]
                }
                message = json.dumps(payload).encode()
                ssock.sendall(message)
                
                # Aspetta risposta
                response = ssock.recv(1024).decode()
                print(f"[✓] Share inviata a peer {peer['id']} ({peer['host']}:{peer['port']})")
                print(f"[←] Risposta: {response}")
                
    except ssl.SSLError as e:
        print(f"[!] Errore SSL con peer {peer['id']}: {e}")
        raise
    except socket.timeout as e:
        print(f"[!] Timeout con peer {peer['id']}: {e}")
        raise
    except Exception as e:
        print(f"[!] Errore generico con peer {peer['id']}: {e}")
        raise

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
                    # Aggiungi un piccolo delay prima di riprovare
                    import time
                    time.sleep(1)

    print(f"[✓] Distribuzione completata: {is_shared}")