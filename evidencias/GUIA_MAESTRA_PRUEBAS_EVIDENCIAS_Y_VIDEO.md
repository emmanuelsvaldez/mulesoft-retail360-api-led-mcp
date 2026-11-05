# 🎬 Guión Maestro de Pruebas, Metodología de Fotos Independientes y Grabación de Video — Retail 360

> **Proyecto Integrador Final · Skala MuleSoft 4 + Agentic AI**  
> **Autor:** Emmanuel Sánchez  
> **Propósito:** Ejecutar la corrida final limpia de los casos `CA-01` a `CA-12` + `Bonus Agentic AI`, capturando fotografías independientes de **Petición/Respuesta**, **Reflejo en Base de Datos (PostgreSQL)**, **Reflejo en Aplicación (Consola Anypoint Studio)** y **Reflejo en CRM (Salesforce)**, además del guión de grabación en video del Agente IA.

---

## 🔍 1. Diagnóstico Actual de PostgreSQL y Salesforce (Antes de Reponer)

### 1.1 Estado Actual del Inventario en PostgreSQL (`retail360-postgres`)
| SKU | Producto | Precio Unitario | Stock Actual | Stock Semilla Oficial | Activo | Diagnóstico para Pruebas |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`LAP-001`** | Laptop 14 pulgadas | `$18,000.00` | 🔴 **`0`** | **`12`** | `true` | **Requiere reposición:** Agotado por las 8 órdenes previas. Sin reponer, `CA-02` fallará con `409 INSUFFICIENT_STOCK`. |
| **`MOU-001`** | Mouse Inalambrico Pro | `$350.00` | 🟡 `11` | **`30`** | `true` | **Requiere reposición a 30** para cuadrar exactamente con las evidencias de `CA-02`. |
| **`CAM-001`** | Webcam Full HD 1080p | `$950.00` | 🟡 `13` | **`15`** | `true` | **Requiere reposición a 15** para `CA-09`. |
| **`MON-001`** | Monitor 27 pulgadas 4K | `$6,500.00` | 🟢 `0` | **`0`** | `true` | Correcto (debe permanecer en `0` para probar `CA-07` Stock Insuficiente). |
| **`KEY-001`** | Teclado Mecanico Legacy | `$1,200.00` | 🟢 `10` | **`10`** | `false` | Correcto (producto inactivo para validar `RF-03`). |

### 1.2 Órdenes Actualmente Registradas y Sincronizadas (PostgreSQL ↔ Salesforce CRM)
Actualmente existen **11 órdenes** y **18 líneas de detalle** sincronizadas 1 a 1 entre PostgreSQL y Salesforce:

