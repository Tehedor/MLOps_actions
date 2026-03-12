import os
import sys
import subprocess
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class DVCController:
    def __init__(self):
        # 1. Configuración de credenciales
        self.client_id = os.getenv('GDRIVE_CLIENT_ID')
        self.client_secret = os.getenv('GDRIVE_CLIENT_SECRET')
        
        # Variables de contexto
        self.fase = os.getenv('FASE', '0') # Por defecto 0 si no existe
     
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
        """Método helper para ejecutar comandos de bash en Python y capturar errores."""
        try:
            # check=True hace que lance una excepción si falla (vital para CI/CD)
            subprocess.run(
                command, 
                shell=True, 
                check=True, 
                text=True,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] El comando falló con código {e.returncode}: {command}")
            # Forzar la salida con error para que GitHub Actions marque el paso como fallido
            sys.exit(e.returncode)

    def setup(self):
        """Configura Google Drive como remote y aplica las credenciales locales."""
        if not all([self.client_id, self.client_secret, self.remote_folder_id]):
            print("[ERROR] Faltan variables de entorno (GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET o FASE_FOLDER_ID)")
            sys.exit(1)

        print(f"--- Configurando DVC Remote ({self.remote_name}) ---")
        
        cmd_add = f"dvc remote add --force {self.remote_name} gdrive://{self.remote_folder_id}"
        print(f"> {cmd_add}")
        self._run_command(cmd_add)

        cmd_client = f"dvc remote modify --local {self.remote_name} gdrive_client_id {self.client_id}"
        print(f"> {cmd_client}")
        self._run_command(cmd_client)

        cmd_secret = f"dvc remote modify --local {self.remote_name} gdrive_client_secret {self.client_secret}"
        print(f"> {cmd_secret}")
        self._run_command(cmd_secret)

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