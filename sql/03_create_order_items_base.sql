-- Olist E-commerce Analytics
-- Paso 03: construir una tabla analitica a nivel item vendido.
--
-- La tabla de ordenes ya nos permite medir KPIs generales. Para responder
-- preguntas de categorias, productos y sellers necesitamos mantener el nivel
-- de detalle de cada item dentro de una orden entregada.
--
-- Dialecto SQL: DuckDB
-- Ejecutar desde la raiz del proyecto, despues de crear fact_orders_delivered.

CREATE OR REPLACE TABLE fact_order_items_delivered AS

WITH delivered_orders AS (
    -- Reutilizamos la tabla procesada a nivel orden para asegurar que los
    -- filtros de estado, fechas, cliente, pago, entrega y review sean los
    -- mismos en todo el proyecto.
    SELECT
        order_id,
        customer_unique_id,
        customer_city,
        customer_state,
        purchase_ts,
        purchase_date,
        purchase_week,
        purchase_month,
        purchase_year,
        purchase_month_number,
        delivery_days,
        delivery_delay_days,
        is_late_delivery,
        delivery_status,
        main_payment_type,
        max_payment_installments,
        avg_review_score
    FROM read_csv_auto('data/processed/fact_orders_delivered.csv')
),

product_dim AS (
    -- Enriquecemos productos con la traduccion de categoria.
    -- Cuando falta traduccion o categoria, usamos 'unknown' para que esos
    -- items no desaparezcan de los totales.
    SELECT
        p.product_id,
        COALESCE(p.product_category_name, 'unknown') AS product_category_name,
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'unknown'
        ) AS product_category_name_english,
        p.product_name_lenght,
        p.product_description_lenght,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM read_csv_auto('olist_products_dataset.csv') AS p
    LEFT JOIN read_csv_auto('product_category_name_translation.csv') AS t
        ON p.product_category_name = t.product_category_name
),

seller_dim AS (
    -- Agregamos ubicacion del seller para poder analizar concentracion y
    -- desempeno por estado vendedor.
    SELECT
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    FROM read_csv_auto('olist_sellers_dataset.csv')
)

SELECT
    -- Identificadores del item y sus entidades relacionadas
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_unique_id,

    -- Fechas y dimensiones de la orden
    o.purchase_ts,
    o.purchase_date,
    o.purchase_week,
    o.purchase_month,
    o.purchase_year,
    o.purchase_month_number,
    o.customer_city,
    o.customer_state,

    -- Producto y categoria
    p.product_category_name,
    p.product_category_name_english AS category,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,

    -- Seller
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state,

    -- Metricas del item
    oi.shipping_limit_date,
    oi.price AS item_revenue,
    oi.freight_value AS item_freight_value,
    CASE
        WHEN oi.price + oi.freight_value = 0 THEN NULL
        ELSE ROUND(oi.freight_value / (oi.price + oi.freight_value), 4)
    END AS item_freight_share,

    -- Contexto de experiencia y pago desde la orden
    o.delivery_days,
    o.delivery_delay_days,
    o.is_late_delivery,
    o.delivery_status,
    o.main_payment_type,
    o.max_payment_installments,
    o.avg_review_score
FROM read_csv_auto('olist_order_items_dataset.csv') AS oi
INNER JOIN delivered_orders AS o
    ON oi.order_id = o.order_id
LEFT JOIN product_dim AS p
    ON oi.product_id = p.product_id
LEFT JOIN seller_dim AS s
    ON oi.seller_id = s.seller_id;

-- Exportamos la tabla para usarla en el notebook y en las visualizaciones
-- de categoria, producto y seller del dashboard.
COPY fact_order_items_delivered
TO 'data/processed/fact_order_items_delivered.csv'
WITH (HEADER, DELIMITER ',');
