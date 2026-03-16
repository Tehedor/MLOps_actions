# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv
# pip install google-api-python-client google-auth python-dotenv
import os
import sys
import io
from dotenv import load_dotenv

# Librerías de Google Drive para Cuenta de Servicio
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Cargar variables del archivo .env
load_dotenv()

# Permisos requeridos para leer, escribir y borrar en Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

GOOGLE_ACCOUNT_SERVICE_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './credentials/service_account.json')


class GDriveController:
    def __init__(self):
        # 1. Configuración de credenciales de la Cuenta de Servicio
        self.credentials_file = GOOGLE_ACCOUNT_SERVICE_CREDENTIALS
        
        # Variables de contexto
        self.variant = os.getenv('VARIANT')
        self.fase = os.getenv('FASE')
        self.fase_urls = os.getenv('FASE_URLS')
        
        # 2. Obtener el ID de la carpeta base según la fase
        folder_env_key = f"FASE{self.fase}_FOLDER_ID"
        self.base_folder_id = os.getenv(folder_env_key)
        
        print("@@@@@@@@@@@@@@@@")
        print(f"Carpeta Base GDrive (Fase {self.fase}): {self.base_folder_id}")
        print("@@@@@@@@@@@@@@@@")

        if not self.credentials_file or not self.base_folder_id:
            raise ValueError("Error: Falta la variable GOOGLE_APPLICATION_CREDENTIALS o el ID de la carpeta de la fase en .env")

        # 3. Autenticación Silenciosa
        self.service = self._authenticate()

    def _authenticate(self):
        """Autenticación silenciosa mediante Cuenta de Servicio para entornos automatizados."""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"No se encontró el archivo de credenciales JSON: {self.credentials_file}")
        
        # Cargamos las credenciales directamente desde el JSON
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_file, scopes=SCOPES)
            
        return build('drive', 'v3', credentials=creds)

    # --- HELPER METHODS PARA MANEJAR CARPETAS EN GDRIVE ---
    def _get_or_create_folder(self, folder_name, parent_id):
        """Busca una carpeta por nombre y parent. Si no existe, la crea."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
        response = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])
        
        if files:
            return files[0]['id']
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')

    def _resolve_path_to_folder_id(self, relative_path, base_parent_id):
        """Navega y crea la estructura jerárquica de carpetas en GDrive."""
        if relative_path in ['.', '']:
            return base_parent_id
            
        parts = os.path.normpath(relative_path).split(os.sep)
        current_parent_id = base_parent_id
        
        for part in parts:
            if part:
                current_parent_id = self._get_or_create_folder(part, current_parent_id)
        return current_parent_id

    # --- COMANDOS PRINCIPALES ---
    def push(self):
        """Sube archivos creando la estructura de carpetas en Drive."""
        ruta_local = os.path.join(self.fase_urls, self.variant)
        
        try:
            if os.path.isdir(ruta_local):
                print(f"--- Iniciando PUSH desde directorio: {ruta_local} ---")
                for root, _, files in os.walk(ruta_local):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Ejemplo: variant/subcarpeta
                        rel_dir = os.path.relpath(root, os.path.dirname(ruta_local))
                        
                        # Obtener ID de la carpeta en Drive donde va el archivo
                        folder_id = self._resolve_path_to_folder_id(rel_dir, self.base_folder_id)
                        
                        # Subir archivo
                        file_metadata = {'name': file, 'parents': [folder_id]}
                        media = MediaFileUpload(full_path, resumable=True)
                        
                        # Comprobar si ya existe para sobreescribir o crear nuevo
                        query = f"name='{file}' and '{folder_id}' in parents and trashed=false"
                        existing = self.service.files().list(q=query, fields='files(id)').execute().get('files', [])
                        
                        if existing:
                            self.service.files().update(fileId=existing[0]['id'], media_body=media).execute()
                            print(f"  [ACTUALIZADO] {os.path.join(rel_dir, file)}")
                        else:
                            self.service.files().create(body=file_metadata, media_body=media).execute()
                            print(f"  [SUBIDO] {os.path.join(rel_dir, file)}")
            else:
                print(f"--- Subiendo archivo único: {ruta_local} ---")
                file_name = os.path.basename(ruta_local)
                file_metadata = {'name': file_name, 'parents': [self.base_folder_id]}
                media = MediaFileUpload(ruta_local, resumable=True)
                self.service.files().create(body=file_metadata, media_body=media).execute()
                print(f"  [SUBIDO] {file_name}")
            
            print("¡Push finalizado con éxito!")
        except Exception as e:
            print(f"Error en PUSH: {e}")

    def _download_folder_recursive(self, folder_id, local_path):
        """Descarga todo el contenido de una carpeta de Drive de forma recursiva."""
        os.makedirs(local_path, exist_ok=True)
        query = f"'{folder_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        items = results.get('files', [])

        for item in items:
            item_path = os.path.join(local_path, item['name'])
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                self._download_folder_recursive(item['id'], item_path)
            else:
                print(f"  [DESCARGANDO] {item['name']}...")
                request = self.service.files().get_media(fileId=item['id'])
                fh = io.FileIO(item_path, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

    def pull(self, prefix=None):
        """Descarga la carpeta correspondiente a la variante actual."""
        prefix = prefix or self.variant
        print(f"--- Iniciando PULL para: {prefix} ---")

        try:
            # Buscar la carpeta raíz de la variante
            query = f"name='{prefix}' and '{self.base_folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
            items = results.get('files', [])

            if not items:
                print(f"No se encontró ninguna carpeta o archivo llamado '{prefix}' en la carpeta de la fase.")
                return

            item = items[0]
            local_target = os.path.join(self.fase_urls, prefix)

            if item['mimeType'] == 'application/vnd.google-apps.folder':
                self._download_folder_recursive(item['id'], local_target)
            else:
                # Es un archivo suelto
                os.makedirs(os.path.dirname(local_target), exist_ok=True)
                request = self.service.files().get_media(fileId=item['id'])
                with io.FileIO(local_target, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                print(f"  [DESCARGADO] {item['name']}")
            
            print("¡Pull finalizado con éxito!")
        except Exception as e:
            print(f"Error en PULL: {e}")

    def delete(self, prefix=None):
        """Elimina la carpeta o archivo que coincida con la variante."""
        prefix = prefix or self.variant
        print(f"--- Iniciando DELETE para: {prefix} ---")

        try:
            query = f"name='{prefix}' and '{self.base_folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            items = results.get('files', [])

            if items:
                for item in items:
                    self.service.files().delete(fileId=item['id']).execute()
                    print(f"  [ELIMINADO] {item['name']} (ID: {item['id']})")
                print("¡Delete finalizado con éxito!")
            else:
                print(f"No se encontró '{prefix}' para eliminar.")
        except Exception as e:
            print(f"Error en DELETE: {e}")

    def list_files(self):
        """Muestra el primer nivel de archivos en la carpeta de la fase."""
        print(f"\n--- Archivos en la carpeta de la fase (ID: {self.base_folder_id}) ---")
        try:
            query = f"'{self.base_folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, fields="files(name, mimeType)").execute()
            items = results.get('files', [])

            if items:
                for item in items:
                    tipo = "[CARPETA]" if item['mimeType'] == 'application/vnd.google-apps.folder' else "[ARCHIVO]"
                    print(f"- {tipo} {item['name']}")
            else:
                print("La carpeta está vacía.")
        except Exception as e:
            print(f"Error listando archivos: {e}")


if __name__ == "__main__":
    ctrl = GDriveController()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        if comando == "push":
            ctrl.push()
        elif comando == "pull":
            ctrl.pull()
        elif comando == "delete":
            ctrl.delete()
        elif comando == "list":
            ctrl.list_files()
        else:
            print(f"Comando desconocido: {comando}")
    else:
        ctrl.list_files()