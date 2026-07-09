-- Olist E-commerce Analytics
-- Paso 05: crear salidas agregadas para preguntas de negocio.
--
-- Estas consultas transforman las tablas base en datasets pequenos y listos
-- para notebook y dashboard. Cada salida responde una pregunta del brief y
-- evita recalcular logica compleja dentro de Streamlit.
--
-- Dialecto SQL: DuckDB
-- Ejecutar despues de crear fact_orders_delivered y fact_order_items_delivered.

CREATE OR REPLACE TABLE kpi_summary AS
SELECT
    COUNT(*) AS delivered_orders,
    ROUND(SUM(product_revenue), 2) AS product_revenue,
    ROUND(AVG(product_revenue), 2) AS average_order_value,
    COUNT(DISTINCT customer_unique_id) AS unique_customers,
    ROUND(AVG(avg_review_score), 2) AS average_review_score,
    ROUND(100 * AVG(is_late_delivery), 2) AS late_delivery_rate_pct,
    ROUND(AVG(delivery_days), 2) AS average_delivery_days,
    MIN(purchase_date) AS first_purchase_date,
    MAX(purchase_date) AS last_purchase_date
FROM read_csv_auto('data/processed/fact_orders_delivered.csv');

COPY kpi_summary
TO 'data/processed/kpi_summary.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE monthly_sales AS
SELECT
    purchase_month,
    COUNT(*) AS delivered_orders,
    ROUND(SUM(product_revenue), 2) AS product_revenue,
    ROUND(AVG(product_revenue), 2) AS average_order_value,
    COUNT(DISTINCT customer_unique_id) AS unique_customers,
    ROUND(AVG(avg_review_score), 2) AS average_review_score,
    ROUND(100 * AVG(is_late_delivery), 2) AS late_delivery_rate_pct
FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
GROUP BY purchase_month
ORDER BY purchase_month;

COPY monthly_sales
TO 'data/processed/monthly_sales.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE weekly_sales AS
SELECT
    purchase_week,
    COUNT(*) AS delivered_orders,
    ROUND(SUM(product_revenue), 2) AS product_revenue,
    ROUND(AVG(product_revenue), 2) AS average_order_value,
    COUNT(DISTINCT customer_unique_id) AS unique_customers
FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
GROUP BY purchase_week
ORDER BY purchase_week;

COPY weekly_sales
TO 'data/processed/weekly_sales.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE category_performance AS
SELECT
    category,
    COUNT(DISTINCT order_id) AS delivered_orders,
    COUNT(*) AS items_sold,
    COUNT(DISTINCT product_id) AS distinct_products,
    COUNT(DISTINCT seller_id) AS distinct_sellers,
    ROUND(SUM(item_revenue), 2) AS product_revenue,
    ROUND(SUM(item_freight_value), 2) AS freight_value,
    ROUND(AVG(item_revenue), 2) AS average_item_revenue,
    ROUND(AVG(item_freight_share), 4) AS average_freight_share,
    ROUND(AVG(avg_review_score), 2) AS average_review_score,
    ROUND(100 * AVG(is_late_delivery), 2) AS late_delivery_rate_pct
FROM read_csv_auto('data/processed/fact_order_items_delivered.csv')
GROUP BY category
ORDER BY product_revenue DESC;

COPY category_performance
TO 'data/processed/category_performance.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE category_monthly_sales AS
SELECT
    purchase_month,
    category,
    COUNT(DISTINCT order_id) AS delivered_orders,
    COUNT(*) AS items_sold,
    ROUND(SUM(item_revenue), 2) AS product_revenue
FROM read_csv_auto('data/processed/fact_order_items_delivered.csv')
GROUP BY purchase_month, category
ORDER BY purchase_month, product_revenue DESC;

COPY category_monthly_sales
TO 'data/processed/category_monthly_sales.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE customer_lifetime AS
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        COUNT(*) AS delivered_orders,
        ROUND(SUM(product_revenue), 2) AS customer_revenue,
        ROUND(AVG(product_revenue), 2) AS average_order_value,
        MIN(purchase_date) AS first_purchase_date,
        MAX(purchase_date) AS last_purchase_date,
        MODE(customer_state) AS primary_customer_state
    FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
    GROUP BY customer_unique_id
)
SELECT
    customer_unique_id,
    delivered_orders,
    customer_revenue,
    average_order_value,
    first_purchase_date,
    last_purchase_date,
    primary_customer_state,
    DATE_DIFF('day', first_purchase_date, last_purchase_date) AS customer_lifespan_days,
    CASE
        WHEN delivered_orders = 1 THEN '1 order'
        WHEN delivered_orders = 2 THEN '2 orders'
        WHEN delivered_orders = 3 THEN '3 orders'
        ELSE '4+ orders'
    END AS frequency_segment,
    CASE
        WHEN delivered_orders > 1 THEN 1
        ELSE 0
    END AS is_repeat_customer,
    CASE
        WHEN customer_revenue >= 500 THEN 'high_value'
        WHEN customer_revenue >= 150 THEN 'mid_value'
        ELSE 'low_value'
    END AS value_segment
FROM customer_orders;

COPY customer_lifetime
TO 'data/processed/customer_lifetime.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE customer_frequency_summary AS
SELECT
    frequency_segment,
    COUNT(*) AS customers,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct,
    ROUND(SUM(customer_revenue), 2) AS product_revenue,
    ROUND(100 * SUM(customer_revenue) / SUM(SUM(customer_revenue)) OVER (), 2) AS revenue_share_pct,
    ROUND(AVG(average_order_value), 2) AS average_order_value
