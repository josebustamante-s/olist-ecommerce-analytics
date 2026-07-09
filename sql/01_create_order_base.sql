-- Olist E-commerce Analytics
-- Paso 01: construir una tabla analitica a nivel orden.
--
-- El dataset crudo de Olist tiene tablas con distinto nivel de detalle:
--   - orders: una fila por orden
--   - order_items: una o mas filas por orden
--   - payments: una o mas filas por orden
--   - reviews: a veces mas de una fila por orden
--
-- Para evitar duplicar metricas al unir tablas, primero llevamos items,
-- pagos y reviews al mismo nivel de detalle: una fila por orden.
--
-- Dialecto SQL: DuckDB
-- Ejecutar desde la raiz del proyecto.

CREATE OR REPLACE TABLE fact_orders_delivered AS

WITH delivered_orders AS (
    -- Partimos desde ordenes entregadas porque los KPIs comerciales deben
    -- representar ventas completadas. Las fechas se convierten a TIMESTAMP
    -- para calcular periodos y tiempos de entrega.
    SELECT
        order_id,
        customer_id,
        order_status,
        CAST(order_purchase_timestamp AS TIMESTAMP) AS purchase_ts,
        CAST(order_approved_at AS TIMESTAMP) AS approved_ts,
        CAST(order_delivered_carrier_date AS TIMESTAMP) AS delivered_carrier_ts,
        CAST(order_delivered_customer_date AS TIMESTAMP) AS delivered_customer_ts,
        CAST(order_estimated_delivery_date AS TIMESTAMP) AS estimated_delivery_ts
    FROM read_csv_auto('olist_orders_dataset.csv')
    WHERE order_status = 'delivered'
),

customer_dim AS (
    -- Mantenemos customer_id para unir con orders y customer_unique_id para
    -- analizar recurrencia de clientes en pasos posteriores.
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    FROM read_csv_auto('olist_customers_dataset.csv')
),

item_summary AS (
    -- Order items viene a nivel producto dentro de la orden. Lo resumimos por
    -- order_id para obtener revenue de producto, flete, cantidad de items,
    -- productos distintos y sellers distintos sin duplicar la orden.
    SELECT
        order_id,
        COUNT(*) AS item_count,
        COUNT(DISTINCT product_id) AS distinct_product_count,
        COUNT(DISTINCT seller_id) AS distinct_seller_count,
        ROUND(SUM(price), 2) AS product_revenue,
        ROUND(SUM(freight_value), 2) AS freight_value,
        ROUND(AVG(price), 2) AS avg_item_price
    FROM read_csv_auto('olist_order_items_dataset.csv')
    GROUP BY order_id
),

payment_ranked AS (
    -- Algunas ordenes tienen mas de una fila de pago. Este ranking permite
    -- identificar el tipo de pago con mayor valor dentro de cada orden para
    -- usarlo luego como descriptor simple en filtros del dashboard.
    SELECT
        order_id,
        payment_type,
        payment_value,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY payment_value DESC, payment_type
        ) AS payment_type_rank
    FROM read_csv_auto('olist_order_payments_dataset.csv')
),

payment_summary AS (
    -- Resumimos pagos por orden. payment_value queda disponible para revisar
    -- consistencia, pero el revenue principal del proyecto viene desde items.
    SELECT
        order_id,
        COUNT(*) AS payment_sequence_count,
        COUNT(DISTINCT payment_type) AS distinct_payment_type_count,
        MAX(payment_installments) AS max_payment_installments,
        ROUND(SUM(payment_value), 2) AS payment_value
    FROM read_csv_auto('olist_order_payments_dataset.csv')
    GROUP BY order_id
),

main_payment_type AS (
    -- Conservamos un solo tipo de pago por orden: el de mayor valor.
    -- Asi podemos filtrar por metodo de pago sin expandir la tabla base.
    SELECT
        order_id,
        payment_type AS main_payment_type
    FROM payment_ranked
    WHERE payment_type_rank = 1
),

