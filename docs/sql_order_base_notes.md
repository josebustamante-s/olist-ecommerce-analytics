# SQL Step 01 - Order Base

## Que estamos construyendo

Creamos una tabla llamada `fact_orders_delivered` con una fila por orden entregada.

El archivo generado queda en:

```text
data/processed/fact_orders_delivered.csv
```

## Por que partimos por esta tabla

En Olist, no todas las tablas tienen el mismo nivel de detalle:

- `orders`: una fila por orden.
- `order_items`: una o varias filas por orden.
- `order_payments`: una o varias filas por orden.
- `order_reviews`: una o mas filas por orden.

Si unimos todo directamente y despues sumamos, podemos duplicar revenue. Por eso primero agregamos cada tabla al nivel de `order_id`.

## Que decisiones de negocio se aplican

1. Solo usamos ordenes `delivered` para KPIs comerciales.
2. Revenue principal = suma de `order_items.price`.
3. Flete se mantiene separado como `freight_value`.
4. Pagos se usan para reconciliacion, no como revenue principal.
5. Cliente recurrente se calculara despues usando `customer_unique_id`.

## Bloques principales del SQL

| Bloque | Proposito |
| --- | --- |
| `delivered_orders` | Filtra ordenes completadas y convierte fechas con `CAST(... AS TIMESTAMP)` |
| `customer_dim` | Selecciona identificadores y geografia del cliente |
| `item_summary` | Usa `GROUP BY order_id` para resumir items, productos, sellers, revenue y flete por orden |
| `payment_ranked` | Usa `ROW_NUMBER() OVER (...)` para ordenar tipos de pago dentro de cada orden |
| `payment_summary` | Usa `GROUP BY order_id` para resumir pago total, cuotas y cantidad de tipos de pago |
| `main_payment_type` | Filtra `payment_type_rank = 1` para seleccionar el tipo de pago dominante |
| `review_summary` | Usa `AVG`, `MIN`, `MAX` y `CASE WHEN` para resumir reviews |
| `SELECT final` | Une todo con `LEFT JOIN` manteniendo una fila por orden entregada |

## Funciones y conceptos SQL usados

Estas son las piezas tecnicas mas importantes que aparecen en el SQL. No es necesario memorizarlas ahora, pero si conviene entender que problema resuelve cada una dentro del flujo.

| Concepto | Donde aparece | Que aporta al analisis |
| --- | --- | --- |
| `WITH` / CTE | Todo el script | Permite escribir la transformacion en pasos legibles |
| `CAST(... AS TIMESTAMP)` | Fechas de orden | Deja las fechas listas para calculos temporales |
| `GROUP BY` | `item_summary`, `payment_summary`, `review_summary` | Lleva tablas de muchas filas por orden a una fila por orden |
| `SUM` | Revenue, flete, pagos | Calcula montos totales |
| `COUNT(*)` | Items, pagos, reviews | Cuenta registros asociados a cada orden |
| `COUNT(DISTINCT ...)` | Productos, sellers, tipos de pago | Evita contar repetidos cuando importa la cantidad de entidades distintas |
| `AVG`, `MIN`, `MAX` | Reviews y precios | Resume variables numericas |
| `ROW_NUMBER() OVER (...)` | `payment_ranked` | Identifica el metodo de pago dominante dentro de cada orden |
| `CASE WHEN` | Atraso y comentario | Convierte reglas de negocio en variables analizables |
| `COALESCE` | `SELECT final` | Evita que campos numericos queden nulos cuando falta informacion secundaria |
| `DATE_TRUNC` | Semana y mes de compra | Crea fechas agrupables para tendencias |
| `DATE_DIFF` | Duracion y atraso de entrega | Calcula tiempos entre eventos |
| `COPY ... TO` | Export final | Guarda la tabla procesada como CSV |

## Como pensar las uniones

El objetivo de `fact_orders_delivered` es tener una fila por cada orden entregada.

Por eso la tabla principal es `delivered_orders`. Desde ahi incorporamos datos de clientes, items, pagos y reviews sin cambiar el numero de ordenes. En SQL esto se implementa con `LEFT JOIN`.

En la practica, eso significa:

- si una orden no tiene review, la orden igual queda en la tabla;
- si una orden tiene informacion de pago faltante, la orden igual queda en la tabla;
- si una orden no encuentra algun dato secundario, no perdemos la venta.

Un `INNER JOIN` seria mas restrictivo: solo conservaria ordenes que tengan match en ambas tablas. Eso es util para algunas validaciones, pero no para construir la base principal del dashboard.

En la validacion de revenue, por ejemplo, si usamos `INNER JOIN` es porque queremos comparar especificamente items que pertenecen a ordenes entregadas. Ahi la restriccion si tiene sentido.


## Que deberiamos validar despues de ejecutar

- La tabla debe tener 96,478 filas, una por orden entregada.
- `order_id` no debe tener duplicados.
- La suma de `product_revenue` debe cuadrar con revenue de items entregados.
- La suma de `freight_value` debe cuadrar con flete de items entregados.
- `avg_review_score` puede tener nulos porque no todas las ordenes tienen review.

## Por que no incluimos categoria todavia

Una orden puede tener varios productos y potencialmente varias categorias.

Si metemos `category` directamente en esta tabla, podriamos forzar una categoria unica para una orden que tiene varias. Eso simplifica el dashboard, pero puede distorsionar el analisis.

La categoria se trabajara en una tabla separada a nivel item o categoria.

## Resultados de validacion

Validaciones ejecutadas con `sql/02_validate_order_base.sql`:

| Check | Resultado |
| --- | --- |
| Filas en tabla base | 96,478 |
| Ordenes distintas | 96,478 |
| Filas duplicadas por `order_id` | 0 |
| Diferencia vs ordenes entregadas raw | 0 |
| Diferencia en `product_revenue` vs raw | 0.00 |
| Diferencia en `freight_value` vs raw | 0.00 |
| Nulos en campos criticos | 0 |

KPIs base preliminares:

| KPI | Valor |
| --- | ---: |
| Product revenue | 13,221,498.11 |
| Average order value | 137.04 |
| Clientes unicos | 93,358 |
| Average review score | 4.16 |
| Late delivery rate | 8.11% |
| Periodo | 2016-09-15 a 2018-08-29 |
