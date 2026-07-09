-- Olist E-commerce Analytics
-- Paso 04: validar la tabla base a nivel item.
--
-- Estas consultas revisan que fact_order_items_delivered conserve el detalle
-- correcto de items vendidos y que sus montos cuadren contra los CSV crudos.
--
-- Dialecto SQL: DuckDB
-- Ejecutar despues de sql/03_create_order_items_base.sql.

-- Validamos que el identificador compuesto order_id + order_item_id no tenga
-- duplicados en la tabla procesada.
SELECT
    'grain_check' AS check_name,
    COUNT(*) AS rows_in_base,
    COUNT(DISTINCT order_id || '-' || order_item_id) AS distinct_order_items,
    COUNT(*) - COUNT(DISTINCT order_id || '-' || order_item_id) AS duplicate_order_item_rows
FROM read_csv_auto('data/processed/fact_order_items_delivered.csv');

-- Comparamos cantidad de items contra order_items raw filtrado a ordenes
-- entregadas. La diferencia esperada es cero.
SELECT
    'delivered_item_count_reconciliation' AS check_name,
    raw.delivered_items_raw,
    base.delivered_items_base,
    base.delivered_items_base - raw.delivered_items_raw AS difference
FROM (
    SELECT COUNT(*) AS delivered_items_raw
    FROM read_csv_auto('olist_order_items_dataset.csv') AS oi
    INNER JOIN read_csv_auto('olist_orders_dataset.csv') AS o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
) AS raw
CROSS JOIN (
    SELECT COUNT(*) AS delivered_items_base
    FROM read_csv_auto('data/processed/fact_order_items_delivered.csv')
) AS base;

-- Reconciliamos revenue y flete de items entregados.
SELECT
    'item_revenue_reconciliation' AS check_name,
    raw.item_revenue_raw,
    base.item_revenue_base,
    ROUND(base.item_revenue_base - raw.item_revenue_raw, 2) AS item_revenue_difference,
    raw.item_freight_raw,
    base.item_freight_base,
    ROUND(base.item_freight_base - raw.item_freight_raw, 2) AS item_freight_difference
FROM (
    SELECT
        ROUND(SUM(oi.price), 2) AS item_revenue_raw,
        ROUND(SUM(oi.freight_value), 2) AS item_freight_raw
    FROM read_csv_auto('olist_order_items_dataset.csv') AS oi
    INNER JOIN read_csv_auto('olist_orders_dataset.csv') AS o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
) AS raw
CROSS JOIN (
    SELECT
        ROUND(SUM(item_revenue), 2) AS item_revenue_base,
        ROUND(SUM(item_freight_value), 2) AS item_freight_base
    FROM read_csv_auto('data/processed/fact_order_items_delivered.csv')
) AS base;

-- Revisamos campos criticos para el dashboard de categorias y sellers.
SELECT
    'critical_null_check' AS check_name,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS missing_order_id,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS missing_product_id,
    SUM(CASE WHEN seller_id IS NULL THEN 1 ELSE 0 END) AS missing_seller_id,
    SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END) AS missing_category,
    SUM(CASE WHEN item_revenue IS NULL THEN 1 ELSE 0 END) AS missing_item_revenue,
    SUM(CASE WHEN purchase_month IS NULL THEN 1 ELSE 0 END) AS missing_purchase_month
FROM read_csv_auto('data/processed/fact_order_items_delivered.csv');

-- Este resumen muestra si hay categorias sin traducir o productos sin categoria.
-- No necesariamente son errores, se documentan para decidir como tratarlos.
SELECT
    'category_quality_check' AS check_name,
    COUNT(*) AS total_items,
    SUM(CASE WHEN category = 'unknown' THEN 1 ELSE 0 END) AS unknown_category_items,
    COUNT(DISTINCT category) AS distinct_categories,
    COUNT(DISTINCT product_id) AS distinct_products,
    COUNT(DISTINCT seller_id) AS distinct_sellers
FROM read_csv_auto('data/processed/fact_order_items_delivered.csv');

-- KPIs preliminares por categoria para revisar que la tabla ya responde
-- preguntas comerciales basicas.
SELECT
    category,
    ROUND(SUM(item_revenue), 2) AS category_revenue,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(*) AS items_sold,
    ROUND(AVG(item_revenue), 2) AS avg_item_revenue,
    ROUND(AVG(avg_review_score), 2) AS avg_review_score
FROM read_csv_auto('data/processed/fact_order_items_delivered.csv')
GROUP BY category
ORDER BY category_revenue DESC
LIMIT 10;
