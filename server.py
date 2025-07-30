import socket
import threading
import json
import ssl
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

def handle_client(conn, addr, context):
    """Gestisce un singolo client con SSL"""
    try:
        # Wrap della connessione con SSL
        with context.wrap_socket(conn, server_side=True) as ssock:
            print(f"[+] Connessione SSL stabilita con {addr}")
            
            # Informazioni certificato client
            try:
                peer_cert = ssock.getpeercert()
                if peer_cert:
                    client_cn = None
                    for subject in peer_cert.get('subject', []):
                        for key, value in subject:
                            if key == 'commonName':
                                client_cn = value
                                break
                    print(f"[✓] Client autenticato: {client_cn}")
            except:
                print("[!] Nessun certificato client verificato")
            
            # Ricevi dati
            data = ssock.recv(1024).decode()
            share = json.loads(data)

            with lock:
                received_shares.append((share["x"], share["y"]))
                print(f"[+] Share ricevuta da {addr}: {share}")
                print(f"[~] Share totali ricevute: {len(received_shares)}")

                if len(received_shares) == THRESHOLD:
                    global secret
                    print("[*] Soglia raggiunta. Ricostruzione del segreto...")
                    secret = reconstruct_secret(received_shares[:THRESHOLD])
                    print("")
                    print(f"[✓] Segreto ricostruito: {secret}")
                    print("")
                    
            # Invia risposta
            ssock.sendall("[✓] Share ricevuta".encode())
            
    except ssl.SSLError as e:
        print(f"[!] Errore SSL da {addr}: {e}")
    except json.JSONDecodeError as e:
        print(f"[!] Errore JSON da {addr}: {e}")
    except Exception as e:
        print(f"[!] Errore generico da {addr}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"[S] Server in ascolto su {HOST}:{PORT} (soglia = {THRESHOLD})")

    # Crea contesto SSL server
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="PKI/server-cert.pem", keyfile="PKI/server-key.pem")
    context.load_verify_locations("PKI/ca-cert.pem")
    context.verify_mode = ssl.CERT_REQUIRED  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[S] Server SSL avviato su {HOST}:{PORT}")

        while secret is None:
            try:
                # Accept connessione normale
                print("[*] In attesa di nuove connessioni...")  
                conn, addr = s.accept()
                print(f"[-] Connessione ricevuta da {addr}")
                
                handle_client(conn, addr, context)
            
                    
            except Exception as e:
                print(f"[!] Errore nell'accettare connessioni: {e}")
                continue

