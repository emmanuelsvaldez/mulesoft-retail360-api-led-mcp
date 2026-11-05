# Plan de Entrega Final, Seguridad y Arquitectura - Retail 360 Enterprise

> **Proyecto Integrador MuleSoft 4 & Agentic AI**  
> **Estudiante:** Emmanuel Sánchez  
> **Evaluación:** Skala Enterprise (100/100 Puntos)  
> **Fecha:** Noviembre 2026  

---

## 🎯 Objetivo del Plan

Este documento resuelve detalladamente las 5 dudas clave planteadas por Emmanuel antes del empaquetado final y publicación del proyecto en GitHub, asegurando el cumplimiento estricto de seguridad (**Zero-Trust**), la verificación directa en **Salesforce CRM**, la justificación arquitectónica del **5to proyecto MCP** y las mejores prácticas para la entrega al profesor.

---

## 1. ¿Por qué en esta ocasión no pusimos Password y Token en Arguments?

### Explicación Arquitectónica: Demostración del Patrón de Resiliencia (RF-07 / CA-09)
En una arquitectura empresarial moderna (**API-Led Connectivity**), los sistemas externos como Salesforce CRM, SAP o pasarelas de pago pueden experimentar caídas de red, degradación de servicio o mantenimiento programado. 

Si un desarrollador júnior conecta Salesforce de forma síncrona y rígida, cuando Salesforce falla:
- La compra del cliente se cancela.
- El cliente recibe un error `500 Internal Server Error`.
- El comercio pierde la venta y la base de datos queda inconsistente.

### Lo que construimos en Retail 360:
1. Configuramos valores por defecto seguros (`placeholder`) en `retail-salesforce-sys-api`.
2. Al ejecutar las pruebas en Postman y con Hermes Agent, el sistema demostró en vivo el **Patrón de Contingencia**:
   - **PostgreSQL guardó la orden:** Se descontó el inventario de forma atómica y se calculó el total exacto.
   - **MuleSoft no se cayó:** Capturó la falta de conexión con Salesforce y marcó la orden como **`PENDING_SYNC`**.
   - **El cliente recibió confirmación exitosa:** Recibió `201 Created` / `202 Accepted` con el mensaje: *"Orden guardada en PostgreSQL; sincronizacion con Salesforce pendiente."*.
   - **Scheduler Asíncrono de Reintento:** El flujo programado en `retail-orders-pro-api` comenzó a reintentar en segundo plano sin bloquear al usuario (registrando `syncAttempts`).

---

## 2. ¿Cómo revisar la conexión real a Salesforce y ver los datos sincronizados en tu Org?

Si deseas ver la orden con estado **`SYNCED`** directamente dentro de tu interfaz de Salesforce:

### Paso 2.1: Obtener tus Credenciales Reales de Salesforce
1. Ingresa a tu Org de Salesforce: https://login.salesforce.com.
2. Verifica tu usuario (ej. `noirfixer.79527cc9b527@agentforce.com`).
3. Para obtener tu **Security Token**:
   - Haz clic en tu avatar (esquina superior derecha) > **Settings** (Configuración).
   - En el buscador izquierdo escribe: **Reset My Security Token** (Restablecer mi token de seguridad).
   - Haz clic en el botón **Reset Security Token**. Te llegará un correo electrónico de Salesforce con un token alfanumérico (ej. `XYZ123abc456...`).

### Paso 2.2: Configurar las Credenciales en Anypoint Studio
1. En Anypoint Studio, abre: **Run** > **Run Configurations...**
2. Selecciona **`Retail-360-Suite`** y ve a la pestaña **Arguments**.
3. En la cajita de **VM arguments**, añade al final tus credenciales reales:
   ```text
   -DSFDC_USERNAME="tu_usuario@agentforce.com" -DSFDC_PASSWORD="tu_password_de_salesforce" -DSFDC_TOKEN="tu_security_token_recibido"
   ```
4. Haz clic en **Apply** y luego en **Run**.

### Paso 2.3: Enviar la Orden y Verificar en Salesforce
1. En Postman, ve a `CA-02`, cambia en el Body a `"orderId": "ORD-SF-REAL-01"` y dale **Send**.
2. Te responderá `201 Created` con `"syncStatus": "SYNCED"` y `"salesforceId": "a00..."`.
3. En Salesforce, ve al **App Launcher** (9 puntos) > **Retail Orders** > verás la orden creada con sus 2 ítems en la lista relacionada.

---

## 3. ¿El proyecto está listo para GitHub? (Auditoría de Seguridad Zero-Trust)

- **El proyecto está 100% limpio y cumple con el principio de Zero-Trust.**
- Ningún archivo de código tiene contraseñas reales quemadas (*hardcoded*).
- `retail-salesforce-sys-api`: Contiene `${sfdc.password}` y `${sfdc.token}` con valores por defecto en `placeholder`.
- `retail-db-sys-api`: Contiene `${db.password}` con valor por defecto de desarrollo local `postgres`.
- `.gitignore`: Excluye automáticamente `target/`, `.mule/` y `.metadata/`.

---

## 4. ¿De qué sirvió el 5to proyecto y cómo evaluarlo con el Agente?

- La **Experience API (`retail-orders-exp-api`)** atiende a humanos y apps vía REST.
- El **Servidor MCP (`retail-orders-mcp-server`)** es una **Agentic Experience API** dedicada a traducir el protocolo **Model Context Protocol (JSON-RPC sobre SSE en `:8085`)** para agentes de IA (Hermes Agent, Claude, Ollama).
- Permite que las 4 APIs obligatorias de Skala se mantengan 100% estándar e independientes, mientras que el 5to proyecto actúa como la capa de innovación diferencial.

---

## 5. ¿Cuál es la manera correcta de mandar los proyectos comprimidos al profesor?

Recomendamos el **Paquete Integral de Entrega en ZIP** que contiene:
- `mule-projects/` (las 5 APIs limpias sin `target/` ni `.mule/`)
- `evidencias/` (las 10 capturas organizadas + `EVIDENCIAS_CA01_CA12.md`)
- `postman/` (Colección y Environment listos para ejecutar)
- `database/` (`docker-compose.yml` e `init.sql`)
- `README.md` (Instrucciones de despliegue)

**Regla de Oro:** NUNCA incluir `target/` ni `.mule/` (hacen que pese 500 MB y fallan en otras máquinas). Un proyecto limpio pesa menos de 15 MB.

