-- Olist E-commerce Analytics
-- Paso 02: validar la tabla base a nivel orden.
--
-- Estas consultas verifican que fact_orders_delivered conserva el grano
-- esperado y que sus metricas principales cuadran contra los CSV originales.
--
-- Dialecto SQL: DuckDB
-- Ejecutar despues de sql/01_create_order_base.sql.

-- Validamos que la tabla mantenga una fila por order_id. Si el conteo total
-- y el conteo de ordenes distintas coinciden, el grano esta correcto.
SELECT
    'grain_check' AS check_name,
    COUNT(*) AS rows_in_base,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_order_rows
FROM read_csv_auto('data/processed/fact_orders_delivered.csv');

-- Comparamos el conteo de la tabla procesada contra el conteo raw de ordenes
-- entregadas. La diferencia esperada es cero.
SELECT
    'delivered_order_count_reconciliation' AS check_name,
    raw.delivered_orders_raw,
    base.delivered_orders_base,
    base.delivered_orders_base - raw.delivered_orders_raw AS difference
FROM (
    SELECT COUNT(*) AS delivered_orders_raw
    FROM read_csv_auto('olist_orders_dataset.csv')
    WHERE order_status = 'delivered'
) AS raw
CROSS JOIN (
    SELECT COUNT(*) AS delivered_orders_base
    FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
) AS base;

-- Reconciliamos revenue y flete contra order_items raw para asegurar que la
-- agregacion por orden no cambio los montos.
SELECT
    'revenue_and_freight_reconciliation' AS check_name,
    raw.product_revenue_raw,
    base.product_revenue_base,
    ROUND(base.product_revenue_base - raw.product_revenue_raw, 2) AS product_revenue_difference,
    raw.freight_value_raw,
    base.freight_value_base,
    ROUND(base.freight_value_base - raw.freight_value_raw, 2) AS freight_value_difference
FROM (
    SELECT
        ROUND(SUM(oi.price), 2) AS product_revenue_raw,
        ROUND(SUM(oi.freight_value), 2) AS freight_value_raw
    FROM read_csv_auto('olist_order_items_dataset.csv') AS oi
    INNER JOIN read_csv_auto('olist_orders_dataset.csv') AS o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
) AS raw
CROSS JOIN (
    SELECT
        ROUND(SUM(product_revenue), 2) AS product_revenue_base,
        ROUND(SUM(freight_value), 2) AS freight_value_base
    FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
) AS base;

-- Revisamos nulos en campos que el dashboard necesitara para filtros, KPIs y
-- series temporales.
SELECT
    'critical_null_check' AS check_name,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS missing_order_id,
    SUM(CASE WHEN customer_unique_id IS NULL THEN 1 ELSE 0 END) AS missing_customer_unique_id,
    SUM(CASE WHEN purchase_ts IS NULL THEN 1 ELSE 0 END) AS missing_purchase_ts,
    SUM(CASE WHEN product_revenue IS NULL THEN 1 ELSE 0 END) AS missing_product_revenue,
    SUM(CASE WHEN delivery_status IS NULL THEN 1 ELSE 0 END) AS missing_delivery_status
FROM read_csv_auto('data/processed/fact_orders_delivered.csv');

-- Guardamos una vista rapida de KPIs base. Si algun cambio futuro altera estos
-- valores sin razon, sabremos que hay que revisar la transformacion.
SELECT
    'baseline_kpis' AS check_name,
    COUNT(*) AS delivered_orders,
    ROUND(SUM(product_revenue), 2) AS product_revenue,
    ROUND(AVG(product_revenue), 2) AS average_order_value,
    COUNT(DISTINCT customer_unique_id) AS unique_customers,
    ROUND(AVG(avg_review_score), 2) AS average_review_score,
    ROUND(100 * AVG(is_late_delivery), 2) AS late_delivery_rate_pct,
    MIN(purchase_ts) AS first_purchase,
    MAX(purchase_ts) AS last_purchase
FROM read_csv_auto('data/processed/fact_orders_delivered.csv');
