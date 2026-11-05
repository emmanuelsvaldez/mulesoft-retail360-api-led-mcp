#!/usr/bin/env python3
"""
==============================================================================
Retail 360 - Enterprise Model Context Protocol (MCP) Server
Bridge between Hermes Agent / Ollama and MuleSoft Experience API (:8081)
==============================================================================
"""

import sys
import json
import urllib.request
import urllib.error

EXP_API_BASE_URL = "http://localhost:8081/api/v1"

def _http_request(method: str, path: str, payload=None, headers=None):
    url = f"{EXP_API_BASE_URL}{path}"
    req_headers = {
        "User-Agent": "HermesAgent-MCP-Bridge/1.0",
        "X-Correlation-ID": f"corr-mcp-hermes-{int(sys.version_info[0])}"
    }
    if headers:
        req_headers.update(headers)

    data = None
    if payload is not None:
        req_headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8")
            status = response.status
            try:
                parsed = json.loads(content)
                return {"status": status, "data": parsed}
            except Exception:
                return {"status": status, "raw": content}
    except urllib.error.HTTPError as e:
        err_content = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_content)
            return {"status": e.code, "error": parsed}
        except Exception:
            return {"status": e.code, "error": err_content}
    except Exception as ex:
        return {"status": 500, "error": str(ex)}

# MCP Tool Handlers
def consultar_producto(sku: str) -> dict:
    """Consulta el catalogo de productos y stock en PostgreSQL a traves de MuleSoft."""
    return _http_request("GET", f"/products/{sku}")

def crear_pedido(order_id: str, customer_id: str, customer_name: str, customer_email: str, items: list) -> dict:
    """Crea una orden en MuleSoft orquestando PostgreSQL transaccional y Salesforce CRM."""
    payload = {
        "orderId": order_id,
        "customer": {
            "customerId": customer_id,
            "name": customer_name,
            "email": customer_email
        },
        "items": items
    }
    return _http_request("POST", "/orders", payload=payload)

def consultar_pedido(order_id: str) -> dict:
    """Consulta una orden por ID incluyendo su estado de sincronizacion con Salesforce."""
    return _http_request("GET", f"/orders/{order_id}")

def obtener_reporte_ordenes() -> dict:
    """Obtiene el reporte consolidado de ordenes en formato CSV."""
    return _http_request("GET", "/orders/report", headers={"Accept": "text/csv"})

TOOLS_METADATA = [
    {
        "name": "consultar_producto",
        "description": "Consulta un producto por su SKU (ej. LAP-001, MOU-001, CAM-001). Devuelve precio, stock y estado activo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku": {"type": "string", "description": "Codigo SKU del producto a consultar"}
            },
            "required": ["sku"]
        }
    },
    {
        "name": "crear_pedido",
        "description": "Crea una nueva orden de compra en Retail 360, descontando inventario y sincronizando con Salesforce.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Identificador unico de la orden (ej. ORD-2001)"},
                "customer_id": {"type": "string", "description": "Identificador del cliente"},
                "customer_name": {"type": "string", "description": "Nombre completo del cliente"},
                "customer_email": {"type": "string", "description": "Correo electronico del cliente"},
                "items": {
                    "type": "array",
                    "description": "Lista de articulos con sku y quantity",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sku": {"type": "string"},
                            "quantity": {"type": "integer"}
                        },
                        "required": ["sku", "quantity"]
                    }
                }
            },
            "required": ["order_id", "customer_id", "customer_name", "customer_email", "items"]
        }
    },
    {
        "name": "consultar_pedido",
        "description": "Consulta el estado actual de una orden por su identificador (ej. ORD-1001), incluyendo su syncStatus con Salesforce.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Identificador de la orden a consultar"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "obtener_reporte_ordenes",
        "description": "Genera el reporte consolidado de pedidos y lineas en formato CSV exportable.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

def main():
    """Bucle stdio JSON-RPC compatible con el estandar Model Context Protocol (MCP)."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line.strip())
            req_id = request.get("id")
            method = request.get("method")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "retail360-mulesoft-mcp-server", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS_METADATA}
                }
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})

                if name == "consultar_producto":
                    result = consultar_producto(args.get("sku", ""))
                elif name == "crear_pedido":
                    result = crear_pedido(
                        order_id=args.get("order_id", ""),
                        customer_id=args.get("customer_id", ""),
                        customer_name=args.get("customer_name", ""),
                        customer_email=args.get("customer_email", ""),
                        items=args.get("items", [])
                    )
                elif name == "consultar_pedido":
                    result = consultar_pedido(args.get("order_id", ""))
                elif name == "obtener_reporte_ordenes":
                    result = obtener_reporte_ordenes()
                else:
                    result = {"error": f"Herramienta desconocida: {name}"}

                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}
                        ]
                    }
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()

