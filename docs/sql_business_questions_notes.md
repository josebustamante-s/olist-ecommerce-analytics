# SQL Step 05 - Business Question Outputs

## Que estamos construyendo

Creamos datasets agregados que responden las preguntas principales del proyecto y que despues alimentaran el notebook y el dashboard Streamlit.

El archivo SQL es:

```text
sql/05_business_question_outputs.sql
```

## Por que no hacer todo directamente en Streamlit

Streamlit debe enfocarse en mostrar, filtrar e interactuar con datos ya preparados.

Si dejamos demasiada logica de negocio dentro de la app, el dashboard se vuelve mas dificil de mantener y mas propenso a inconsistencias. Por eso preparamos extractos agregados desde SQL.

## Outputs generados

| Archivo | Pregunta que responde |
| --- | --- |
| `kpi_summary.csv` | Cuales son los KPIs principales del negocio? |
| `monthly_sales.csv` | Como evolucionan revenue, ordenes y AOV por mes? |
| `weekly_sales.csv` | Como se mueve la demanda semana a semana? |
| `category_performance.csv` | Que categorias concentran revenue, volumen y satisfaccion? |
| `category_monthly_sales.csv` | Como evoluciona cada categoria por mes? |
| `customer_lifetime.csv` | Cuanto compra cada cliente y si vuelve a comprar? |
| `customer_frequency_summary.csv` | Como se distribuye la recurrencia de clientes? |
| `customer_state_summary.csv` | Que estados concentran revenue, clientes y problemas de entrega? |
| `delivery_satisfaction.csv` | Como cambia la satisfaccion segun atraso o adelanto de entrega? |
| `payment_summary.csv` | Como se comportan metodo de pago, cuotas y ticket promedio? |
| `seller_performance.csv` | Que sellers concentran revenue y que riesgo de calidad presentan? |

## Decisiones importantes

Los outputs usan dos tablas base:

```text
fact_orders_delivered
fact_order_items_delivered
```

Cuando la pregunta es de ordenes, clientes, fechas o entrega, usamos `fact_orders_delivered`.

Cuando la pregunta es de categorias, productos o sellers, usamos `fact_order_items_delivered`.

Esta separacion evita mezclar granos y ayuda a que los totales cuadren.

## Segmentos creados

### Frecuencia de clientes

`customer_lifetime.csv` clasifica clientes en:

- `1 order`
- `2 orders`
- `3 orders`
- `4+ orders`

Esto permite mostrar recurrencia sin crear un modelo demasiado complejo en la primera version.

### Valor de clientes

Tambien se crea un segmento simple de valor:

- `low_value`: revenue menor a 150
- `mid_value`: revenue entre 150 y 499.99
- `high_value`: revenue desde 500

Estos cortes son exploratorios. En el EDA podremos ajustarlos si la distribucion muestra que otros umbrales son mas utiles.

### Entrega

`delivery_satisfaction.csv` agrupa ordenes segun atraso o adelanto frente a la fecha estimada. Esto permite comparar review score con una lectura operacional mas clara que mirar dias individuales.

## Como se usara en el dashboard

| Tab del dashboard | Datasets principales |
| --- | --- |
| Executive Overview | `kpi_summary`, `monthly_sales`, `category_performance` |
| Sales and Categories | `category_performance`, `category_monthly_sales` |
| Customers | `customer_lifetime`, `customer_frequency_summary`, `customer_state_summary` |
| Delivery and Satisfaction | `delivery_satisfaction`, `customer_state_summary` |
| Seller Risk v2 | `seller_performance` |

## Validaciones esperadas

Despues de ejecutar el SQL deberiamos revisar:

- que todos los CSV se generen en `data/processed/`;
- que `monthly_sales` tenga 23 meses;
- que `weekly_sales` tenga 91 semanas;
- que `category_performance` mantenga el mismo revenue total que `fact_order_items_delivered`;
- que `customer_lifetime` tenga 93,358 clientes unicos;
- que `kpi_summary` mantenga los KPIs base ya validados.

## Resultados de validacion

Validaciones ejecutadas despues de generar los outputs:

| Check | Resultado |
| --- | --- |
| Archivos CSV generados en `data/processed/` | 13 |
| Meses en `monthly_sales` | 23 |
| Revenue total en `monthly_sales` | 13,221,498.11 |
| Semanas en `weekly_sales` | 91 |
| Revenue total en `weekly_sales` | 13,221,498.11 |
| Categorias en `category_performance` | 74 |
| Revenue total en `category_performance` | 13,221,498.11 |
| Clientes en `customer_lifetime` | 93,358 |
| Clientes recurrentes | 2,801 |
| Repeat customer rate | 3.00% |

KPIs principales desde `kpi_summary.csv`:

| KPI | Valor |
| --- | ---: |
| Ordenes entregadas | 96,478 |
| Product revenue | 13,221,498.11 |
| Average order value | 137.04 |
| Clientes unicos | 93,358 |
| Average review score | 4.16 |
| Late delivery rate | 8.11% |
| Average delivery days | 12.50 |

Lectura preliminar de entrega y satisfaccion:

| Segmento de entrega | Ordenes | Review promedio |
| --- | ---: | ---: |
| 7+ days early | 76,140 | 4.31 |
| 1-6 days early | 12,504 | 4.18 |
| on estimate | 1,292 | 4.04 |
| 1-3 days late | 1,870 | 3.29 |
| 4-7 days late | 1,802 | 2.11 |
| 8+ days late | 2,870 | 1.71 |

Esta ultima tabla ya sugiere una historia fuerte para el dashboard: las entregas tardias tienen una caida clara en review score. Se tratara como hallazgo preliminar hasta confirmarlo en el EDA.
