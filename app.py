import os
import sys
import json
import requests
from datetime import datetime
from requests.exceptions import ConnectionError, Timeout, HTTPError

# ─────────────────────────────────────────────────────────────
#  EXTINTORES DE RIVERO SpA - MODO DEMO
#  Módulo WMS & Facturación Electrónica — SimpleAPI (ChileSystems)
#  Versión Demo - Sin certificados reales
# ─────────────────────────────────────────────────────────────

EMPRESA       = "Extintores de Rivero Ltda (DEMO)"
VERSION       = "1.0.0-DEMO"
SIMPLEAPI_URL = "https://api.simpleapi.cl"

# URL mock para pruebas locales (opcional)
MOCK_MODE = True  # Cambiar a False para usar API real

def banner():
    print("=" * 60)
    print(f"  {EMPRESA}")
    print(f"  Módulo WMS & Facturación Electrónica v{VERSION}")
    print(f"  Integración: SimpleAPI (api.simpleapi.cl)")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    print("  🧪 MODO DEMO - Simulación sin certificados reales")
    print("=" * 60)

def consultar_rut_receptor(apikey, rut):
    """Versión demo - simula respuesta del SII"""
    if MOCK_MODE:
        print("  [DEMO] Simulando consulta al SII...")
        return {
            "rut": rut,
            "razon_social": "Maderera del Sur Ltda. (DEMO)",
            "domicilio": "Av. Industrial 456, Santiago",
            "comuna": "Pudahuel",
            "correo": "contacto@maderera.cl"
        }
    
    url = f"{SIMPLEAPI_URL}/v2/dte/receptor_info"
    headers = {"Authorization": apikey}
    params = {"rut": rut}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def generar_dte(apikey, payload):
    """Versión demo - simula generación de DTE"""
    if MOCK_MODE:
        print("  [DEMO] Simulando generación de DTE...")
        return {
            "XML": f"""<?xml version="1.0" encoding="UTF-8"?>
<DTE version="1.0">
  <Documento>
    <TipoDTE>33</TipoDTE>
    <Folio>{payload.get('Folio', '1234')}</Folio>
    <FechaEmision>{payload.get('FechaEmision', '2026-05-17')}</FechaEmision>
    <MontoTotal>{payload.get('Totales', {}).get('MntTotal', 0)}</MontoTotal>
  </Documento>
</DTE>""",
            "PDF": "BASE64_SIMULADO_PDF_CONTENT",
            "TED": "TIMBRE_ELECTRONICO_SIMULADO",
            "Folio": payload.get('Folio', 1234)
        }
    
    url = f"{SIMPLEAPI_URL}/v2/dte/generar_dte"
    headers = {"Authorization": apikey, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()

def main():
    banner()

    # ── 1. Configuración DEMO ──
    # En modo demo, usamos valores predeterminados
    apikey = os.getenv("SIMPLEAPI_TOKEN", "DEMO_TOKEN_12345")
    
    # Datos demo del emisor
    emisor_rut = "76.123.456-7"
    emisor_razon = "Extintores de Rivero SpA"
    emisor_giro = "Venta y mantención de extintores"
    emisor_dir = "Av. Seguridad 1234, Santiago"
    emisor_comuna = "Santiago"
    emisor_ciudad = "Santiago"
    
    alert_email = os.getenv("ALERT_EMAIL", "contacto@derivero.cl")

    if not MOCK_MODE:
        # Validar variables solo en modo real
        cert_b64 = os.getenv("CERT_B64")
        cert_password = os.getenv("CERT_PASSWORD")
        caf_xml = os.getenv("CAF_XML")
        
        faltantes = []
        if not apikey or apikey == "DEMO_TOKEN_12345": faltantes.append("SIMPLEAPI_TOKEN")
        if not cert_b64: faltantes.append("CERT_B64")
        if not cert_password: faltantes.append("CERT_PASSWORD")
        if not caf_xml: faltantes.append("CAF_XML")

        if faltantes:
            print("\n[ERROR CRITICO] Faltan variables de entorno:")
            for v in faltantes:
                print(f"  - {v}")
            print("\nO use MOCK_MODE = True para demo")
            sys.exit(1)

    print(f"\n[INFO] API Key cargada : {apikey[:4]}...{apikey[-4:] if len(apikey) > 8 else '(demo)'}")
    print(f"[INFO] Emisor          : {emisor_razon} | RUT {emisor_rut}")
    print(f"[INFO] Notificaciones  : {alert_email}")

    # ── 2. Consultar receptor ───────────────────────────
    RUT_RECEPTOR = "76.534.890-2"
    print(f"\n[1/3] Consultando RUT receptor {RUT_RECEPTOR} en SII...")

    try:
        receptor = consultar_rut_receptor(apikey, RUT_RECEPTOR)

        razon_receptor  = receptor.get("razon_social", "DESCONOCIDO")
        dir_receptor    = receptor.get("domicilio",    "Sin direccion")
        correo_receptor = receptor.get("correo",       "sin-correo@sii.cl")
        comuna_rec      = receptor.get("comuna",       "")

        print(f"\n  DATOS RECEPTOR (SII)")
        print(f"  RUT          : {RUT_RECEPTOR}")
        print(f"  Razon Social : {razon_receptor}")
        print(f"  Domicilio    : {dir_receptor}")
        print(f"  Comuna       : {comuna_rec}")
        print(f"  Correo SII   : {correo_receptor}")

    except Exception as e:
        print(f"[ERROR] Fallo consulta: {e}, usando datos demo")
        razon_receptor  = "Maderera del Sur Ltda."
        dir_receptor    = "Av. Industrial 456, Santiago"
        correo_receptor = "contacto@maderera.cl"
        comuna_rec      = "Pudahuel"

    # ── 3. Construir payload DTE ─────────────────────────
    PRODUCTO_ID   = "EXT-PQS-6KG-001"
    TIPO_EXTINTOR = "PQS"
    CANTIDAD      = 3
    PRECIO_NETO   = 42000
    folio         = 2847

    neto_total = PRECIO_NETO * CANTIDAD
    iva        = round(neto_total * 0.19)
    total      = neto_total + iva

    print(f"\n[2/3] Preparando DTE Factura Electronica (tipo 33)")
    print(f"  Tipo DTE   : Factura Electronica (33)")
    print(f"  Folio      : #{folio}")
    print(f"  Emisor     : {emisor_razon} | {emisor_rut}")
    print(f"  Receptor   : {razon_receptor} | {RUT_RECEPTOR}")
    print(f"  Producto   : Extintor {TIPO_EXTINTOR} 6KG x {CANTIDAD} un.")
    print(f"  ID WMS     : {PRODUCTO_ID}")
    print(f"  Neto       : ${neto_total:,} CLP")
    print(f"  IVA (19%)  : ${iva:,} CLP")
    print(f"  TOTAL      : ${total:,} CLP")

    payload = {
        "Certificado": "DEMO_CERT_BASE64",
        "CertPass":    "demo_password",
        "CAF":         "DEMO_CAF_XML",
        "TipoDTE":     33,
        "Folio":       folio,
        "FechaEmision": datetime.now().strftime("%Y-%m-%d"),
        "Emisor": {
            "RUTEmisor":    emisor_rut,
            "RznSoc":       emisor_razon,
            "GiroEmis":     emisor_giro,
            "DirOrigen":    emisor_dir,
            "CmnaOrigen":   emisor_comuna,
            "CiudadOrigen": emisor_ciudad
        },
        "Receptor": {
            "RUTRecep":    RUT_RECEPTOR,
            "RznSocRecep": razon_receptor,
            "DirRecep":    dir_receptor,
            "CmnaRecep":   comuna_rec,
            "CorreoRecep": correo_receptor
        },
        "Detalle": [
            {
                "NmbItem":   f"Extintor {TIPO_EXTINTOR} 6KG",
                "DscItem":   f"ID WMS: {PRODUCTO_ID} | Proteccion y Seguridad",
                "QtyItem":   CANTIDAD,
                "PrcItem":   PRECIO_NETO,
                "MontoItem": neto_total
            }
        ],
        "Totales": {
            "MntNeto":  neto_total,
            "TasaIVA":  19,
            "IVA":      iva,
            "MntTotal": total
        }
    }

    # ── 4. Generar DTE ─────────────────────────────────────
    print("\n[3/3] Enviando solicitud a SimpleAPI...")

    try:
        resultado = generar_dte(apikey, payload)

        xml_dte   = resultado.get("XML",   "")
        pdf_b64   = resultado.get("PDF",   "")
        ted       = resultado.get("TED",   "")
        folio_res = resultado.get("Folio", folio)

        print("\n  RESPUESTA SIMPLEAPI")
        print(f"  Estado       : DTE generado exitosamente OK")
        print(f"  Folio DTE    : #{folio_res}")
        print(f"  XML generado : {'Si (' + str(len(xml_dte)) + ' chars)' if xml_dte else 'No disponible'}")
        print(f"  PDF generado : {'Si (base64)' if pdf_b64 else 'No disponible'}")
        print(f"  TED (timbre) : {'Presente' if ted else 'No disponible'}")

        if xml_dte:
            fname = f"dte_factura_{folio_res}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(xml_dte)
            print(f"\n[OK] XML guardado en: {fname}")
            print(f"[INFO] Proximo paso: enviar XML al SII dentro de 12 horas.")
            print(f"[INFO] Notificacion al receptor: {correo_receptor}")

        print(f"\n[OK] DTE procesado correctamente — {EMPRESA}")

    except Exception as e:
        print(f"[ERROR] Fallo al generar DTE: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"  Proceso completado exitosamente.")
    print("=" * 60)

if __name__ == "__main__":
    main()

