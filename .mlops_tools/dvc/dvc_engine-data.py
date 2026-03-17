import os
import sys
import subprocess
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TOKEN_DVC_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'credentials', 'dvc_token.json'))
TOKEN_DVC_PATH_NAME = os.path.abspath(os.getenv('DVC_TOKEN_PATH', DEFAULT_TOKEN_DVC_PATH))

class DVCController:
    def __init__(self):
        # 1. Configuración de credenciales
        self.client_id = os.getenv('GDRIVE_CLIENT_ID')
        self.client_secret = os.getenv('GDRIVE_CLIENT_SECRET')
        
        # Variables de contexto
        # Por defecto errror si no existe
        self.fase = os.getenv('FASE')
        if not self.fase:
            print("[ERROR] No se ha definido la variable de entorno FASE. Por favor, añádela al .env (ej: FASE=1)")
            sys.exit(1)
     
        # 2. Obtener el ID de la carpeta base según la fase
        folder_env_key = f"FASE{self.fase}_FOLDER_ID"
        self.remote_folder_id = os.getenv(folder_env_key)
        
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

    def setup(self):
        """Configura Google Drive como remote y aplica las credenciales locales."""
        if not all([self.client_id, self.client_secret, self.remote_folder_id]):
            print("[ERROR] Faltan variables de entorno (GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET o FASE_FOLDER_ID)")
            sys.exit(1)

        print(f"--- Configurando DVC Remote ({self.remote_name}) ---")
        
        cmd_add = f"dvc remote add --force {self.remote_name} gdrive://{self.remote_folder_id}"
        print(f"> {cmd_add}")
        self._run_command(cmd_add)


        # cmd_use_service_account = (
        #     f"dvc remote modify --local {self.remote_name} "
        #     "gdrive_use_service_account true"
        # )
        # print(f"> {cmd_use_service_account}")
        # self._run_command(cmd_use_service_account)

        cmd_client = f"dvc remote modify --local {self.remote_name} gdrive_client_id {self.client_id}"
        print(f"> {cmd_client}")
        self._run_command(cmd_client)

        cmd_secret = f"dvc remote modify --local {self.remote_name} gdrive_client_secret {self.client_secret}"
        print(f"> {cmd_secret}")
        self._run_command(cmd_secret)

            # dvc remote modify myremote0 gdrive_user_credentials_file $GITHUB_WORKSPACE/token.json --local
        cmd_ctrl_token = f"dvc remote modify --local {self.remote_name} gdrive_user_credentials_file {TOKEN_DVC_PATH_NAME}"
        print(f"> {cmd_ctrl_token}")
        self._run_command(cmd_ctrl_token)
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