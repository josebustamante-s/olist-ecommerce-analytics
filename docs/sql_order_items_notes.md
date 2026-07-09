# SQL Step 03 - Order Items Base

## Que estamos construyendo

Creamos una tabla llamada `fact_order_items_delivered` con una fila por item vendido en una orden entregada.

El archivo generado queda en:

```text
data/processed/fact_order_items_delivered.csv
```

## Por que necesitamos esta segunda tabla

La tabla `fact_orders_delivered` tiene una fila por orden. Es ideal para KPIs generales como ordenes, clientes, AOV, recurrencia y entrega.

Pero las categorias, productos y sellers viven a nivel item. Una misma orden puede tener mas de un producto y mas de una categoria. Si forzaramos categoria dentro de la tabla de ordenes, simplificariamos el modelo pero podriamos distorsionar el analisis.

Por eso usamos dos tablas:

```text
fact_orders_delivered       -> una fila por orden
fact_order_items_delivered  -> una fila por item vendido
```

## Decisiones de modelado

1. Solo incluimos items que pertenecen a ordenes entregadas.
2. El revenue de categoria se calcula con `item_revenue`, que viene de `order_items.price`.
3. El flete de categoria se calcula con `item_freight_value`.
4. Las categorias faltantes o sin traduccion se agrupan como `unknown`.
5. Se agrega contexto de la orden, como fecha, estado del cliente, entrega, pago y review, para poder filtrar el dashboard.

## Como pensar las uniones

La tabla parte desde `olist_order_items_dataset.csv` porque ese es el nivel de detalle que queremos conservar.

Despues se une con `fact_orders_delivered` usando `INNER JOIN`. Esto deja solo items de ordenes entregadas, manteniendo coherencia con los KPIs comerciales del proyecto.

Luego se incorporan producto y seller con `LEFT JOIN`. Es preferible conservar el item aunque falte algun dato descriptivo de producto o seller, porque perder items alteraria el revenue.

## Bloques principales del SQL

| Bloque | Proposito |
| --- | --- |
| `delivered_orders` | Trae contexto de orden desde la tabla procesada anterior |
| `product_dim` | Agrega categoria traducida y atributos del producto |
| `seller_dim` | Agrega ubicacion del seller |
| `SELECT final` | Une items con orden, producto y seller |

## Funciones y conceptos SQL usados

| Concepto | Donde aparece | Que aporta al analisis |
| --- | --- | --- |
| `INNER JOIN` | Items con ordenes entregadas | Filtra el universo a ventas completadas |
| `LEFT JOIN` | Productos y sellers | Agrega descripciones sin perder items |
| `COALESCE` | Categoria | Evita categorias nulas, agrupandolas como `unknown` |
| `CASE WHEN` | Freight share | Evita dividir por cero |
| `ROUND` | Freight share | Deja proporciones con una precision razonable |
| `COPY ... TO` | Export final | Guarda la tabla procesada como CSV |

## Que deberiamos validar despues de ejecutar

- El identificador `order_id + order_item_id` no debe tener duplicados.
- La cantidad de items debe cuadrar con los items de ordenes entregadas.
- La suma de `item_revenue` debe cuadrar con `order_items.price` filtrado a ordenes entregadas.
- La suma de `item_freight_value` debe cuadrar con `order_items.freight_value` filtrado a ordenes entregadas.
- Las categorias `unknown` deben existir solo cuando falte categoria o traduccion.

## Resultados de validacion

Validaciones ejecutadas con `sql/04_validate_order_items_base.sql`:

| Check | Resultado |
| --- | --- |
| Filas en tabla base | 110,197 |
| Items distintos por `order_id + order_item_id` | 110,197 |
| Filas duplicadas por item | 0 |
| Diferencia vs items raw de ordenes entregadas | 0 |
| Diferencia en `item_revenue` vs raw | 0.00 |
| Diferencia en `item_freight_value` vs raw | 0.00 |
| Nulos en campos criticos | 0 |
| Items con categoria `unknown` | 1,537 |
| Categorias distintas | 74 |
| Productos distintos | 32,216 |
| Sellers distintos | 2,970 |

Top categorias preliminares por revenue:

| Categoria | Revenue | Ordenes | Items vendidos | Review promedio |
| --- | ---: | ---: | ---: | ---: |
| health_beauty | 1,233,131.72 | 8,647 | 9,465 | 4.19 |
| watches_gifts | 1,166,176.98 | 5,495 | 5,859 | 4.07 |
| bed_bath_table | 1,023,434.76 | 9,272 | 10,953 | 3.92 |
| sports_leisure | 954,852.55 | 7,530 | 8,431 | 4.17 |
| computers_accessories | 888,724.61 | 6,530 | 7,644 | 3.99 |

Estos valores son preliminares. Sirven para validar que la tabla responde preguntas comerciales, pero los hallazgos finales se documentaran despues del EDA.
