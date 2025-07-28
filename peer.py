import socket
import json
import argparse
import ssl
import time

CONFIG_FILE = "peers.json"

def send_share(host, port, x, y, peer_id):
    certfile = f"PKI/peer{peer_id}-cert.pem"
    keyfile = f"PKI/peer{peer_id}-key.pem"
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations("PKI/ca-cert.pem")
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    context.check_hostname = False  # Per localhost

    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            share = {"x": x, "y": y}
            ssock.sendall(json.dumps(share).encode())
            response = ssock.recv(1024).decode()
            print(f"[SERVER] {response}")

def receive_share(port, server_host, server_port, peer_id):
    print(f"[.] Peer{peer_id} in ascolto su porta {port} per ricevere la share...")

    # Configura il contesto SSL per il server (peer)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(f"PKI/peer{peer_id}-cert.pem", f"PKI/peer{peer_id}-key.pem")
    context.load_verify_locations("PKI/ca-cert.pem")
    context.verify_mode = ssl.CERT_REQUIRED  
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', port))
        s.listen(1)
        print(f"[P] SSL Server avviato su 127.0.0.1:{port}")

        try:
            # Accetta connessione normale prima
            conn, addr = s.accept()
            print(f"[P] Connessione ricevuta da {addr}")
            
            # Poi avvolgi con SSL
            with context.wrap_socket(conn, server_side=True) as ssock:
                print(f"[✓] Handshake SSL completato con {addr}")
                
                # Informazioni sul certificato del client (se presente)
                peer_cert = ssock.getpeercert()
                if peer_cert:
                    holder_cn = None
                    for subject in peer_cert.get('subject', []):
                        for key, value in subject:
                            if key == 'commonName':
                                holder_cn = value
                                break
                    print(f"[.] Holder autenticato: {holder_cn}")

                # Ricevi dati
                data = ssock.recv(1024)
                    
                share_data = data.decode()
                share = json.loads(share_data)
                print(f"[→] Share ricevuta: {share}")

                # Invia la share al server centrale
                try:
                    send_share(server_host, server_port, share["x"], share["y"], peer_id)
                    response_msg = "Share ricevuta e inviata al server."
                except Exception as e:
                    print(f"[!] Errore invio al server: {e}")
                    response_msg = f"Errore invio server: {e}"

                # Invia risposta all'holder
                ssock.sendall(response_msg.encode())
                print("[→] Risposta inviata. Chiusura connessione.")
                
        except ssl.SSLError as e:
            print(f"[!] Errore SSL: {e}")
            print(f"[!] Tipo errore: {type(e).__name__}")
        except json.JSONDecodeError as e:
            print(f"[!] Errore JSON: {e}")
            try:
                ssock.sendall(b"Errore: formato JSON non valido")
            except:
                pass
        except ConnectionResetError as e:
            print(f"[!] Connessione reset dal client: {e}")
        except Exception as e:
            print(f"[!] Errore durante elaborazione: {e}")
                    
        except KeyboardInterrupt:
            print("[ℹ] Interruzione utente")
        except Exception as e:
            print(f"[!] Errore server: {e}")

def main():
    parser = argparse.ArgumentParser(description="Peer for key escrow")
    parser.add_argument("--id", type=int, required=True, help="Peer ID in the configuration file")
    args = parser.parse_args()
    
    if args.id is None:
        print("Errore: --id è obbligatorio")
        return
    
    with open(CONFIG_FILE, "r") as f:
        peers = json.load(f)

    peer = next((p for p in peers if p.get("id") == args.id), None)
    if peer is None:
        print(f"Peer con ID {args.id} non trovato nel file di configurazione.")
        return

    print(f"[P] Avvio peer {peer['id']} su porta {peer['port']}")
    receive_share(peer["port"], "localhost", 5000, peer["id"])

if __name__ == "__main__":
    main()