# pip install requests pynacl python-dotenv
import requests
from base64 import b64encode
from nacl import encoding, public
from dotenv import dotenv_values

# ==========================================
#         VARIABLES GLOBALES
# ==========================================
# Tu Personal Access Token (PAT) de GitHub (debe tener el scope 'repo')
# GITHUB_TOKEN = "ghp_tu_token_aqui_xxxxxxxxxxxx"
GITHUB_TOKEN = dotenv_values(".env").get("GITHUB_CTRL_SECRET_TOKEN")  # Lee el token desde .env para mayor seguridad

# El repositorio en formato "usuario/repositorio" o "organizacion/repositorio"
REPOSITORY = "Tehedor/MLOps_actions"

# Lista con las rutas a los archivos .env que quieres procesar
ENV_FILES = [
    ".mlops_tools/gdrive/.env-gfolders",
]
# ==========================================

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_repo_public_key():
    """Obtiene la clave pública del repositorio necesaria para encriptar los secretos."""
    url = f"https://api.github.com/repos/{REPOSITORY}/actions/secrets/public-key"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encripta el secreto usando la clave pública (Requisito estricto de GitHub)."""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def upload_secret(secret_name: str, encrypted_value: str, key_id: str):
    """Sube el secreto ya encriptado a GitHub Actions."""
    url = f"https://api.github.com/repos/{REPOSITORY}/actions/secrets/{secret_name}"
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    response = requests.put(url, headers=HEADERS, json=data)
    if response.status_code in [201, 204]:
        print(f"✅ Secreto '{secret_name}' subido/actualizado correctamente.")
    else:
        print(f"❌ Error al subir '{secret_name}': {response.status_code} - {response.text}")

def main():
    print(f"Obteniendo clave pública para {REPOSITORY}...")
    try:
        key_info = get_repo_public_key()
        public_key = key_info["key"]
        key_id = key_info["key_id"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener la clave pública. Verifica tu TOKEN y REPOSITORY. Detalle: {e}")
        return

    for env_file in ENV_FILES:
        print(f"\n📁 Procesando archivo: {env_file}...")
        
        # Lee el archivo .env como un diccionario sin cargar las variables al sistema local
        secrets = dotenv_values(env_file)
        
        if not secrets:
            print(f"⚠️ No se encontraron variables en {env_file} o el archivo no existe.")
            continue

        for secret_name, secret_value in secrets.items():
            if secret_value is None:
                continue # Ignora variables vacías
            
            # GitHub requiere que los nombres de los secretos sean en mayúsculas y sin caracteres especiales extraños
            clean_name = secret_name.strip().upper()
            
            # Encriptar y subir
            encrypted_value = encrypt_secret(public_key, str(secret_value))
            upload_secret(clean_name, encrypted_value, key_id)

    print("\n🚀 ¡Proceso finalizado!")

if __name__ == "__main__":
    main()