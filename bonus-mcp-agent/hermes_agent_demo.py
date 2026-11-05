#!/usr/bin/env python3
"""
==============================================================================
Simulador & Conector Hermes Agent + Ollama (gemma4:e4b) -> MuleSoft Retail 360
==============================================================================
Demuestra cómo el modelo local gemma4:e4b en Ollama / Hermes Agent razona e
invoca las herramientas MCP expuestas por MuleSoft Experience API (:8081/:8085):
1. consultar_producto (LAP-001)
2. crear_pedido (ORD-HERMES-01) -> PostgreSQL + Salesforce CRM
3. consultar_pedido (ORD-HERMES-01)
==============================================================================
"""

import json
import urllib.request
from retail360_mcp_server import (
    consultar_producto,
    crear_pedido,
    consultar_pedido,
    obtener_reporte_ordenes
)

OLLAMA_MODEL = "gemma4:e4b"
OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_ollama_gemma(prompt: str) -> str:
    """Envía un prompt al modelo local gemma4:e4b en Ollama si está activo."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception:
        return "[Ollama gemma4:e4b listo para conexión desde Dashboard de Hermes Agent]"

def main():
    print("=" * 75)
    print(f"  HERMES AGENT + OLLAMA ({OLLAMA_MODEL}) -> MULESOFT 4 MCP SERVER")
    print("=" * 75)

    # Paso 1: Consulta de inventario
    print("\n[Paso 1: Tool Call -> 'consultar_producto' (SKU: LAP-001)]")
    res_prod = consultar_producto("LAP-001")
    print(f"<- Respuesta MuleSoft (:8081):\n{json.dumps(res_prod, indent=2, ensure_ascii=False)}")

    # Paso 2: Creación de orden por el Agente
    order_id = "ORD-HERMES-01"
    print(f"\n[Paso 2: Tool Call -> 'crear_pedido' ({order_id})]")
    items = [{"sku": "LAP-001", "quantity": 1}, {"sku": "MOU-001", "quantity": 2}]
    res_order = crear_pedido(
        order_id=order_id,
        customer_id="CUST-AI-01",
        customer_name="Emmanuel Sanchez (Hermes Agent)",
        customer_email="emmanuel.sanchez@skala.io",
        items=items
    )
    print(f"<- Respuesta MuleSoft (:8081):\n{json.dumps(res_order, indent=2, ensure_ascii=False)}")

    # Paso 3: Verificación de sincronización en Salesforce
    print(f"\n[Paso 3: Tool Call -> 'consultar_pedido' ({order_id})]")
    res_get = consultar_pedido(order_id)
    print(f"<- Respuesta MuleSoft (:8081):\n{json.dumps(res_get, indent=2, ensure_ascii=False)}")

    # Paso 4: Síntesis con gemma4:e4b
    print(f"\n[Paso 4: Síntesis en Lenguaje Natural con Ollama ({OLLAMA_MODEL})]")
    summary_prompt = (
        f"Eres Hermes Agent conectado a MuleSoft Retail 360. "
        f"Acabas de crear el pedido {order_id} con resultado: {json.dumps(res_order)}. "
        f"Responde en español en 2 líneas confirmando el total y el estado de sincronización con Salesforce."
    )
    ai_reply = ask_ollama_gemma(summary_prompt)
    print(f"🤖 Hermes Agent ({OLLAMA_MODEL}): {ai_reply}")

    print("\n" + "=" * 75)
    print("  FLUJO AGENTICO MULESOFT + SALESFORCE + POSTGRESQL COMPLETADO")
    print("=" * 75)

if __name__ == "__main__":
    main()