review_summary AS (
    -- Las reviews se resumen por orden. La mayoria tiene una sola review,
    -- pero usar agregaciones mantiene estable el modelo cuando hay mas de una.
    -- Tambien guardamos si existe comentario escrito para posibles analisis futuros.
    SELECT
        order_id,
        COUNT(*) AS review_count,
        ROUND(AVG(review_score), 2) AS avg_review_score,
        MIN(review_score) AS min_review_score,
        MAX(review_score) AS max_review_score,
        MAX(
            CASE
                WHEN review_comment_message IS NOT NULL
                     AND LENGTH(TRIM(review_comment_message)) > 0
                THEN 1 ELSE 0
            END
        ) AS has_review_comment
    FROM read_csv_auto('olist_order_reviews_dataset.csv')
    GROUP BY order_id
)

SELECT
    -- Identificadores
    o.order_id,
    o.customer_id,
    c.customer_unique_id,

    -- Geografia del cliente
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state,

    -- Fechas del ciclo de vida de la orden
    o.order_status,
    o.purchase_ts,
    CAST(o.purchase_ts AS DATE) AS purchase_date,
    DATE_TRUNC('week', o.purchase_ts)::DATE AS purchase_week,
    DATE_TRUNC('month', o.purchase_ts)::DATE AS purchase_month,
    EXTRACT(YEAR FROM o.purchase_ts) AS purchase_year,
    EXTRACT(MONTH FROM o.purchase_ts) AS purchase_month_number,
    o.approved_ts,
    o.delivered_carrier_ts,
    o.delivered_customer_ts,
    o.estimated_delivery_ts,

    -- Metricas de entrega. delivery_days mide duracion total y
    -- delivery_delay_days mide atraso o adelanto contra la fecha estimada.
    DATE_DIFF('day', o.purchase_ts, o.delivered_customer_ts) AS delivery_days,
    DATE_DIFF('day', o.estimated_delivery_ts, o.delivered_customer_ts) AS delivery_delay_days,
    CASE
        WHEN o.delivered_customer_ts > o.estimated_delivery_ts THEN 1
        ELSE 0
    END AS is_late_delivery,
    CASE
        WHEN o.delivered_customer_ts > o.estimated_delivery_ts THEN 'late'
        ELSE 'on_time'
    END AS delivery_status,

    -- Metricas de items y revenue. COALESCE evita que valores faltantes en
    -- tablas secundarias se propaguen como nulos en metricas numericas.
    COALESCE(i.item_count, 0) AS item_count,
    COALESCE(i.distinct_product_count, 0) AS distinct_product_count,
    COALESCE(i.distinct_seller_count, 0) AS distinct_seller_count,
    COALESCE(i.product_revenue, 0) AS product_revenue,
    COALESCE(i.freight_value, 0) AS freight_value,
    COALESCE(i.avg_item_price, 0) AS avg_item_price,
    CASE
        WHEN COALESCE(i.product_revenue, 0) + COALESCE(i.freight_value, 0) = 0
        THEN NULL
        ELSE ROUND(
            i.freight_value / (i.product_revenue + i.freight_value),
            4
        )
    END AS freight_share,

    -- Metricas de pago
    COALESCE(p.payment_sequence_count, 0) AS payment_sequence_count,
    COALESCE(p.distinct_payment_type_count, 0) AS distinct_payment_type_count,
    p.max_payment_installments,
    m.main_payment_type,
    COALESCE(p.payment_value, 0) AS payment_value,

    -- Metricas de reviews
    COALESCE(r.review_count, 0) AS review_count,
    r.avg_review_score,
    r.min_review_score,
    r.max_review_score,
    COALESCE(r.has_review_comment, 0) AS has_review_comment
FROM delivered_orders AS o
-- Las uniones parten desde delivered_orders para preservar una fila por orden
-- entregada, incluso cuando alguna tabla secundaria no tenga informacion.
LEFT JOIN customer_dim AS c
    ON o.customer_id = c.customer_id
LEFT JOIN item_summary AS i
    ON o.order_id = i.order_id
LEFT JOIN payment_summary AS p
    ON o.order_id = p.order_id
LEFT JOIN main_payment_type AS m
    ON o.order_id = m.order_id
LEFT JOIN review_summary AS r
    ON o.order_id = r.order_id;

-- Exportamos la tabla analitica para reutilizar exactamente la misma base en
-- notebooks y en la aplicacion Streamlit.
COPY fact_orders_delivered
TO 'data/processed/fact_orders_delivered.csv'
WITH (HEADER, DELIMITER ',');
