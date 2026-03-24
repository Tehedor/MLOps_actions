#!/usr/bin/env bash
set -euo pipefail

BRANCH_PREFIX="feature/fase1-mejoras"
BASE_BRANCH="main"
PR_TITLE="feat: add control file for testing pipeline"
PR_BODY="This PR adds a control file to validate the pipeline flow."
CONTROL_FILE="control_file"

BRANCH="${BRANCH_PREFIX}-$(date +%Y%m%d-%H%M%S)"
git checkout "$BASE_BRANCH"
git pull --ff-only origin "$BASE_BRANCH"
git checkout -b "$BRANCH"

RANDOM_VALUE="$(date +%s)-$RANDOM-$(head -c 8 /dev/urandom | od -An -tx1 | tr -d ' \n')"
printf "run_id=%s\n" "$RANDOM_VALUE" > "$CONTROL_FILE"
git add "$CONTROL_FILE"

if git diff --cached --quiet; then
	echo "No hay cambios para commitear."
else
	git commit -m "$PR_TITLE"
fi

git push -u origin "$BRANCH"

PR_COMPARE_URL="https://github.com/Tehedor/MLOps_actions/compare/${BASE_BRANCH}...${BRANCH}?expand=1"

if gh auth status >/dev/null 2>&1; then
	gh pr create --base "$BASE_BRANCH" --head "$BRANCH" --title "$PR_TITLE" --body "$PR_BODY"

	# Activa el borrado automático de ramas al hacer merge de PRs en este repositorio.
	REPO="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
	gh api -X PATCH "repos/$REPO" -f delete_branch_on_merge=true >/dev/null
	echo "Configurado: GitHub eliminará automáticamente la rama de la PR al hacer merge."
else
	echo "[WARN] gh no está autenticado."
	echo "[INFO] Crea la PR manualmente aquí: $PR_COMPARE_URL"
	echo "[INFO] Para dejarlo 100% automático en próximas ejecuciones: gh auth login"
fi

git checkout "$BASE_BRANCH"