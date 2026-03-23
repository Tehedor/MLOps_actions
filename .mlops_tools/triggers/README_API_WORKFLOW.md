# Disparar Workflow desde API REST

Este documento explica cómo disparar los workflows de MLOps desde la API de GitHub y monitorear su ejecución en tiempo real.

## 📌 Problema: HTTP 204 No Content

Cuando disparas un `repository_dispatch`, GitHub responde con **HTTP 204 No Content** porque:
- Es un evento **asíncrono**
- La API no espera a que el workflow termine
- Solo registra el evento y devuelve la respuesta inmediatamente

## ✅ Solución: Script de Monitoreo

### Paso 1: Usar el script `trigger_workflow.sh`

El script está en `scripts/trigger_workflow.sh` y hace:
1. ✅ **Recibido**: Dispara el evento y confirma
2. 🔄 **En ejecución**: Busca y monitorea el workflow
3. ✅ **Completado**: Reporta el resultado final

### Uso:

```bash
# Forma básica
./scripts/trigger_workflow.sh <TOKEN>

# Con más controles
./scripts/trigger_workflow.sh <TOKEN> fase1 v001

# Ejemplo completo
./scripts/trigger_workflow.sh "github_****" fase2 v011 v001
```

### Parámetros:

| Parámetro | Obligatorio | Descripción |
|-----------|-------------|-------------|
| `TOKEN` | ✅ Sí | Token de GitHub (fine-grained) |
| `FASE` | ❌ No | fase1, fase2, fase3, fase4, fase5 (default: fase1) |
| `VARIANT_ID` | ❌ No | ID de la variante (default: v001) |
| `PARENT_VARIANT` | ❌ No | ID del parent (default: vacío) |
| `PARAMS_JSON` | ❌ No | JSON con parámetros (default: {}) |

### Ejemplo interactivo:

```bash
# Fase 1
./scripts/trigger_workflow.sh "$TOKEN" fase1 v001 "" '{"RAW": "./data/raw.csv", "CLEANING_STRATEGY": "basic", "NAN_VALUES": "[-999999]"}'

# Fase 2
./scripts/trigger_workflow.sh "$TOKEN" fase2 v011 v001 '{"BANDS": "20 60 80", "STRATEGY": "transitions", "NAN": "discard"}'

# Fase 3
./scripts/trigger_workflow.sh "$TOKEN" fase3 v111 v011 '{"OW": "600", "LT": "300", "PW": "600", "WS": "synchro", "NAN": "discard"}'
```

## 🎯 Salida esperada

### Inicio ✅
```
📤 Disparando workflow: fase=fase1, variant_id=v001
✅ Evento disparado exitosamente
⏳ Buscando la ejecución del workflow...
✅ Workflow encontrado: ID=12345678
```

### Monitoreo 🔄
```
🔍 Monitoreando ejecución (ID: 12345678)...
📊 https://github.com/Tehedor/MLOps_actions/actions/runs/12345678

⏳ Estado: En cola (esperando)...
🔄 Estado: En ejecución...
```

### Completado ✅
```
✅ Workflow completado exitosamente
```

## 📡 Opción 2: Usar Webhooks (Avanzado)

Si quieres notificaciones en tiempo real a tu servidor, configura un webhook:

1. Ve a: Repo Settings → Webhooks
2. Selecciona eventos: `Workflow runs`
3. Tu servidor recibirá notificaciones cuando cambie el estado del workflow

Payload de ejemplo:
```json
{
  "action": "completed",
  "workflow_run": {
    "id": 12345678,
    "status": "completed",
    "conclusion": "success",
    "name": "MLOps Pipeline - Ejecutar por API"
  }
}
```

## 🔐 Tokens Seguros

**⚠️ IMPORTANTE**: Tu token está expuesto en el archivo `.http`. 

Mejores prácticas:
1. **Guardar en variables de entorno**:
   ```bash
   export GITHUB_TOKEN="github_pat_..."
   ./scripts/trigger_workflow.sh "$GITHUB_TOKEN" fase1
   ```

2. **Guardar en `.env` (no comitear)**:
   ```
   GITHUB_TOKEN=github_pat_...
   ```

3. **Usar credenciales de GitHub CLI**:
   ```bash
   gh auth login
   ./scripts/trigger_workflow.sh "$(gh auth token)" fase1
   ```

## 📋 Resumen de estados del workflow

| Estado | Significado |
|--------|------------|
| `queued` | En cola, esperando ejecutor |
| `in_progress` | Ejecutándose |
| `completed` | Terminado |

| Conclusión | Significado |
|-----------|------------|
| `success` | ✅ Completado sin errores |
| `failure` | ❌ Error durante ejecución |
| `neutral` | ⚪ Completado sin éxito ni fallo |
| `cancelled` | ⛔ Cancelado manualmente |
| `skipped` | ⏭️ Saltado (condiciones no se cumplieron) |
| `action_required` | ⚠️ Requiere acción manual |

## 🛠️ Crear un alias bash

Para facilitar el uso:

```bash
# Agregar a ~/.bashrc o ~/.zshrc
alias trigger-mlops='~/Work/tfm/github_actions/MLOps_actions/scripts/trigger_workflow.sh'

# Uso:
trigger-mlops "$GITHUB_TOKEN" fase1
```

## 📝 Logs en el Workflow

El workflow ahora muestra:
1. **Inicio**: Fase recibida, parámetros
2. **Ejecución**: Qué fase se está corriendo, parámetros actuales
3. **Final**: Éxito o error, marca de tiempo

Ver logs en: https://github.com/Tehedor/MLOps_actions/actions
