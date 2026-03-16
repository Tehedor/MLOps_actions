import json
import os
import shlex
import sys
import subprocess
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

GOOGLE_ACCOUNT_SERVICE_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './credentials/service_account.json')

class DVCController:
    def __init__(self):
        # 1. Configuración de credenciales
        self.credentials_file = GOOGLE_ACCOUNT_SERVICE_CREDENTIALS
        self.service_account_user_email = None
        
        # Variables de contexto
        # Por defecto errror si no existe
        self.fase = os.getenv('FASE')
        if not self.fase:
            print("[ERROR] No se ha definido la variable de entorno FASE. Por favor, añádela al .env (ej: FASE=1)")
            sys.exit(1)
     
        # 2. Obtener el ID de la carpeta base según la fase
        folder_env_key = f"FASE{self.fase}_FOLDER_ID"
        self.remote_folder_id = os.getenv(folder_env_key)

        if self.credentials_file:
            self.credentials_file = os.path.abspath(self.credentials_file)
        
        # Generar nombre del remote dinámico
        self.remote_name = "myremote" + self.fase 

        print("@@@@@@@@@@@@@@@@@@@@@@@@")
        print(f"DVC Config - Fase {self.fase}")
        print(f"Target GDrive Folder: {self.remote_folder_id}")
        print("@@@@@@@@@@@@@@@@@@@@@@@@\n")

    def _run_command(self, command):
        """Ejecuta comandos y corta en cuanto detecta OAuth interactivo en CI."""
        oauth_markers = (
            "Your browser has been opened to visit:",
            "accounts.google.com/o/oauth2/auth",
            "The operation was canceled.",
        )

        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )

        interactive_oauth_detected = False
        for line in process.stdout:
            print(line, end="")
            if any(marker in line for marker in oauth_markers):
                interactive_oauth_detected = True
                break

        if interactive_oauth_detected:
            process.kill()
            process.wait()
            print("\n[ERROR] DVC intentó autenticación interactiva (abrir navegador).")
            print("[ERROR] Aborta el paso. Revisa token/credenciales de GDrive en CI.")
            sys.exit(2)

        return_code = process.wait()
        if return_code != 0:
            print(f"\n[ERROR] El comando falló con código {return_code}: {command}")
            sys.exit(return_code)

        return True

    def _load_service_account_email(self):
        """Obtiene el email de la cuenta de servicio desde el JSON de credenciales."""
        try:
            with open(self.credentials_file, encoding='utf-8') as credentials_file:
                credentials_data = json.load(credentials_file)
        except OSError as exc:
            print(f"[ERROR] No se pudo leer el archivo de credenciales: {exc}")
            sys.exit(1)
        except json.JSONDecodeError as exc:
            print(f"[ERROR] El archivo de credenciales no contiene JSON válido: {exc}")
            sys.exit(1)

        service_account_email = credentials_data.get('client_email')
        if not service_account_email:
            print("[ERROR] El archivo de credenciales no incluye el campo client_email")
            sys.exit(1)

        return service_account_email

    def setup(self):
        """Configura Google Drive como remote usando una cuenta de servicio."""
        if not all([self.credentials_file, self.remote_folder_id]):
            print("[ERROR] Faltan variables de entorno (GOOGLE_APPLICATION_CREDENTIALS o FASE_FOLDER_ID)")
            sys.exit(1)

        if not os.path.exists(self.credentials_file):
            print(f"[ERROR] No se encontró el archivo de credenciales: {self.credentials_file}")
            sys.exit(1)

        self.service_account_user_email = self._load_service_account_email()

        print(f"--- Configurando DVC Remote ({self.remote_name}) ---")
        
        cmd_add = f"dvc remote add --force {self.remote_name} gdrive://{self.remote_folder_id}"
        print(f"> {cmd_add}")
        self._run_command(cmd_add)

        cmd_use_service_account = (
            f"dvc remote modify --local {self.remote_name} "
            "gdrive_use_service_account true"
        )
        print(f"> {cmd_use_service_account}")
        self._run_command(cmd_use_service_account)

        cmd_service_account_file = (
            f"dvc remote modify --local {self.remote_name} "
            f"gdrive_service_account_json_file_path {shlex.quote(self.credentials_file)}"
        )
        print(f"> {cmd_service_account_file}")
        self._run_command(cmd_service_account_file)

        if self.service_account_user_email:
            cmd_user_email = (
                f"dvc remote modify --local {self.remote_name} "
                f"gdrive_service_account_user_email {shlex.quote(self.service_account_user_email)}"
            )
            print(f"> {cmd_user_email}")
            self._run_command(cmd_user_email)

        print("¡Configuración de DVC completada con éxito!")

    def push(self):
        print("--- Iniciando DVC PUSH ---")
        cmd_push = f"dvc push -r {self.remote_name}"
        print(f"> {cmd_push}")
        self._run_command(cmd_push)

    def pull(self):
        print("--- Iniciando DVC PULL ---")
        cmd_pull = f"dvc pull -r {self.remote_name}"
        print(f"> {cmd_pull}")
        self._run_command(cmd_pull)

    def status(self):
        print("--- Comprobando DVC STATUS ---")
        cmd_status = f"dvc status -r {self.remote_name}"
        print(f"> {cmd_status}")
        self._run_command(cmd_status)


if __name__ == "__main__":
    ctrl = DVCController()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        if comando == "setup":
            ctrl.setup()
        elif comando == "push":
            ctrl.push()
        elif comando == "pull":
            ctrl.pull()
        elif comando == "status":
            ctrl.status()
        else:
            print(f"Comando desconocido: {comando}")
            print("Comandos disponibles: setup, push, pull, status")
            sys.exit(1)
    else:
        ctrl.status()