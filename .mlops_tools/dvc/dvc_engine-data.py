import cmd
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
        
        # Variables de contexto (igual que en tu GDriveController)
        self.fase = os.getenv('FASE', '0') # Por defecto 1 si no existe
     
        # 2. Obtener el ID de la carpeta base según la fase (Tu antiguo $F00_DATA)
        folder_env_key = f"FASE{self.fase}_FOLDER_ID"
        self.remote_folder_id = os.getenv(folder_env_key)
        
        self.remote_name = "myremote" + self.fase 

        print("@@@@@@@@@@@@@@@@@@@@@@@@")
        print(f"DVC Config - Fase {self.fase}")
        print(f"Target GDrive Folder: {self.remote_folder_id}")
        print("@@@@@@@@@@@@@@@@@@@@@@@@\n")

    def _run_command(self, command):
        """Método helper para ejecutar comandos de bash en Python y capturar errores."""
        try:
            # Ejecutamos el comando. check=True hace que lance una excepción si falla.
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                text=True,
                # Redirigimos la salida para que se imprima en la consola en tiempo real
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] El comando DVC falló con código {e.returncode}")
            return False

    def setup(self):
        """Configura Google Drive como remote y aplica las credenciales locales."""
        if not all([self.client_id, self.client_secret, self.remote_folder_id]):
            print("[ERROR] Faltan variables en el .env (GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET o FASE_FOLDER_ID)")
            return

        print(f"--- Configurando DVC Remote ({self.remote_name}) ---")
        
        # 1. Añadir el remote (equivalente a: dvc remote add -d myremote gdrive://ID)
        # Usamos --force por si el remote ya existe, para sobreescribirlo sin dar error
        cmd_add = f"dvc remote add {self.remote_name} gdrive://{self.remote_folder_id}"
        print(f"> {cmd_add}")
        self._run_command(cmd_add)

        # 2. Inyectar Client ID en config.local
        cmd_client = f"dvc remote modify --local {self.remote_name} gdrive_client_id {self.client_id}"
        print(f"> {cmd_client}")
        self._run_command(cmd_client)

        # 3. Inyectar Client Secret en config.local
        cmd_secret = f"dvc remote modify --local {self.remote_name} gdrive_client_secret {self.client_secret}"
        print(f"> {cmd_secret}")
        self._run_command(cmd_secret)

        print("¡Configuración de DVC completada con éxito!")

    def push(self):
        """Sube los datos cacheados al remote configurado."""
        print("--- Iniciando DVC PUSH ---")
        cmd_push = f"dvc push -r {self.remote_name}"
        print(f"> {cmd_push}")
        self._run_command(cmd_push)

    def pull(self):
        """Descarga los datos desde el remote configurado."""
        print("--- Iniciando DVC PULL ---")
        cmd_pull = f"dvc pull -r {self.remote_name}"
        print(f"> {cmd_pull}")
        self._run_command(cmd_pull)

    def status(self):
        """Comprueba el estado de los datos (qué falta por subir/bajar)."""
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
    else:
        # Por defecto muestra el estado
        ctrl.status()