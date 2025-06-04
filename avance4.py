from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
import os

private_key_A = None
private_key_B = None
public_key_A = None
public_key_B = None
shared_secret = None
derived_key = None
salt = None

# Generar pares X25519 
def generar_pares():
    global private_key_A, private_key_B, public_key_A, public_key_B
    private_key_A = x25519.X25519PrivateKey.generate()
    public_key_A = private_key_A.public_key()

    private_key_B = x25519.X25519PrivateKey.generate()
    public_key_B = private_key_B.public_key()

    print("\n✔ Pares de claves generados:")
    print(f"Public Key A: {public_key_A.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw).hex()}")
    print(f"Public Key B: {public_key_B.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw).hex()}")

# Calcular clave compartida 
def calcular_clave_compartida():
    global shared_secret
    if private_key_A is None or public_key_B is None:
        print("\n Error: primero genera los pares de claves.")
        return

    shared_secret = private_key_A.exchange(public_key_B)
    print("\n Clave compartida (A con B):")
    print(shared_secret.hex())

# Derivar clave con HKDF 
def derivar_clave_con_hkdf():
    global derived_key, salt
    if shared_secret is None:
        print("\n Error: primero calcula la clave compartida.")
        return

    salt = os.urandom(32)
    info = b'X25519 Key Agreement'

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
    )
    derived_key = hkdf.derive(shared_secret)

    print("\n Clave derivada con HKDF + SHA-256:")
    print(f"Derived Key: {derived_key.hex()}")
    print(f"Salt usado: {salt.hex()}")


def menu():
    while True:
        print("\n--- MENÚ DE PRUEBAS X25519 + HKDF ---")
        print("1. Generar pares X25519")
        print("2. Calcular clave compartida")
        print("3. Derivar clave con HKDF")
        print("4. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            generar_pares()
        elif opcion == '2':
            calcular_clave_compartida()
        elif opcion == '3':
            derivar_clave_con_hkdf()
        elif opcion == '4':
            print("Saliendo del programa.")
            break
        else:
            print(" Opción no válida.")

if __name__ == "__main__":
    menu()
