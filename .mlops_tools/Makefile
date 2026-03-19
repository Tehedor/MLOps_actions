SHELL := /bin/bash

############################################
# ENTORNO DE EJECUCIÓN (PIPELINE)
############################################
# PYTHON := ../.venv/bin/python3
PYTHON := python3
PYTHON-A := ../.venv/bin/activate

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
	push_variant_to_storage \
	push_variant_to_storage_fase1 \
	push_to_storgage \
	push_to_storgage_fase1 \
	pull_from_storage \
	pull_from_storage_fase1 \
	pull_variant_from_storage \
	pull_variant_from_storage_fase1


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

push_to_storage_fase2:
	@$(MAKE) push_to_storage FASE=2 FASE_URLS="$(FASE2)" VARIANT="$(VARIANT)"

push_to_storage_fase3:
	@$(MAKE) push_to_storage FASE=3 FASE_URLS="$(FASE3)" VARIANT="$(VARIANT)"

push_to_storage_fase4:
	@$(MAKE) push_to_storage FASE=4 FASE_URLS="$(FASE4)" VARIANT="$(VARIANT)"

push_to_storage_fase5:
	@$(MAKE) push_to_storage FASE=5 FASE_URLS="$(FASE5)" VARIANT="$(VARIANT)"



pull_from_storage:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" VARIANT="$(VARIANT)" $(PYTHON) $(VARIANT_ENGINE) pull

# make pull_from_storage_fase1 VARIANT=v100
pull_from_storage_fase1:
# 	@$(MAKE) check_artifact_fase1
	@$(MAKE) pull_from_storage FASE=1 FASE_URLS="$(FASE1)" VARIANT="$(VARIANT)"

pull_from_storage_fase2:
	@$(MAKE) pull_from_storage FASE=2 FASE_URLS="$(FASE2)" VARIANT="$(VARIANT)"

pull_from_storage_fase3:
	@$(MAKE) pull_from_storage FASE=3 FASE_URLS="$(FASE3)" VARIANT="$(VARIANT)"

pull_from_storage_fase4:
	@$(MAKE) pull_from_storage FASE=4 FASE_URLS="$(FASE4)" VARIANT="$(VARIANT)"

pull_from_storage_fase5:
	@$(MAKE) pull_from_storage FASE=5 FASE_URLS="$(FASE5)" VARIANT="$(VARIANT)"


push_variant_to_storage:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" VARIANT="$(VARIANT)" $(PYTHON) $(VARIANT_ENGINE) push-variant

# make push_variant_to_storage_fase1
push_variant_to_storage_fase1:
	@$(MAKE) push_variant_to_storage FASE=1 FASE_URLS="$(FASE1)"

push_variant_to_storage_fase2:
	@$(MAKE) push_variant_to_storage FASE=2 FASE_URLS="$(FASE2)"

push_variant_to_storage_fase3:
	@$(MAKE) push_variant_to_storage FASE=3 FASE_URLS="$(FASE3)"

push_variant_to_storage_fase4:
	@$(MAKE) push_variant_to_storage FASE=4 FASE_URLS="$(FASE4)"

push_variant_to_storage_fase5:
	@$(MAKE) push_variant_to_storage FASE=5 FASE_URLS="$(FASE5)"

pull_variant_from_storage:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" VARIANT="$(VARIANT)" $(PYTHON) $(VARIANT_ENGINE) pull-variant

# make pull_variant_from_storage_fase1
pull_variant_from_storage_fase1:
	@$(MAKE) pull_variant_from_storage FASE=1 FASE_URLS="$(FASE1)"

pull_variant_from_storage_fase2:
	@$(MAKE) pull_variant_from_storage FASE=2 FASE_URLS="$(FASE2)"

pull_variant_from_storage_fase3:
	@$(MAKE) pull_variant_from_storage FASE=3 FASE_URLS="$(FASE3)"

pull_variant_from_storage_fase4:
	@$(MAKE) pull_variant_from_storage FASE=4 FASE_URLS="$(FASE4)"

pull_variant_from_storage_fase5:
	@$(MAKE) pull_variant_from_storage FASE=5 FASE_URLS="$(FASE5)"



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

DVC_ENGINE := dvc/dvc_engine-data.py
# DVC_ENGINE := dvc/dvc_engine-data-AccountService.py

dvc_setup:
	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" $(PYTHON) $(DVC_ENGINE) setup
# 	. $(PYTHON-A) && \ 
# 	FASE="$(FASE)" FASE_URLS="$(FASE_URLS)" python $(DVC_ENGINE) setup


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





upload_secrets:
	@cd .. && \
	python .mlops_tools/githubActionsVars/upload_variables.py