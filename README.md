# 🔥 Extintores de Rivero — ERP WMS & Facturación Electrónica

> **Asignatura:** Programación y Redes Virtualizadas (DRY7122)  
> **Evaluación 2:** Solución de Software Profesional y CI/CD  
> **Versión:** 2.0.0 | **API:** SimpleAPI (ChileSystems) — api.simpleapi.cl

---

## 👤 Stakeholder

**Administrador de Operaciones y Logística** de *Extintores de Rivero SpA*, empresa de protección y seguridad contra incendios. Responsable de:

- Registrar en el inventario WMS los extintores que ingresan para recarga o venta.
- Emitir boletas y facturas electrónicas (DTE) verificadas contra el SII.
- Monitorear alertas de vencimiento y stock crítico de clientes.

---

## 💡 Propuesta de Valor (Problema → Solución)

### Problema

La empresa verifica **manualmente** el stock WMS antes de generar documentos de venta, generando duplicidad de tareas y riesgo de vender sin stock real.

### Solución

Este módulo:
1. Consulta datos del receptor directamente desde el SII via SimpleAPI (`/v2/dte/receptor_info`).
2. Genera el DTE firmado y timbrado via SimpleAPI (`/v2/dte/generar_dte`), incluyendo XML válido ante el SII.
3. Alerta de stock y vencimientos de clientes por consola.

---

## 🗂️ Estructura del Repositorio

```
extintores-rivero-app/
├── app.py               # Script principal: SimpleAPI DTE
├── build.sh             # Genera Dockerfile + build + run
├── requirements.txt     # requests==2.31.0
├── .gitignore
├── README.md
└── evidencias/
    ├── docker/
    │   ├── output.txt       # docker ps -a + logs reales
    │   └── screenshot.png   # Captura consola
    └── jenkins/
        ├── stage_view.png
        ├── console_output_build.png
        ├── credentials.png
        └── pipeline_script.txt
```

---

## ⚙️ Variables de Entorno Requeridas

| Variable | Descripción |
|---|---|
| `SIMPLEAPI_TOKEN` | ApiKey de SimpleAPI (panel.simpleapi.cl) |
| `CERT_B64` | Certificado digital en Base64 (archivo .pfx/.p12) |
| `CERT_PASSWORD` | Contraseña del certificado digital |
| `CAF_XML` | Archivo CAF en Base64 (folios descargados del SII) |
| `EMISOR_RUT` | RUT del emisor (Extintores de Rivero SpA) |
| `EMISOR_RAZON` | Razón social del emisor |
| `EMISOR_GIRO` | Giro comercial |
| `EMISOR_DIR` | Dirección del emisor |
| `EMISOR_COMUNA` | Comuna del emisor |
| `EMISOR_CIUDAD` | Ciudad del emisor |
| `ALERT_EMAIL` | Email para alertas operativas (opcional) |

**Configurar en Linux/Bash:**
```bash
export SIMPLEAPI_TOKEN="5593-XXXX-XXXX-XXXX-XXXX"   # Tu ApiKey real
export CERT_B64="$(base64 -w0 tu_certificado.pfx)"
export CERT_PASSWORD="tu_password_cert"
export CAF_XML="$(base64 -w0 tu_caf_33.xml)"
export EMISOR_RUT="76.XXX.XXX-X"
export EMISOR_RAZON="Extintores de Rivero SpA"
export EMISOR_GIRO="Venta y mantención de extintores"
export EMISOR_DIR="Av. Seguridad 1234, Santiago"
export EMISOR_COMUNA="Santiago"
export EMISOR_CIUDAD="Santiago"
```

> ⚠️ **Nunca** escribas credenciales en el código. `.env` está en `.gitignore`.

---

## 🌐 Endpoints SimpleAPI Utilizados

| Endpoint | Método | Descripción |
|---|---|---|
| `/v2/dte/receptor_info` | GET | Consulta razón social, domicilio y correo del receptor en SII |
| `/v2/dte/generar_dte` | POST | Genera XML firmado y timbrado del DTE |

**Autenticación:** Header `Authorization: TU_APIKEY` (sin Bearer).

---

## 🐳 Instrucciones de Ejecución con Docker

```bash
# 1. Dar permisos al script
chmod +x build.sh

# 2. Ejecutar (genera Dockerfile, construye imagen y corre contenedor)
./build.sh

# 3. Verificar que terminó limpiamente
docker ps -a

# 4. Ver logs
docker logs samplerunning
```

---

## 🏗️ CI/CD con Jenkins

### Flujo completo
```
GitHub (push) → SamplePipeline → Preparation → Build → BuildAppJob → Docker → SimpleAPI
```

### BuildAppJob (Freestyle)
- **Source Code Management:** Git — URL del repositorio.
- **Credentials:** Personal Access Token GitHub (Jenkins Credentials Manager).
- **Build Steps → Execute shell:**
```bash
chmod +x build.sh
./build.sh
```

### SamplePipeline (Pipeline Script)
```groovy
node {
    stage ('Preparation') {
        catchError (buildResult: 'SUCCESS') {
            sh 'docker stop samplerunning'
            sh 'docker rm samplerunning'
        }
    }
    stage ('Build') {
        build 'BuildAppJob'
    }
}
```

---

## 🐍 Manejo de Errores (7 tipos)

| # | Tipo | Causa |
|---|---|---|
| 1 | `HTTPError` 401/403 | ApiKey inválida o sin permisos |
| 2 | `HTTPError` 404 | RUT o endpoint no encontrado |
| 3 | `HTTPError` 400 | Payload DTE inválido |
| 4 | `HTTPError` 5xx | Error interno SimpleAPI |
| 5 | `ConnectionError` | Sin conectividad a api.simpleapi.cl |
| 6 | `Timeout` | SimpleAPI no responde en 15s |
| 7 | `ValueError` | Respuesta no es JSON válido |
