#!/bin/bash

# Script para disparar workflow y monitorear su ejecución

set -e

TOKEN="$1"
REPO_OWNER="Tehedor"
REPO_NAME="MLOps_actions"
FASE="${2:-fase1}"
VARIANT_ID="${3:-v001}"
PARENT_VARIANT="${4:-}"
PARAMS_JSON="${5:-{}}"

if [[ -z "$TOKEN" ]]; then
  echo "❌ Error: Debes proporcionar el token de GitHub"
  echo "Uso: $0 <TOKEN> [fase1|fase2|...] [variant_id] [parent_variant] [params_json]"
  exit 1
fi

echo "📤 Disparando workflow: fase=$FASE, variant_id=$VARIANT_ID"

# 1. Disparar el workflow
DISPATCH_RESPONSE=$(curl -s -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/dispatches" \
  -d @- <<EOF
{
  "event_type": "ejecutar-fase-api",
  "client_payload": {
    "fase": "$FASE",
    "variant_id": "$VARIANT_ID",
    "parent_variant": "$PARENT_VARIANT",
    "params": $PARAMS_JSON
  }
}
EOF
)

if [[ -z "$DISPATCH_RESPONSE" ]]; then
  echo "✅ Evento disparado exitosamente"
else
  echo "⚠️  Respuesta del servidor: $DISPATCH_RESPONSE"
fi

# 2. Obtener el ID del último workflow run
echo "⏳ Buscando la ejecución del workflow..."
sleep 3

MAX_ATTEMPTS=10
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  RUNS=$(curl -s \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs?event=repository_dispatch&per_page=1" \
    | jq -r '.workflow_runs[0] | "\(.id)|\(.status)|\(.conclusion)"')
  
  RUN_ID=$(echo "$RUNS" | cut -d'|' -f1)
  STATUS=$(echo "$RUNS" | cut -d'|' -f2)
  CONCLUSION=$(echo "$RUNS" | cut -d'|' -f3)
  
  if [[ "$RUN_ID" != "null" && "$RUN_ID" != "" ]]; then
    echo "✅ Workflow encontrado: ID=$RUN_ID"
    break
  fi
  
  ATTEMPT=$((ATTEMPT + 1))
  if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
    echo "⏳ Reintentando en 2 segundos... ($ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
  fi
done

if [[ -z "$RUN_ID" || "$RUN_ID" == "null" ]]; then
  echo "❌ No se pudo encontrar el workflow ejecutándose"
  exit 1
fi

# 3. Monitorear la ejecución
echo ""
echo "🔍 Monitoreando ejecución (ID: $RUN_ID)..."
echo "📊 https://github.com/$REPO_OWNER/$REPO_NAME/actions/runs/$RUN_ID"
echo ""

ATTEMPTS=0
MAX_WAIT=3600  # 1 hora de timeout

while [ $ATTEMPTS -lt $MAX_WAIT ]; do
  RUN_DATA=$(curl -s \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs/$RUN_ID")
  
  STATUS=$(echo "$RUN_DATA" | jq -r '.status')
  CONCLUSION=$(echo "$RUN_DATA" | jq -r '.conclusion')
  
  if [[ "$STATUS" == "completed" ]]; then
    echo ""
    if [[ "$CONCLUSION" == "success" ]]; then
      echo "✅ Workflow completado exitosamente"
      exit 0
    else
      echo "❌ Workflow falló: $CONCLUSION"
      exit 1
    fi
  fi
  
  # Mostrar estado
  case "$STATUS" in
    "queued")
      echo -ne "\r⏳ Estado: En cola (esperando)..."
      ;;
    "in_progress")
      echo -ne "\r🔄 Estado: En ejecución..."
      ;;
    *)
      echo -ne "\r📊 Estado: $STATUS"
      ;;
  esac
  
  sleep 5
  ATTEMPTS=$((ATTEMPTS + 5))
done

echo ""
echo "❌ Timeout: el workflow tardó demasiado (>1 hora)"
exit 1
