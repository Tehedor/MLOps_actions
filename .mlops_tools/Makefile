SHELL := /bin/bash

############################################
# ENTORNO DE EJECUCIÓN (PIPELINE)
############################################
PYTHON := ../.venv/bin/python3

# ifeq ($(OS),Windows_NT)
# 	PYTHON := .venv/Scripts/python.exe
# 	DVC := .venv/Scripts/dvc.exe
# 	JUPYTER := .venv/Scripts/jupyter.exe
# else
# 	ifneq ("$(wildcard .venv/bin/python3)","")
# 		DVC := .venv/bin/dvc
# 		JUPYTER := .venv/bin/jupyter
# 	else
# 		PYTHON := python3
# 		DVC := dvc
# 		JUPYTER := jupyter
# 	endif
# endif

$(info [INFO] Usando interprete Python en venv: $(PYTHON))

############################################
# Variables
############################################
FASE ?=
VARIANT ?=
# MINIO_CTRL_SCRIPT := .mlops_tools/minio/minio_ctrl.py
MINIO_CTRL_SCRIPT := minio/minio_ctrl.py
GDRIVE_CTRL_SCRIPT := gdrive/gdrive_ctrl.py
GDRIVE_CTRL_SERVICE_SCRIPT := gdrive/gdrive_ctrl-service.py
VARIANT_ENGINE := ${GDRIVE_CTRL_SCRIPT}


FASE0 := ../data/raw.csv
FASE1 := ../executions/01_explore
FASE2 := ../executions/02_prepareeventsds
FASE3 := ../executions/03_preparewindowsds
FASE4 := ../executions/04_targetengineering
FASE5 := ../executions/05_modeling
FASE6 := ../executions/06_packaging
FASE7 := ../executions/07_deployrun

############################################
# CHECK
############################################
.PHONY: \
	check_artifact \
	check_artifact_fase1 \
	push_to_storage \
	push_to_storage_fase1 \
	push_to_storgage \
	push_to_storgage_fase1 \
	pull_from_storage \
	pull_from_storage_fase1


check_artifact: 

check_artifact_fase1: 


############################################
# CHECK
############################################




############################################
# PUSH & PULL
############################################
push_to_storage:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" VARIANT="$(VARIANT)" $(PYTHON) $(VARIANT_ENGINE) push


# make push_to_storage_fase1 VARIANT=v100
push_to_storage_fase1:
# 	@$(MAKE) check_artifact_fase1
	@$(MAKE) push_to_storage FASE=1 FASE_URLS="$(FASE1)" VARIANT="$(VARIANT)"


pull_from_storage:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" VARIANT="$(VARIANT)" $(PYTHON) $(VARIANT_ENGINE) pull

pull_from_storage_fase1:
# 	@$(MAKE) check_artifact_fase1
	@$(MAKE) pull_from_storage FASE=1 FASE_URLS="$(FASE1)" VARIANT="$(VARIANT)"

# Alias por compatibilidad con el typo anterior
push_to_storgage: push_to_storage

push_to_storgage_fase1: push_to_storage_fase1


pull_from_storage:

pull_from_storage_fase1:
############################################
# DELETE
############################################
delete_from_storage:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" VARIANT="$(VARIANT)" $(PYTHON) $(VARIANT_ENGINE) delete

delete_from_storage_fase1:
# 	@$(MAKE) check_artifact_fase1
	@$(MAKE) delete_from_storage FASE=1 FASE_URLS="$(FASE1)" VARIANT="$(VARIANT)"




############################################
# DVC
############################################
# dvc_start:
# 	dvc init


# if __name__ == "__main__":
#     ctrl = DVCController()
    
#     if len(sys.argv) > 1:
#         comando = sys.argv[1].lower()
#         if comando == "setup":
#             ctrl.setup()
#         elif comando == "push":
#             ctrl.push()
#         elif comando == "pull":
#             ctrl.pull()
#         elif comando == "status":
#             ctrl.status()
#         else:
#             print(f"Comando desconocido: {comando}")
#             print("Comandos disponibles: setup, push, pull, status")
#     else:
#         # Por defecto muestra el estado
#         ctrl.status()

DVC_ENGINE := "dvc/dvc_engine-data.py"

dvc_setup:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" $(PYTHON) $(DVC_ENGINE) setup
dvc_push:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" $(PYTHON) $(DVC_ENGINE) push
dvc_pull:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" $(PYTHON) $(DVC_ENGINE) pull
dvc_status:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" $(PYTHON) $(DVC_ENGINE) status


dvc_setup_fase0:
	@$(MAKE) dvc_setup FASE=0 FASE_URLS="$(FASE0)" 
dvc_push_fase0:
	@$(MAKE) dvc_push FASE=0 FASE_URLS="$(FASE0)" 
dvc_pull_fase0:
	@$(MAKE) dvc_pull FASE=0 FASE_URLS="$(FASE0)" 
dvc_status_fase0:
	@$(MAKE) dvc_status FASE=0 FASE_URLS="$(FASE0)"