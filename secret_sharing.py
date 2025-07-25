import random
from functools import reduce

# Primo numero primo abbastanza grande per l'aritmetica modulare
PRIME = 20891

def eval_polynomial(coeffs, x, p):
    """Valuta il polinomio in x modulo p"""
    return sum([coeff * pow(x, i, p) for i, coeff in enumerate(coeffs)]) % p

def generate_shares(secret, t, n, p=PRIME):
    """Genera n share da un segreto usando un polinomio di grado t-1"""
    coeffs = [secret] + [random.randint(0, p - 1) for _ in range(t - 1)]
    shares = [(i, eval_polynomial(coeffs, i, p)) for i in range(1, n + 1)]
    return shares

def reconstruct_secret(shares, p=PRIME):
    """Ricostruisce il segreto con l'interpolazione di Lagrange"""
    def lagrange_basis(j, x=0):
        xj, _ = shares[j]
        num = den = 1
        for m in range(len(shares)):
            if m != j:
                xm, _ = shares[m]
                num = (num * (x - xm)) % p
                den = (den * (xj - xm)) % p
        return num * pow(den, -1, p)

    secret = sum([y * lagrange_basis(j) for j, (_, y) in enumerate(shares)]) % p
    return secret


'''
# Esempio di utilizzo del modulo di condivisione segreti
if __name__ == "__main__":
    secret = 1234
    t = 3  # numero minimo di share per ricostruire
    n = 5  # numero totale di share

    print(f"Segreto originale: {secret}")
    shares = generate_shares(secret, t, n)
    print("\nShare generati:")
    for s in shares:
        print(s)


    # Prendi 3 share a caso per ricostruire
    selected = random.sample(shares, t)
    print("\nShare selezionati per la ricostruzione:")
    print(selected)

    recovered = reconstruct_secret(selected)
    print(f"\nSegreto ricostruito: {recovered}")
'''