FROM customer_lifetime
GROUP BY frequency_segment
ORDER BY
    CASE frequency_segment
        WHEN '1 order' THEN 1
        WHEN '2 orders' THEN 2
        WHEN '3 orders' THEN 3
        ELSE 4
    END;

COPY customer_frequency_summary
TO 'data/processed/customer_frequency_summary.csv'
WITH (HEADER, DELIMITER ',');

-- El dashboard solo necesita la duración de las compras repetidas, no el
-- identificador ni el historial completo de cada cliente. Este extracto
-- compacto permite publicar la visualización sin versionar datos a nivel cliente.
CREATE OR REPLACE TABLE customer_repeat_timing AS
SELECT
    customer_lifespan_days
FROM customer_lifetime
WHERE is_repeat_customer = 1;

COPY customer_repeat_timing
TO 'data/processed/customer_repeat_timing.csv'
WITH (HEADER, DELIMITER ',');

-- La tasa de recompra por estado mantiene solo los conteos necesarios para
-- comparar territorios, evitando que Streamlit tenga que cargar customer_lifetime.
CREATE OR REPLACE TABLE customer_repeat_rate_by_state AS
SELECT
    primary_customer_state AS customer_state,
    COUNT(*) AS unique_customers,
    SUM(is_repeat_customer) AS repeat_customers,
    ROUND(100 * SUM(is_repeat_customer) / COUNT(*), 2) AS repeat_customer_rate_pct
FROM customer_lifetime
GROUP BY primary_customer_state
ORDER BY unique_customers DESC;

COPY customer_repeat_rate_by_state
TO 'data/processed/customer_repeat_rate_by_state.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE customer_state_summary AS
SELECT
    customer_state,
    COUNT(*) AS delivered_orders,
    COUNT(DISTINCT customer_unique_id) AS unique_customers,
    ROUND(SUM(product_revenue), 2) AS product_revenue,
    ROUND(AVG(product_revenue), 2) AS average_order_value,
    ROUND(AVG(avg_review_score), 2) AS average_review_score,
    ROUND(100 * AVG(is_late_delivery), 2) AS late_delivery_rate_pct,
    ROUND(AVG(delivery_days), 2) AS average_delivery_days
FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
GROUP BY customer_state
ORDER BY product_revenue DESC;

COPY customer_state_summary
TO 'data/processed/customer_state_summary.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE delivery_satisfaction AS
SELECT
    CASE
        WHEN delivery_delay_days <= -7 THEN '7+ days early'
        WHEN delivery_delay_days BETWEEN -6 AND -1 THEN '1-6 days early'
        WHEN delivery_delay_days = 0 THEN 'on estimate'
        WHEN delivery_delay_days BETWEEN 1 AND 3 THEN '1-3 days late'
        WHEN delivery_delay_days BETWEEN 4 AND 7 THEN '4-7 days late'
        ELSE '8+ days late'
    END AS delivery_delay_segment,
    COUNT(*) AS delivered_orders,
    ROUND(SUM(product_revenue), 2) AS product_revenue,
    ROUND(AVG(product_revenue), 2) AS average_order_value,
    ROUND(AVG(delivery_days), 2) AS average_delivery_days,
    ROUND(AVG(delivery_delay_days), 2) AS average_delay_days,
    ROUND(AVG(avg_review_score), 2) AS average_review_score
FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
GROUP BY delivery_delay_segment
ORDER BY
    CASE delivery_delay_segment
        WHEN '7+ days early' THEN 1
        WHEN '1-6 days early' THEN 2
        WHEN 'on estimate' THEN 3
        WHEN '1-3 days late' THEN 4
        WHEN '4-7 days late' THEN 5
        ELSE 6
    END;

COPY delivery_satisfaction
TO 'data/processed/delivery_satisfaction.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE payment_summary AS
SELECT
    COALESCE(main_payment_type, 'unknown') AS main_payment_type,
    CASE
        WHEN max_payment_installments IS NULL THEN 'unknown'
        WHEN max_payment_installments <= 1 THEN '1 installment'
        WHEN max_payment_installments BETWEEN 2 AND 3 THEN '2-3 installments'
        WHEN max_payment_installments BETWEEN 4 AND 6 THEN '4-6 installments'
        ELSE '7+ installments'
    END AS installment_segment,
    COUNT(*) AS delivered_orders,
    ROUND(SUM(product_revenue), 2) AS product_revenue,
    ROUND(AVG(product_revenue), 2) AS average_order_value,
    COUNT(DISTINCT customer_unique_id) AS unique_customers
FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
GROUP BY main_payment_type, installment_segment
ORDER BY product_revenue DESC;

COPY payment_summary
TO 'data/processed/payment_summary.csv'
WITH (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE seller_performance AS
SELECT
    seller_id,
    seller_state,
    seller_city,
    COUNT(DISTINCT order_id) AS delivered_orders,
    COUNT(*) AS items_sold,
    COUNT(DISTINCT product_id) AS distinct_products,
    COUNT(DISTINCT category) AS distinct_categories,
    ROUND(SUM(item_revenue), 2) AS product_revenue,
    ROUND(AVG(item_revenue), 2) AS average_item_revenue,
    ROUND(AVG(avg_review_score), 2) AS average_review_score,
    ROUND(100 * AVG(is_late_delivery), 2) AS late_delivery_rate_pct
FROM read_csv_auto('data/processed/fact_order_items_delivered.csv')
GROUP BY seller_id, seller_state, seller_city
ORDER BY product_revenue DESC;

COPY seller_performance
TO 'data/processed/seller_performance.csv'
WITH (HEADER, DELIMITER ',');
