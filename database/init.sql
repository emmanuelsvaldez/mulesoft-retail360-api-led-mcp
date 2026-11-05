-- ============================================================================
-- SKALA · PROYECTO INTEGRADOR FINAL: RETAIL 360
-- Script de Inicialización y Datos Semilla para PostgreSQL (Base: retail360)
-- ============================================================================

-- Limpieza previa idempotente (para reinicios de laboratorio)
DROP TABLE IF EXISTS retail_order_items CASCADE;
DROP TABLE IF EXISTS retail_orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- 1. Tabla de Catálogo e Inventario de Productos
CREATE TABLE products (
    sku           VARCHAR(30) PRIMARY KEY,
    product_name  VARCHAR(120) NOT NULL,
    unit_price    NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    stock         INTEGER NOT NULL CHECK (stock >= 0),
    active        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Cabecera de Órdenes Retail
CREATE TABLE retail_orders (
    order_id         VARCHAR(50) PRIMARY KEY,
    customer_id      VARCHAR(50) NOT NULL,
    customer_name    VARCHAR(120) NOT NULL,
    customer_email   VARCHAR(150) NOT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'CREATED'
                     CHECK (status IN ('CREATED')),
    sync_status      VARCHAR(20) NOT NULL DEFAULT 'PENDING_SYNC'
                     CHECK (sync_status IN ('PENDING_SYNC', 'SYNCED', 'SYNC_ERROR')),
    total            NUMERIC(12, 2) NOT NULL CHECK (total >= 0),
    currency         VARCHAR(10) NOT NULL DEFAULT 'MXN',
    salesforce_id    VARCHAR(50),
    sync_attempts    INTEGER NOT NULL DEFAULT 0 CHECK (sync_attempts >= 0),
    last_sync_error  TEXT,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas del Scheduler (PENDING_SYNC) y Reportes CSV
CREATE INDEX idx_retail_orders_sync_status ON retail_orders(sync_status);
CREATE INDEX idx_retail_orders_created_at ON retail_orders(created_at DESC);

-- 3. Tabla de Líneas de Detalle de Órdenes Retail
CREATE TABLE retail_order_items (
    id          SERIAL PRIMARY KEY,
    order_id    VARCHAR(50) NOT NULL REFERENCES retail_orders(order_id) ON DELETE CASCADE,
    sku         VARCHAR(30) NOT NULL REFERENCES products(sku),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal    NUMERIC(12, 2) NOT NULL CHECK (subtotal >= 0),
    CONSTRAINT uq_retail_order_items_order_sku UNIQUE (order_id, sku)
);

CREATE INDEX idx_retail_order_items_order_id ON retail_order_items(order_id);

-- ============================================================================
-- DATOS SEMILLA OFICIALES DEL LABORATORIO (Sección 6 y Casos CA-01 a CA-12)
-- ============================================================================
INSERT INTO products (sku, product_name, unit_price, stock, active) VALUES
    -- Productos activos con stock para CA-01 y CA-02 (2*18000 + 3*350 = 37,050.00 MXN)
    ('LAP-001', 'Laptop 14 pulgadas',       18000.00, 12, TRUE),
    ('MOU-001', 'Mouse Inalambrico Pro',      350.00, 30, TRUE),
    ('CAM-001', 'Webcam Full HD 1080p',       950.00, 15, TRUE),
    -- Producto activo SIN STOCK para probar CA-07 (409 INSUFFICIENT_STOCK y Rollback)
    ('MON-001', 'Monitor 27 pulgadas 4K',    6500.00,  0, TRUE),
    -- Producto INACTIVO con stock para probar RF-03 (Rechazo de productos inactivos)
    ('KEY-001', 'Teclado Mecanico Legacy',   1200.00, 10, FALSE);

