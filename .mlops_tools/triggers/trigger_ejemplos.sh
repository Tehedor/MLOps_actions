#!/bin/bash

# Ejemplos de cómo disparar el workflow con curl y monitorear la ejecución

set -e

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️  CONFIGURACIÓN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOKEN="${GITHUB_TOKEN}"
REPO_OWNER="Tehedor"
REPO_NAME="MLOps_actions"
GITHUB_API="https://api.github.com"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📝 FUNCIÓN: Disparar fase
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

trigger_fase() {
    local FASE="$1"
    local VARIANT_ID="$2"
    local PARENT_VARIANT="$3"
    local PARAMS_JSON="$4"
    
    echo ""
    echo "📤 Disparando fase: $FASE"
    echo "   Variante: $VARIANT_ID"
    echo "   Parent: ${PARENT_VARIANT:-ninguno}"
    
    curl -s -X POST \
      -H "Accept: application/vnd.github.v3+json" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "$GITHUB_API/repos/$REPO_OWNER/$REPO_NAME/dispatches" \
      -d @- <<EOF | jq '.'
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
    
    echo "✅ Evento enviado"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 FUNCIÓN: Monitorear ejecución
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

monitor_workflow() {
    echo ""
    echo "⏳ Buscando workflow..."
    sleep 3
    
    # Obtener el último run
    RUN_DATA=$(curl -s \
      -H "Accept: application/vnd.github.v3+json" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "$GITHUB_API/repos/$REPO_OWNER/$REPO_NAME/actions/runs?event=repository_dispatch&per_page=1")
    
    RUN_ID=$(echo "$RUN_DATA" | jq -r '.workflow_runs[0].id')
    RUN_NAME=$(echo "$RUN_DATA" | jq -r '.workflow_runs[0].name')
    
    if [[ "$RUN_ID" == "null" || -z "$RUN_ID" ]]; then
        echo "❌ No se encontró workflow"
        return 1
    fi
    
    echo "✅ Workflow encontrado:"
    echo "   ID: $RUN_ID"
    echo "   Nombre: $RUN_NAME"
    echo "   Link: https://github.com/$REPO_OWNER/$REPO_NAME/actions/runs/$RUN_ID"
    echo ""
    
    # Monitorear estado
    echo "🔍 Monitoreando ejecución..."
    local ATTEMPTS=0
    local MAX_ATTEMPTS=720  # 1 hora (5 seg * 720)
    
    while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
        RUN_DATA=$(curl -s \
          -H "Accept: application/vnd.github.v3+json" \
          -H "Authorization: Bearer $TOKEN" \
          -H "X-GitHub-Api-Version: 2022-11-28" \
          "$GITHUB_API/repos/$REPO_OWNER/$REPO_NAME/actions/runs/$RUN_ID")
        
        STATUS=$(echo "$RUN_DATA" | jq -r '.status')
        CONCLUSION=$(echo "$RUN_DATA" | jq -r '.conclusion')
        CREATED_AT=$(echo "$RUN_DATA" | jq -r '.created_at')
        UPDATED_AT=$(echo "$RUN_DATA" | jq -r '.updated_at')
        
        # Mostrar estado actual
        case "$STATUS" in
            "completed")
                echo ""
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                if [[ "$CONCLUSION" == "success" ]]; then
                    echo "✅ WORKFLOW COMPLETADO EXITOSAMENTE"
                else
                    echo "❌ WORKFLOW FALLIDO: $CONCLUSION"
                fi
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Conclusión: $CONCLUSION"
                echo "Comenzó: $CREATED_AT"
                echo "Finalizó: $UPDATED_AT"
                return 0
                ;;
            "queued")
                echo -ne "\r⏳ En cola... [$ATTEMPTS/$MAX_ATTEMPTS]"
                ;;
            "in_progress")
                echo -ne "\r🔄 En ejecución... [$ATTEMPTS/$MAX_ATTEMPTS]"
                ;;
            *)
                echo -ne "\r📊 Estado: $STATUS [$ATTEMPTS/$MAX_ATTEMPTS]"
                ;;
        esac
        
        sleep 5
        ATTEMPTS=$((ATTEMPTS + 1))
    done
    
    echo ""
    echo "❌ Timeout: el workflow tardó más de 1 hora"
    return 1
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 MENÚ DE EJEMPLOS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

case "${1:-menu}" in
    # Fase 1: Exploración
    fase1)
        trigger_fase \
            "fase1" \
            "v001" \
            "" \
            '{"RAW": "./data/raw.csv", "CLEANING_STRATEGY": "basic", "NAN_VALUES": "[-999999]"}'
        monitor_workflow
        ;;
    
    # Fase 2: Preparación de eventos
    fase2)
        trigger_fase \
            "fase2" \
            "v011" \
            "v001" \
            '{"BANDS": "20 60 80", "STRATEGY": "transitions", "NAN": "discard"}'
        monitor_workflow
        ;;
    
    # Fase 3: Windows dataset
    fase3)
        trigger_fase \
            "fase3" \
            "v111" \
            "v011" \
            '{"OW": "600", "LT": "300", "PW": "600", "WS": "synchro", "NAN": "discard"}'
        monitor_workflow
        ;;
    
    # Fase 4: Target engineering
    fase4)
        trigger_fase \
            "fase4" \
            "v201" \
            "v111" \
            '{"PREDICTION_NAME": "molamas", "OBJECTIVE": "{operator: OR, events: [Battery_Active_Power_0_20-to-80_100, Battery_Active_Power_20_60-to-80_100, Battery_Active_Power_60_80-to-80_100]}"}'
        monitor_workflow
        ;;
    
    # Fase 5: Modelado
    fase5)
        trigger_fase \
            "fase5" \
            "v301" \
            "v201" \
            '{"MODEL_FAMILY": "dense_bow", "IMBALANCE_STRATEGY": "rare_events", "IMBALANCE_MAX_MAJ": "20000"}'
        monitor_workflow
        ;;
    
    # Ejecutar todas las fases secuencialmente
    todas)
        echo "🔄 EJECUTANDO TODAS LAS FASES SECUENCIALMENTE"
        for FASE in fase1 fase2 fase3 fase4 fase5; do
            echo ""
            echo "▶️  Disparando $FASE..."
            $0 "$FASE" || break
            echo "✅ $FASE completada"
            echo "⏳ Esperando 5 segundos antes de la siguiente..."
            sleep 5
        done
        echo ""
        echo "🎉 TODAS LAS FASES COMPLETADAS"
        ;;
    
    *)
        echo ""
        echo "╔════════════════════════════════════════════════════╗"
        echo "║        MLOps Workflow - Ejemplos de uso            ║"
        echo "╚════════════════════════════════════════════════════╝"
        echo ""
        echo "Uso: $0 [COMANDO]"
        echo ""
        echo "Comandos disponibles:"
        echo "  fase1      - Ejecutar Fase 1: Exploración y limpieza"
        echo "  fase2      - Ejecutar Fase 2: Preparación de eventos"
        echo "  fase3      - Ejecutar Fase 3: Windows dataset"
        echo "  fase4      - Ejecutar Fase 4: Target engineering"
        echo "  fase5      - Ejecutar Fase 5: Modelado"
        echo "  todas      - Ejecutar todas las fases secuencialmente"
        echo ""
        echo "Ejemplos:"
        echo "  $0 fase1"
        echo "  $0 todas"
        echo ""
        echo "Variables de entorno:"
        echo "  GITHUB_TOKEN  - Token de GitHub (default: env var)"
        echo ""
esac
