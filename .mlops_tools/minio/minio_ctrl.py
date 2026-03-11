# pip install boto3 python-dotenv
import os
import sys
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
from botocore.config import Config
from dpath import delete

# Cargar variables del archivo .env
load_dotenv()

class MinioController:
    def __init__(self):
        # 1. Configuración de credenciales
        self.access_key = os.getenv('MINIO_ACCESS_KEY')
        self.secret_key = os.getenv('MINIO_SECRET_KEY')
        self.endpoint_url = os.getenv('MINIO_ENDPOINT_URL')
        self.region_name = os.getenv('MINIO_REGION', 'us-east-1')
        
        # Variables de contexto
        self.variant = os.getenv('VARIANT')
        self.fase = os.getenv('FASE')
        self.fase_urls = os.getenv('FASE_URLS')
        self.nombre_bucket = f"fase{self.fase}" # Dinámico según FASE
        print("@@@@@@@@@@@@@@@@")
        print(self.nombre_bucket)
        print("@@@@@@@@@@@@@@@@")

        if not all([self.access_key, self.secret_key, self.endpoint_url]):
            raise ValueError("Error: Faltan credenciales de MinIO en .env")

        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name,
            config=Config(request_checksum_calculation='when_required')
        )

    def push(self):
        """Sube archivos o directorios manteniendo la estructura."""
        ruta_local = os.path.join(self.fase_urls, self.variant)
        
        try:
            if os.path.isdir(ruta_local):
                print(f"--- Iniciando PUSH desde directorio: {ruta_local} ---")
                for root, _, files in os.walk(ruta_local):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # La 'Key' en S3 será: variant/subcarpetas/archivo
                        rel_path = os.path.relpath(full_path, os.path.dirname(ruta_local))
                        
                        self.s3.upload_file(full_path, self.nombre_bucket, rel_path)
                        print(f"  [SUBIDO] {rel_path}")
            else:
                print(f"--- Subiendo archivo único: {ruta_local} ---")
                self.s3.upload_file(ruta_local, self.nombre_bucket, self.variant)
            
            print("¡Push finalizado con éxito!")
        except Exception as e:
            print(f"Error en PUSH: {e}")

    def pull(self, prefix=None):
        """Descarga todo lo que coincida con el prefijo (normalmente la VARIANT)."""
        # Si no se pasa prefijo, usamos la variant del .env
        prefix = prefix or self.variant
        print(f"--- Iniciando PULL para el prefijo: {prefix} ---")

        try:
            # Listar objetos que empiezan con la variante
            paginator = self.s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.nombre_bucket, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_key = obj['Key']
                        # Definir dónde se guardará localmente
                        local_file_path = os.path.join(self.fase_urls, s3_key)
                        
                        # Crear las carpetas locales si no existen
                        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                        
                        print(f"  [DESCARGANDO] {s3_key}...")
                        self.s3.download_file(self.nombre_bucket, s3_key, local_file_path)
                else:
                    print(f"No se encontraron archivos con el prefijo '{prefix}' en el bucket.")
            
            print("¡Pull finalizado con éxito!")
        except Exception as e:
            print(f"Error en PULL: {e}")

    def delete(self, prefix=None):
        """Elimina todos los objetos en el bucket que coincidan con el prefijo."""
        prefix = prefix or self.variant
        print(f"--- Iniciando DELETE para el prefijo: {prefix} en bucket: {self.nombre_bucket} ---")

        try:
            # 1. Identificar los objetos a borrar
            paginator = self.s3.get_paginator('list_objects_v2')
            objetos_a_borrar = []

            for page in paginator.paginate(Bucket=self.nombre_bucket, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objetos_a_borrar.append({'Key': obj['Key']})

            # 2. Proceder al borrado si hay archivos
            if objetos_a_borrar:
                # S3 permite borrar hasta 1000 objetos por llamada
                # Para simplificar, lo hacemos en bloques si fuera necesario
                for i in range(0, len(objetos_a_borrar), 1000):
                    batch = objetos_a_borrar[i:i + 1000]
                    response = self.s3.delete_objects(
                        Bucket=self.nombre_bucket,
                        Delete={'Objects': batch}
                    )
                    
                    # Opcional: imprimir qué se borró
                    for del_obj in response.get('Deleted', []):
                        print(f"  [ELIMINADO] {del_obj['Key']}")
                
                print(f"¡Delete finalizado! Se eliminaron {len(objetos_a_borrar)} objetos.")
            else:
                print(f"No se encontraron archivos con el prefijo '{prefix}' para eliminar.")

        except Exception as e:
            print(f"Error en DELETE: {e}")

    def list_files(self):
        """Muestra el contenido actual del bucket."""
        print(f"\n--- Archivos en bucket {self.nombre_bucket} ---")
        response = self.s3.list_objects_v2(Bucket=self.nombre_bucket)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"- {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("El bucket está vacío.")


if __name__ == "__main__":
    ctrl = MinioController()
    
    # Verificamos qué comando llega desde el Makefile
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
        # Por defecto si no hay argumentos, puedes listar o no hacer nada
        ctrl.list_files()