| # | `order_id` (PostgreSQL) | `External_Order_Id__c` (Salesforce) | `salesforce_id` (`Retail_Order__c`) | Cliente | Total (MXN) | Estado Sync | Impacto en Corrida de Pruebas |
| :-: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 1 | **`ORD-1001`** | **`ORD-1001`** | `a00bm00003My3KzAAJ` | `CUST-001` (Juan Perez) | `$37,050.00` | `SYNCED` | ⚠️ **Colisiona con `CA-02`** (daría `409 ORDER_ALREADY_EXISTS` si no se limpia). |
| 2 | `ORD-1002` | `ORD-1002` | `a00bm00003MxM3eAAF` | `CUST-002` (Maria Lopez) | `$18,700.00` | `SYNCED` | Sin colisión. |
| 3 | **`ORD-1009-CONTINGENCY`** | **`ORD-1009-CONTINGENCY`** | `a00bm00003MvhzkAAB` | `CUST-006` (Laura Medina) | `$950.00` | `SYNCED` | ⚠️ **Colisiona con `CA-09` y `CA-10`**. |
| 4 | `ORD-LIVE-01` | `ORD-LIVE-01` | `a00bm00003My6E2AAJ` | `CUST-001` (Juan Perez) | `$18,350.00` | `SYNCED` | Sin colisión. |
| 5 | `ORD-2001` | `ORD-2001` | `a00bm00003MyUbJAAV` | `CUST-001` (Juan Perez) | `$37,050.00` | `SYNCED` | Sin colisión. |
| 6 | `ORD-9009-CONTINGENCY` | `ORD-9009-CONTINGENCY` | `a00bm00003MyUcvAAF` | `CUST-006` (Laura Medina) | `$950.00` | `SYNCED` | Sin colisión. |
| 7 | `ORD-HERMES-01` | `ORD-HERMES-01` | `a00bm00003MyUkzAAF` | `CUST-AI-01` (Emmanuel Sanchez) | `$18,000.00` | `SYNCED` | Orden histórica de Hermes Agent. |
| 8 | `ORD-SF-REAL-01` | `ORD-SF-REAL-01` | `a00bm00003MviUOAAZ` | `CUST-001` (Juan Perez) | `$37,050.00` | `SYNCED` | Sin colisión. |
| 9 | `ORD-SF-REAL-02` | `ORD-SF-REAL-02` | `a00bm00003My4x8AAB` | `CUST-001` (Juan Perez) | `$37,050.00` | `SYNCED` | Sin colisión. |
| 10 | `ORD-LIVE-SF-01` | `ORD-LIVE-SF-01` | `a00bm00003My78TAAR` | `CUS-LIVE-01` (Emmanuel Sanchez) | `$18,700.00` | `SYNCED` | Sin colisión. |
| 11 | `ORD-HERMES-LIVE-02*` | `ORD-HERMES-LIVE-02` | `a00bm00003N10nBAAR` | `CUST-AI-02` (Emmanuel Sanchez - Hermes Live) | `$700.00` | `SYNCED` | Orden validada con Scheduler y sanitización. |

---

## 🔄 2. Cómo Reponer la Base de Datos y Salesforce Antes de Iniciar

