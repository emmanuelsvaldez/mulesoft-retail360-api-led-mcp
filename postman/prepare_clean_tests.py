#!/usr/bin/env python3
"""
==============================================================================
Retail 360 - Utilidad de Preparación y Reposición de Entorno (PostgreSQL + SF)
==============================================================================
Modos de uso:
  1. Reposición Selectiva (Recomendado: restaura stock inicial y libera solo
     ORD-1001 y ORD-1009-CONTINGENCY para que Postman CA-01..CA-12 corra en
     verde sin borrar tus órdenes de Hermes):
     python postman/prepare_clean_tests.py --mode selective

  2. Limpieza Total (Reinicia PostgreSQL con init.sql y borra todas las
     órdenes de prueba en Salesforce CRM para empezar desde cero):
     python postman/prepare_clean_tests.py --mode full
==============================================================================
"""

import argparse
import json
import os
import subprocess
import urllib.parse
import urllib.request

TOKEN_URL = os.environ.get("SFDC_TOKEN_URL", "https://your-domain.develop.my.salesforce.com/services/oauth2/token")
CLIENT_ID = os.environ.get("SFDC_CLIENT_ID", "YOUR_SFDC_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SFDC_CLIENT_SECRET", "YOUR_SFDC_CLIENT_SECRET")
CONTAINER = "retail360-postgres"


def run_psql(sql: str):
    res = subprocess.run(
        ["docker", "exec", "-i", CONTAINER, "psql", "-U", "postgres", "-d", "retail360", "-c", sql],
        capture_output=True, text=True
    )
    if res.returncode != 0:
        print(f"[ERROR PSQL] {res.stderr}")
    else:
        print(res.stdout.strip())


def get_sf_auth():
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }).encode("utf-8")
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        tok = json.loads(resp.read().decode("utf-8"))
    return tok["access_token"], tok["instance_url"]


def delete_sf_orders(ext_ids=None):
    access_token, instance_url = get_sf_auth()
    where_clause = ""
    if ext_ids:
        quoted = ", ".join(f"'{x}'" for x in ext_ids)
        where_clause = f" WHERE External_Order_Id__c IN ({quoted})"

    soql = f"SELECT Id, External_Order_Id__c FROM Retail_Order__c{where_clause}"
    q_url = f"{instance_url}/services/data/v60.0/query?q={urllib.parse.quote(soql)}"
    req = urllib.request.Request(q_url, headers={"Authorization": f"Bearer {access_token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        records = json.loads(resp.read().decode("utf-8")).get("records", [])

    if not records:
        print("[Salesforce] No hay registros que eliminar para el filtro indicado.")
        return

    for rec in records:
        sf_id = rec["Id"]
        ext_id = rec.get("External_Order_Id__c")
        # Eliminar primero líneas hijas por seguridad si es Lookup
        soql_items = f"SELECT Id FROM Retail_Order_Item__c WHERE Order__c = '{sf_id}'"
        qi_url = f"{instance_url}/services/data/v60.0/query?q={urllib.parse.quote(soql_items)}"
        qi_req = urllib.request.Request(qi_url, headers={"Authorization": f"Bearer {access_token}"})
        with urllib.request.urlopen(qi_req, timeout=15) as qi_resp:
            items = json.loads(qi_resp.read().decode("utf-8")).get("records", [])
        for item in items:
            del_item_url = f"{instance_url}/services/data/v60.0/sobjects/Retail_Order_Item__c/{item['Id']}"
            d_req = urllib.request.Request(del_item_url, headers={"Authorization": f"Bearer {access_token}"}, method="DELETE")
            urllib.request.urlopen(d_req, timeout=15).close()

        del_url = f"{instance_url}/services/data/v60.0/sobjects/Retail_Order__c/{sf_id}"
        d_req = urllib.request.Request(del_url, headers={"Authorization": f"Bearer {access_token}"}, method="DELETE")
        urllib.request.urlopen(d_req, timeout=15).close()
        print(f"[Salesforce] Eliminada orden {ext_id} ({sf_id}) y {len(items)} líneas.")


def main():
    parser = argparse.ArgumentParser(description="Repone el entorno Retail 360 para pruebas de entrega.")
    parser.add_argument("--mode", choices=["selective", "full"], default="selective")
    args = parser.parse_args()

    if args.mode == "selective":
        print("=== MODO SELECTIVO: Restaurando stock oficial y liberando ORD-1001 / ORD-1009-CONTINGENCY ===")
        sql = """
        UPDATE products SET stock = 12, active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'LAP-001';
        UPDATE products SET stock = 30, active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'MOU-001';
        UPDATE products SET stock = 15, active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'CAM-001';
        UPDATE products SET stock = 0,  active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'MON-001';
        UPDATE products SET stock = 10, active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'KEY-001';
        DELETE FROM retail_orders WHERE order_id IN ('ORD-1001', 'ORD-1009-CONTINGENCY');
        """
        run_psql(sql)
        delete_sf_orders(["ORD-1001", "ORD-1009-CONTINGENCY"])
    else:
        print("=== MODO FULL: Limpiando todas las órdenes en PostgreSQL y Salesforce, y restaurando stock semilla ===")
        sql = """
        TRUNCATE TABLE retail_order_items, retail_orders RESTART IDENTITY CASCADE;
        UPDATE products SET stock = 12, active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'LAP-001';
        UPDATE products SET stock = 30, active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'MOU-001';
        UPDATE products SET stock = 15, active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'CAM-001';
        UPDATE products SET stock = 0,  active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'MON-001';
        UPDATE products SET stock = 10, active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE sku = 'KEY-001';
        """
        run_psql(sql)
        delete_sf_orders(None)

    print("\n=== VERIFICACIÓN DE INVENTARIO REPUESTO EN POSTGRESQL ===")
    run_psql("SELECT sku, product_name, unit_price, stock, active FROM products ORDER BY sku;")
    print("\n=== VERIFICACIÓN DE ÓRDENES EN POSTGRESQL ===")
    run_psql("SELECT order_id, customer_id, status, sync_status, total, salesforce_id FROM retail_orders ORDER BY created_at ASC;")


if __name__ == "__main__":
    main()

