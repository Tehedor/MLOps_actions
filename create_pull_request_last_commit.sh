#!/usr/bin/env bash
set -euo pipefail

# Carga variables desde .env si existe (sin imprimir secretos).
if [[ -f .env ]]; then
	# shellcheck disable=SC1091
	set -a
	source .env
	set +a
fi

# Prioriza token explícito para GitHub CLI en modo no interactivo.
if [[ -z "${GH_TOKEN:-}" && -n "${GITHUB_ACTIONS_TOKEN:-}" ]]; then
	export GH_TOKEN="$GITHUB_ACTIONS_TOKEN"
fi
if [[ -z "${GH_TOKEN:-}" && -n "${GITHUB_TOKEN:-}" ]]; then
	export GH_TOKEN="$GITHUB_TOKEN"
fi

BRANCH_PREFIX="feature/fase1-mejoras"
BASE_BRANCH="main"
PR_TITLE="feat: add control file for testing pipeline"
PR_BODY="This PR adds a control file to validate the pipeline flow."
CONTROL_FILE="control_file"

ORIGIN_URL="$(git remote get-url origin)"
if [[ "$ORIGIN_URL" =~ github.com[:/]([^/]+)/([^/.]+)(\.git)?$ ]]; then
	REPO_SLUG="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
else
	echo "[ERROR] No se pudo inferir owner/repo desde origin: $ORIGIN_URL"
	exit 1
fi

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

PR_COMPARE_URL="https://github.com/${REPO_SLUG}/compare/${BASE_BRANCH}...${BRANCH}?expand=1"

if gh pr create --repo "$REPO_SLUG" --base "$BASE_BRANCH" --head "$BRANCH" --title "$PR_TITLE" --body "$PR_BODY"; then

	# Activa el borrado automático de ramas al hacer merge de PRs en este repositorio.
	gh api -X PATCH "repos/$REPO_SLUG" -f delete_branch_on_merge=true >/dev/null
	echo "Configurado: GitHub eliminará automáticamente la rama de la PR al hacer merge."
else
	echo "[WARN] No se pudo crear la PR automáticamente con gh."
	echo "[INFO] Verifica token en .env (GH_TOKEN o GITHUB_ACTIONS_TOKEN) y permisos de PR."
	echo "[INFO] Crea la PR manualmente aquí: $PR_COMPARE_URL"
	echo "[INFO] Alternativa interactiva: gh auth login"
fi

git checkout "$BASE_BRANCH"