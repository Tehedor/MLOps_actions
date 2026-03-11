export $(grep -v '^#' .env | xargs)

# 4. Configurar Google Drive como tu almacenamiento remoto (Remote)
# Usamos la variable de entorno para el ID de la carpeta
dvc remote add -d myremote gdrive://$F00_DATA

# 5. Inyectar las credenciales en la configuración local de DVC
# Usamos --local para que se guarde en .dvc/config.local (que Git ignora)
dvc remote modify --local myremote gdrive_client_id $gdrive_client_id
dvc remote modify --local myremote gdrive_client_secret $gdrive_client_secret