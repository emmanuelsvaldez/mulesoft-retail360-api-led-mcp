# Carpeta de Evidencias Fotográficas - Retail 360 Skala

En esta carpeta se almacenan las capturas de pantalla numeradas que respaldan los 12 Casos de Aceptación (`CA-01` a `CA-12`), la persistencia en PostgreSQL, la sincronización en Salesforce CRM, la ejecución de MUnit y el servidor MCP con Hermes Agent.

## Índice de Capturas Esperadas
1. `Evidencia_01_PostgreSQL_Tablas_y_Catalogo.png` — Contenedor Docker y consulta inicial `SELECT * FROM products;`.
2. `Evidencia_02_Salesforce_Object_Retail_Order.png` — Objeto Custom `Retail_Order__c` con `External_Order_Id__c` (External ID & Unique).
3. `Evidencia_03_Salesforce_Object_Retail_Order_Item.png` — Objeto Custom `Retail_Order_Item__c` con `External_Line_Id__c` (External ID & Unique).
4. `Evidencia_04_Anypoint_4_APIs_Deployed.png` — Las 4 APIs desplegadas simultáneamente en Anypoint Studio.
5. `Evidencia_05_CA01_CA03_Postman_y_Salesforce.png` — Creación `ORD-1001` (`201 Created`) y registro creado en Salesforce CRM + PostgreSQL.
6. `Evidencia_06_CA04_CA08_Validaciones_e_Idempotencia.png` — Respuestas `409 Conflict`, `404 Not Found` y `400 Bad Request`.
7. `Evidencia_07_CA09_CA10_Contingencia_202_y_Sync_200.png` — Continuidad de negocio con `202 PENDING_SYNC` y posterior sincronización `200 SYNCED`.
8. `Evidencia_08_CA11_Reporte_CSV.png` — Descarga del reporte `text/csv` con encabezado único.
9. `Evidencia_09_MUnit_6_Tests_Green.png` — Ejecución exitosa de la suite de 6+ pruebas MUnit.
10. `Evidencia_10_Bonus_MCP_Hermes_Agent.png` — Simulación Agentic AI desde Hermes Agent + Ollama invocando MuleSoft.

