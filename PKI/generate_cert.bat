@echo off
REM Genera certificati per holder, server e tutti i peer (1-5)

echo Generando certificato per holder...

REM Crea file di configurazione per holder
(
    echo [req]
    echo distinguished_name = req_distinguished_name
    echo req_extensions = v3_req
    echo prompt = no
    echo.
    echo [req_distinguished_name]
    echo C = IT
    echo ST = Emilia-Romagna
    echo L = Bologna
    echo O = UNIBO
    echo OU = Key Escrow Holder
    echo CN = holder.localhost
    echo.
    echo [v3_req]
    echo basicConstraints = CA:FALSE
    echo keyUsage = nonRepudiation, digitalSignature, keyEncipherment
    echo subjectAltName = @alt_names
    echo.
    echo [alt_names]
    echo DNS.1 = localhost
    echo DNS.2 = holder.localhost
    echo IP.1 = 127.0.0.1
) > holder.cnf

REM Genera chiave privata per holder
openssl genrsa -out holder-key.pem 2048

REM Genera CSR per holder
openssl req -new -key holder-key.pem -out holder.csr -config holder.cnf

REM Genera certificato firmato dalla CA per holder
openssl x509 -req -in holder.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out holder-cert.pem -days 365 -sha256 -extensions v3_req -extfile holder.cnf

REM Pulisci file temporanei holder
del holder.csr
del holder.cnf

echo Holder completato!
echo.

REM Genera certificati per tutti i peer (1-5)
for /L %%i in (1,1,5) do (
    echo Generando certificato per peer%%i...
    
    REM Crea file di configurazione per peer%%i
    (
        echo [req]
        echo distinguished_name = req_distinguished_name
        echo req_extensions = v3_req
        echo prompt = no
        echo.
        echo [req_distinguished_name]
        echo C = IT
        echo ST = Emilia-Romagna
        echo L = Bologna
        echo O = UNIBO
        echo OU = Key Escrow Peer
        echo CN = peer%%i.localhost
        echo.
        echo [v3_req]
        echo basicConstraints = CA:FALSE
        echo keyUsage = nonRepudiation, digitalSignature, keyEncipherment
        echo subjectAltName = @alt_names
        echo.
        echo [alt_names]
        echo DNS.1 = localhost
        echo DNS.2 = peer%%i.localhost
        echo IP.1 = 127.0.0.1
    ) > peer%%i.cnf
    
    REM Genera chiave privata
    openssl genrsa -out peer%%i-key.pem 2048
    
    REM Genera CSR
    openssl req -new -key peer%%i-key.pem -out peer%%i.csr -config peer%%i.cnf
    
    REM Genera certificato firmato dalla CA
    openssl x509 -req -in peer%%i.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out peer%%i-cert.pem -days 365 -sha256 -extensions v3_req -extfile peer%%i.cnf
    
    REM Pulisci file temporanei
    del peer%%i.csr
    del peer%%i.cnf
    
    echo Peer%%i completato!
    echo.
)

echo Tutti i certificati sono stati generati!
echo.

echo Generando certificato per server...

REM Crea file di configurazione per server
(
    echo [req]
    echo distinguished_name = req_distinguished_name
    echo req_extensions = v3_req
    echo prompt = no
    echo.
    echo [req_distinguished_name]
    echo C = IT
    echo ST = Emilia-Romagna
    echo L = Bologna
    echo O = UNIBO
    echo OU = Key Escrow Server
    echo CN = localhost
    echo.
    echo [v3_req]
    echo basicConstraints = CA:FALSE
    echo keyUsage = nonRepudiation, digitalSignature, keyEncipherment
    echo subjectAltName = @alt_names
    echo.
    echo [alt_names]
    echo DNS.1 = localhost
    echo DNS.2 = server.localhost
    echo IP.1 = 127.0.0.1
) > server.cnf

REM Genera chiave privata per server
openssl genrsa -out server-key.pem 2048

REM Genera CSR per server
openssl req -new -key server-key.pem -out server.csr -config server.cnf

REM Genera certificato firmato dalla CA per server
openssl x509 -req -in server.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 365 -sha256 -extensions v3_req -extfile server.cnf

REM Pulisci file temporanei server
del server.csr
del server.cnf

echo Server completato!

echo File generati:
dir /b *-cert.pem
dir /b *-key.pem