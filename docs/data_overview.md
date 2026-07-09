# Olist Dataset Overview

## Objetivo de esta revision

Antes de calcular KPIs, revisamos la estructura del dataset para entender:

- que representa cada tabla,
- cual es su nivel de detalle,
- que llaves permiten unirlas,
- que problemas de calidad pueden afectar el analisis.

## Tablas disponibles

| Archivo | Filas | Columnas | Nivel de detalle |
| --- | ---: | ---: | --- |
| `olist_orders_dataset.csv` | 99,441 | 8 | Una fila por orden |
| `olist_customers_dataset.csv` | 99,441 | 5 | Una fila por `customer_id` |
| `olist_order_items_dataset.csv` | 112,650 | 7 | Una fila por item dentro de una orden |
| `olist_order_payments_dataset.csv` | 103,886 | 5 | Una fila por pago o secuencia de pago |
| `olist_order_reviews_dataset.csv` | 99,224 | 7 | Una fila por review |
| `olist_products_dataset.csv` | 32,951 | 9 | Una fila por producto |
| `olist_sellers_dataset.csv` | 3,095 | 4 | Una fila por vendedor |
| `product_category_name_translation.csv` | 71 | 2 | Una fila por categoria traducida |
| `olist_geolocation_dataset.csv` | 1,000,163 | 5 | Multiples coordenadas por prefijo postal |

## Llaves principales

| Tabla | Llave principal o candidata | Resultado |
| --- | --- | --- |
| Orders | `order_id` | Sin duplicados |
| Customers | `customer_id` | Sin duplicados |
| Products | `product_id` | Sin duplicados |
| Sellers | `seller_id` | Sin duplicados |
| Category translation | `product_category_name` | Sin duplicados |

## Relaciones importantes

```text
customers.customer_id
  -> orders.customer_id

orders.order_id
  -> order_items.order_id
  -> order_payments.order_id
  -> order_reviews.order_id

order_items.product_id
  -> products.product_id

order_items.seller_id
  -> sellers.seller_id

products.product_category_name
  -> product_category_name_translation.product_category_name
```

## Puntos clave para el analisis

### 1. `customer_id` no es lo mismo que `customer_unique_id`

- `customer_id` identifica una compra o relacion puntual con una orden.
- `customer_unique_id` identifica al cliente de forma mas estable.
- Hay 96,096 clientes unicos y 2,997 clientes tienen mas de un `customer_id`.

Implicacion: para recurrencia de clientes usaremos `customer_unique_id`, no `customer_id`.

### 2. No todas las ordenes fueron entregadas

Distribucion de `order_status`:

| Estado | Ordenes |
| --- | ---: |
| delivered | 96,478 |
| shipped | 1,107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

Implicacion: los KPIs comerciales principales deben usar ordenes `delivered`, para no mezclar ventas completadas con ordenes canceladas, no disponibles o en proceso.

### 3. Las tablas de items, pagos y reviews tienen multiples filas por orden

| Tabla | Filas | Ordenes unicas | Maximo de filas por orden |
| --- | ---: | ---: | ---: |
| Items | 112,650 | 98,666 | 21 |
| Payments | 103,886 | 99,440 | 29 |
| Reviews | 99,224 | 98,673 | 3 |

Implicacion: no debemos unir estas tablas directamente y luego sumar sin cuidado, porque se puede duplicar revenue o pagos. Primero hay que agregarlas al nivel de orden.

### 4. Hay nulos esperados en algunas columnas

| Tabla | Campo | Nulos | Lectura |
| --- | --- | ---: | --- |
| Orders | `order_delivered_customer_date` | 2,965 | Ordenes no entregadas o sin fecha final |
| Orders | `order_delivered_carrier_date` | 1,783 | Ordenes sin salida registrada |
| Orders | `order_approved_at` | 160 | Ordenes sin aprobacion registrada |
| Reviews | `review_comment_title` | 87,656 | Comentarios opcionales |
| Reviews | `review_comment_message` | 58,247 | Comentarios opcionales |
| Products | `product_category_name` | 610 | Productos sin categoria |

Implicacion: los nulos de comentarios no son un problema para el analisis cuantitativo. Los nulos de fechas importan para metricas de entrega. Los productos sin categoria deben agruparse como `unknown` o excluirse segun el analisis.

### 5. Geolocation no esta a nivel unico por codigo postal

- `olist_geolocation_dataset.csv` tiene 1,000,163 filas.
- Hay 19,015 prefijos postales unicos.
- Existen 261,831 filas exactamente duplicadas.
- Muchos prefijos postales tienen multiples coordenadas.

Implicacion: para mapas o analisis geografico, primero hay que agregar por prefijo postal, por ejemplo usando latitud y longitud promedio. Para el primer dashboard no es obligatorio usar esta tabla.

## Reglas iniciales de modelado

1. Analizar ventas con ordenes `delivered`.
2. Medir clientes con `customer_unique_id`.
3. Calcular revenue desde `order_items.price`.
4. Mantener `freight_value` separado de revenue de producto.
5. Agregar items, pagos y reviews al nivel de orden antes de unirlos.
6. Tratar categorias faltantes como `unknown`.
7. Usar geolocation solo despues de agregar por prefijo postal.

## Proximo paso

Definir el caso de negocio y los KPIs principales antes de escribir consultas finales.