Se ha dejado listo el script automatizado [`postman/prepare_clean_tests.py`](file:///c:/Users/emman/AnypointStudio/studio-workspace/postman/prepare_clean_tests.py) con dos modos a elegir:

* **Opción A — Limpieza Total (`--mode full`, Recomendada para Evidencias Limpias de Entrega):**
  Restaura el stock inicial (`LAP-001=12`, `MOU-001=30`, `CAM-001=15`, `MON-001=0`, `KEY-001=10`) y limpia las órdenes de prueba en PostgreSQL y Salesforce para que la tabla y el CRM luzcan impecables desde el Caso 1.
  ```powershell
  python c:\Users\emman\AnypointStudio\studio-workspace\postman\prepare_clean_tests.py --mode full
  ```
* **Opción B — Reposición Selectiva (`--mode selective`):**
  Restaura el stock inicial y elimina **únicamente** `ORD-1001` y `ORD-1009-CONTINGENCY` (en PostgreSQL y Salesforce), conservando tus órdenes previas de Hermes.
  ```powershell
  python c:\Users\emman\AnypointStudio\studio-workspace\postman\prepare_clean_tests.py --mode selective
  ```

---

## 📸 3. Metodología de Guardado de Fotos Independientes

Todas las capturas deben guardarse en `c:\Users\emman\AnypointStudio\studio-workspace\evidencias\capturas\` siguiendo la regla de **Independencia por Capa**:
1. **Foto de Petición y Respuesta (`_A_Postman.png`):** En Postman, asegurando que se vea el método HTTP, la URL, el Body enviado, el código de estado (`200`, `201`, `202`, `400`, `404`, `409`) y el JSON/CSV de respuesta con el header `X-Correlation-ID`.
2. **Foto de Reflejo en Base de Datos (`_B_PostgreSQL.png`):** Cuando la operación consulta o modifica datos en PostgreSQL, tomar captura de la terminal/cliente SQL mostrando el estado exacto de `products`, `retail_orders` y `retail_order_items`.
3. **Foto de Reflejo en Aplicación (`_C_Anypoint_Console.png`):** Cuando sea relevante demostrar la trazabilidad (`X-Correlation-ID`), el rollback transaccional o el Scheduler, tomar captura de la consola de Anypoint Studio.
4. **Foto de Reflejo en Salesforce CRM (`_D_Salesforce.png`):** Cuando la orden se sincroniza al CRM, tomar captura del registro `Retail_Order__c` (pestaña *Details* y *Related* con sus `Retail_Order_Item__c`).

### Matriz Maestra Paso a Paso (Guión de Pruebas y Capturas)

| Caso | Prueba a Ejecutar | Acción / Comando de Verificación en BD | Fotos Independientes a Guardar en `evidencias/capturas/` |
| :---: | :--- | :--- | :--- |
| **PRE** | **Infraestructura Lista** | Ejecutar reposición de BD y verificar las 5 apps `DEPLOYED` en Anypoint Studio. | 1. `00_A_PostgreSQL_Catalogo_Semilla.png` (Tabla `products` con stock inicial: LAP=12, MOU=30, CAM=15, MON=0, KEY=10).<br>2. `00_B_Anypoint_5_APIs_Deployed.png` (Consola Studio con las 5 apps `DEPLOYED`).<br>3. `00_C_Salesforce_Object_Retail_Order.png` y `00_D_Salesforce_Object_Retail_Order_Item.png`. |
| **CA-01** | **Consultar Producto Existente**<br>`GET /api/v1/products/LAP-001` | Verificar en BD que `LAP-001` tiene `unit_price = 18000.00`, `stock = 12`, `active = true`. | 1. `CA01_A_Postman_Get_Product_200.png` (Petición y respuesta `200 OK`).<br>2. `CA01_B_PostgreSQL_Product_LAP001.png` (Consulta SQL en BD confirmando el registro). |
| **CA-02** | **Alta de Orden Exitosa Sincronizada**<br>`POST /api/v1/orders` (`ORD-1001`: 2× `LAP-001` + 3× `MOU-001`) | Verificar en BD:<br>• `products`: `LAP-001` baja de `12` a **`10`**; `MOU-001` baja de `30` a **`27`**.<br>• `retail_orders`: `ORD-1001` con `total = 37050.00`, `sync_status = SYNCED`, `salesforce_id` poblado. | 1. `CA02_A_Postman_Create_ORD1001_201.png` (Request + Response `201 Created` con `salesforceId`).<br>2. `CA02_B_PostgreSQL_Order_And_Stock_Deducted.png` (Tablas `products`, `retail_orders` y `retail_order_items`).<br>3. `CA02_C_Salesforce_ORD1001_Header.png` (Ficha *Details* en Salesforce con `Status = SYNCED` y `$37,050.00`).<br>4. `CA02_D_Salesforce_ORD1001_Items.png` (Pestaña *Related* en Salesforce mostrando las 2 líneas hijas). |
| **CA-03** | **Consultar Orden Sincronizada**<br>`GET /api/v1/orders/ORD-1001` | — | 1. `CA03_A_Postman_Get_ORD1001_200.png` (Respuesta `200 OK` mostrando cabecera, 2 líneas, `total: 37050` y `salesforceId`). |
| **CA-04** | **Idempotencia (Repetir `ORD-1001`)**<br>`POST /api/v1/orders` (`ORD-1001`) | Verificar en BD que el stock de `LAP-001` sigue en **`10`** y `MOU-001` en **`27`** (sin doble descuento). | 1. `CA04_A_Postman_Duplicate_Order_409.png` (Respuesta `409 Conflict - ORDER_ALREADY_EXISTS`).<br>2. `CA04_B_PostgreSQL_Stock_Unchanged.png` (Evidencia en BD de que el stock no se descontó por segunda vez). |
| **CA-05** | **Validación Cantidad Inválida (`<= 0`)**<br>`POST /api/v1/orders` (`quantity: 0`) | Verificar que `ORD-1005-BADQTY` no existe en `retail_orders`. | 1. `CA05_A_Postman_Bad_Quantity_400.png` (Respuesta `400 Bad Request`). |
| **CA-06** | **Producto Inexistente (`XXX-999`)**<br>`POST /api/v1/orders` (`sku: XXX-999`) | Verificar que `ORD-1006-NOSKU` no existe en `retail_orders`. | 1. `CA06_A_Postman_Product_Not_Found_404.png` (Respuesta `404 Not Found - PRODUCT_NOT_FOUND`). |
| **CA-07** | **Stock Insuficiente (`MON-001`, stock 0)**<br>`POST /api/v1/orders` (`ORD-1007-NOSTOCK`) | Verificar en BD que la transacción hizo **Rollback** y no se insertó `ORD-1007-NOSTOCK`. | 1. `CA07_A_Postman_Insufficient_Stock_409.png` (Respuesta `409 Conflict - INSUFFICIENT_STOCK`).<br>2. `CA07_B_PostgreSQL_Rollback_Verified.png` (Consulta en BD confirmando 0 filas para `ORD-1007-NOSTOCK`). |
| **CA-08** | **SKUs Duplicados en Misma Orden**<br>`POST /api/v1/orders` (`CAM-001` dos veces) | — | 1. `CA08_A_Postman_Duplicate_SKU_400.png` (Respuesta `400 Bad Request - DUPLICATE_SKU`). |
| **CA-09** | **Contingencia de Salesforce (`202 PENDING_SYNC`)**<br>Detener temporalmente `retail-salesforce-sys-api` (o simular fallo) y enviar `POST /api/v1/orders` (`ORD-1009-CONTINGENCY` con 1× `CAM-001`). | Verificar en BD:<br>• `ORD-1009-CONTINGENCY` guardada con `sync_status = PENDING_SYNC`.<br>• Stock de `CAM-001` descontado de `15` a **`14`**. | 1. `CA09_A_Postman_Contingency_202_PendingSync.png` (Respuesta `202 Accepted` con `syncStatus: PENDING_SYNC`).<br>2. `CA09_B_PostgreSQL_Order_PendingSync.png` (Registro en BD con `PENDING_SYNC` y `CAM-001` en `14`). |
| **CA-10** | **Recuperación y Sincronización (`SYNCED`)**<br>Restaurar `retail-salesforce-sys-api` y ejecutar `POST http://localhost:8082/internal/v1/orders/ORD-1009-CONTINGENCY/sync` (o dejar actuar al Scheduler de 60s). | Verificar en BD:<br>• `ORD-1009-CONTINGENCY` cambia a `SYNCED` con `salesforce_id`.<br>• Stock de `CAM-001` permanece en **`14`** (sin descontar de nuevo). | 1. `CA10_A_Postman_Manual_Sync_200.png` (Respuesta `200 OK` con `syncStatus: SYNCED`).<br>2. `CA10_B_PostgreSQL_Order_Synced_NoDoubleDeduct.png` (BD mostrando `SYNCED` y stock de `CAM-001 = 14`).<br>3. `CA10_C_Salesforce_ORD1009_Synced.png` (Registro en Salesforce CRM). |
| **CA-11** | **Reporte Consolidado CSV**<br>`GET /api/v1/orders/report` (`Accept: text/csv`) | — | 1. `CA11_A_Postman_Report_CSV_200.png` (Respuesta `200 OK` en texto CSV con encabezado único). |
| **CA-12** | **Error Parcial en Líneas de Salesforce**<br>Verificación de no marcar `SYNCED` ante fallo de líneas y mantener `PENDING_SYNC`. | — | 1. `CA12_A_Partial_Error_Protection.png` (Evidencia de validación en `imp-orders-salesforce.xml` y respuesta `502` / `PENDING_SYNC`). |
| **MUNIT** | **Suite de 6 Pruebas Unitarias MUnit**<br>Ejecutar MUnit en `retail-orders-exp-api`. | — | 1. `MUNIT_A_Anypoint_6_Tests_Green.png` (Panel MUnit con 6/6 pruebas en verde y cobertura). |

---

## 🎥 4. Guión de Grabación en Video: Interacción con el Agente IA + Consola Anypoint + Salesforce

Para tu grabación de video (duración ideal: **90 a 150 segundos**), te sugiero organizar tu pantalla o alternar entre tres ventanas ya abiertas:
1. **Ventana 1:** **Hermes Agent** (Web UI en `http://127.0.0.1:9119` o CLI con `gemma4:e4b`).
2. **Ventana 2:** **Anypoint Studio** (Consola mostrando las 5 aplicaciones `DEPLOYED`).
3. **Ventana 3:** **Salesforce CRM** (Pestaña `Retail Orders -> All`).

### Escena 1: Estado Inicial (15 seg)
* Muestra rápidamente en **Anypoint Studio** que los 5 proyectos (`retail-orders-exp-api`, `retail-orders-pro-api`, `retail-db-sys-api`, `retail-salesforce-sys-api`, `retail-orders-mcp-server`) están **`DEPLOYED`**.
* Muestra en **Hermes Agent -> MCP** que `retail360-mulesoft` está activo con sus **4 herramientas** (`consultar_producto`, `crear_pedido`, `consultar_pedido`, `obtener_reporte_ordenes`).

### Escena 2: Prompt en Vivo al Agente IA (45 seg)
Pega este prompt limpio (**sin asteriscos de Markdown alrededor de los valores** para que entre limpio en el primer intento):

> Hola Hermes. Usando tus herramientas de MuleSoft Retail 360:
> 1. Consulta primero el producto LAP-001 y dime su precio y cuántas unidades tiene disponibles en stock.
> 2. Crea un nuevo pedido con los siguientes datos exactos:
>    - orderId: ORD-HERMES-VIDEO-01
>    - customerId: CUST-AI-99
>    - customerName: Emmanuel Sanchez Demo Final
>    - customerEmail: emmanuel@skala.io
>    - items: 1 unidad de LAP-001 y 2 unidades de MOU-001
> 3. Confírmame el estado de sincronización y el salesforceId asignado por Salesforce.

### Escena 3: Reflejo en Consola de Anypoint Studio (20 seg)
* Mientras Hermes ejecuta las herramientas (`consultar_producto` y `crear_pedido`), cambia a la **Consola de Anypoint Studio**.
* Se verá en vivo el rastro con `corr-mcp-hermes-3`:
  * `Consultando articulo en PostgreSQL: LAP-001`
  * `Registrando nueva orden: "ORD-HERMES-VIDEO-01"`
  * `Guardando orden transaccional en PostgreSQL: "ORD-HERMES-VIDEO-01"` (`HTTP 201`)
  * `Orden ORD-HERMES-VIDEO-01 sincronizada exitosamente en Salesforce con ID: "a00bm..."`

### Escena 4: Reflejo en Salesforce CRM y Cierre (30 seg)
* Regresa a **Hermes Agent** para mostrar su respuesta final con el resumen del pedido (`$18,700.00 MXN`, `SYNCED` y el `salesforceId`).
* Cambia al navegador en **Salesforce CRM (`Retail Orders`)**, pulsa el botón de **Refresh** y abre el registro recién creado **`ORD-HERMES-VIDEO-01`**.
* Muestra la pestaña **Details** (`Total: $18,700.00`, `Status: SYNCED`, `Customer Name: Emmanuel Sanchez Demo Final`) y la pestaña **Related** con los 2 ítems (`ORD-HERMES-VIDEO-01-LAP-001` y `ORD-HERMES-VIDEO-01-MOU-001`).
* *(Opcional)* Toma también las 3 capturas fijas del hito Bonus:
  * `BONUS_A_Hermes_ToolCalls_Response.png`
  * `BONUS_B_Anypoint_Console_MCP_Logs.png`
  * `BONUS_C_Salesforce_ORD_HERMES_VIDEO_01.png`

