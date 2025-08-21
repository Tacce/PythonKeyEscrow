# Key Escrow con Secret Sharing e Socket SSL in Python

Questo progetto è valido per la parte pratica dell’esame di **Sicurezza dell’Informazione** del corso di Laurea Magistrale in Ingengeria Informatica dell'Università di Bologna (UNIBO).  
L’obiettivo è quello implementare in Python un semplice sistema di **Key Escrow** basato su *Shamir’s Secret Sharing* con comunicazione sicura via **socket SSL/TLS**.

---

## Descrizione del progetto

Il progetto simula un sistema di escrow delle chiavi, composto da:

- **Holder**: detiene il segreto (denominato `SECRET`) e lo divide in `N` *share* usando Shamir Secret Sharing.
- **Peer**: ciascun peer riceve una *share* dall’holder e la inoltra al server centrale.
- **Server centrale**: riceve le share dai peer e, raggiunta la soglia `T`, ricostruisce il segreto originale.


### Architettura del sistema 
```bash
                ┌───────────┐
                │  HOLDER   │
                │ (segreto) │
                └─────┬─────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │  PEER1  │   │  PEER2  │   │  PEER3  │  ... (fino a N)
   │ (share) │   │ (share) │   │ (share) │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │             │
        └───────┬─────┴───────┬─────┘
                │             │
                ▼             ▼
             ┌───────────────────┐
             │       SERVER      │
             │  (ricostruzione)  │
             └───────────────────┘
```


### Flusso di esecuzione

1. L’**Holder** genera `N` share del segreto con soglia `T`.
2. Le share vengono distribuite ai **Peer** tramite connessioni SSL/TLS.
3. Ogni **Peer** riceve la propria share, la valida e la inoltra al **Server**.
4. Il **Server**, al raggiungimento della soglia `T`, ricostruisce il segreto tramite interpolazione di Lagrange.

---

## Struttura del codice

- `holder.py` → genera e distribuisce le share ai peer.  
- `peer.py` → riceve la share dall’holder e la invia al server.  
- `server.py` → raccoglie le share e ricostruisce il segreto quando ne ha abbastanza.  
- `secret_sharing.py` → implementa la logica relativa al Secret Sharing (generazione e ricostruzione delle share).  
- `peers.json` → file di configurazione con elenco dei peer e delle porte associate.  
- `PKI/` → cartella contenente certificati e chiavi (CA, holder, peerX).

---

## Sicurezza

- Tutte le comunicazioni avvengono tramite **SSL/TLS** con **mutua autenticazione** grazie all'utilizzo del modulo `ssl` di P.  
- Una **CA locale** firma i certificati di holder, peer e server.  
- Le connessioni vengono accettate solo se i certificati sono validi e appartengono alla stessa CA.

---

## Come eseguire il codice

1. **Preparare la PKI**  
   Generare la CA e i certificati per holder, peer e server (già inclusi nella cartella `PKI/` in questa demo).
   Lo script `generate_cert.bat` permette di generare i certificati per server, peer e holder firmati dalla CA.
    
3. **Avviare il server**  
   ```bash
   python server.py

4. **Avviare l'holder**
   ```bash
   python holder.py

5. **Avviare i peer**
   ```bash
   python peer.py --id 1
   python peer.py --id 2
   ...

---

## Note

Il progetto è pensato come prototipo didattico e in quanto tale presenta alcune semplificazioni:

- Tutte le chiavi private e i certificati sono salvati in chiaro nella cartella `PKI/` senza alcuna protezione con password, HSM o storage sicuro.
In un ambiente reale sarebbe necessario proteggerle con permessi ristretti, cifratura del filesystem o dispositivi hardware.

- I certificati contengono `localhost` e `127.0.0.1` come SAN (Subject Alternative Name), quindi sono validi solo in test locali. In un sistema reale andrebbe usata una PKI vera, con gestione della revoca (CRL/OCSP).

- Non viene fatta una gestione avanzata degli errori TLS.
