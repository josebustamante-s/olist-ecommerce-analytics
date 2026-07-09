# Project Brief - Olist E-commerce Analytics

## Rol del proyecto en el portafolio

Este proyecto debe demostrar que el analista puede transformar datos transaccionales crudos en un caso de negocio claro, reproducible y accionable.

El objetivo no es solo mostrar graficos de ventas. El objetivo es construir una lectura completa de un marketplace e-commerce:

1. como crecen las ventas,
2. que categorias y regiones concentran valor,
3. que tan recurrentes son los clientes,
4. como la experiencia de entrega se relaciona con satisfaccion,
5. que acciones comerciales u operacionales se pueden priorizar.

## Objetivo final

Analizar el desempeno comercial de Olist usando datos de ordenes, clientes, productos, pagos, vendedores y reviews para identificar patrones de compra, oportunidades de crecimiento, concentracion de valor y riesgos operacionales que puedan afectar recurrencia y satisfaccion.

## Audiencia del dashboard

El dashboard estara pensado para un perfil de negocio/BI:

- reclutadores que quieren evaluar habilidades de Data Analyst,
- stakeholders comerciales que quieren entender ventas y clientes,
- equipo operacional que quiere detectar problemas de entrega y satisfaccion.

## Benchmark de proyectos revisados

Se revisaron proyectos publicos de referencia con el dataset Olist:

- [Vinayak16-coder/Olist-Ecommerce-PowerBI-Dashboard](https://github.com/Vinayak16-coder/Olist-Ecommerce-PowerBI-Dashboard)
- [srishnagar/olist_ecommerce_dashboard](https://github.com/srishnagar/olist_ecommerce_dashboard)
- [abhishekbhagat685/Olist-Ecommerce-Dashboard](https://github.com/abhishekbhagat685/Olist-Ecommerce-Dashboard)
- [gcapart/olist-ecommerce-powerbi-dashboard](https://github.com/gcapart/olist-ecommerce-powerbi-dashboard)

Patrones comunes encontrados:

- dashboards separados por ventas, clientes, logistica, vendedores y productos,
- KPIs como revenue, ordenes, AOV, clientes, review score y delivery days,
- mucho foco en Power BI y capturas,
- algunos repos suben CSV crudos o solo el archivo `.pbix`,
- pocos explican con precision el modelo de datos, las decisiones de metrica o el riesgo de duplicar revenue al unir items, pagos y reviews.

Decision para nuestro proyecto:

- mantener el dashboard interactivo en Streamlit + Plotly,
- documentar SQL y definiciones de metricas,
- no subir CSV crudos al repo,
- mostrar el razonamiento analitico, no solo el resultado visual,
- incluir un README tipo caso de negocio con recomendaciones.

## Pregunta central del proyecto

> Donde deberia enfocar Olist sus esfuerzos comerciales y operacionales para crecer de forma rentable, mejorar recurrencia y proteger la satisfaccion del cliente?

Esta pregunta es mejor que "como evolucionan las ventas" porque obliga a conectar ventas, clientes, categorias, logistica y satisfaccion.

## Preguntas de negocio recomendadas

| Prioridad | Pregunta | Por que importa | Visualizacion sugerida |
| --- | --- | --- | --- |
| Alta | Como evolucionaron revenue, ordenes y ticket promedio en el tiempo? | Da contexto de crecimiento, estacionalidad y cambios de demanda. | Line chart mensual + barras semanales opcionales |
| Alta | Que categorias generan mas revenue y volumen? | Permite priorizar categorias comerciales y detectar mix de productos. | Barras horizontales top N + Pareto |
| Alta | Que tan recurrentes son los clientes? | La recurrencia es clave para crecimiento sostenible y marketing lifecycle. | KPI de repeat rate + barras por frecuencia de compra |
| Alta | Que segmentos simples concentran mas valor? | Ayuda a separar compradores unicos, recurrentes y alto valor. | Matriz o barras por segmento RFM simple |
| Alta | Como se relacionan entrega tardia y review score? | Conecta operaciones con satisfaccion y riesgo de retencion. | Boxplot/barra de review por segmento de delay |
| Media | Que estados concentran revenue, clientes y problemas de entrega? | Muestra concentracion geografica y oportunidades/regiones con friccion. | Barras por estado; mapa opcional en version 2 |
| Media | Que vendedores concentran revenue y como es su calidad? | Marketplace depende de sellers; volumen sin calidad puede ser riesgoso. | Scatter revenue vs review score por seller |
| Media | Que metodos de pago predominan y como se relacionan con AOV? | Ayuda a entender comportamiento de checkout y ticket. | Barras por payment type + AOV por installments |
| Baja | Que productos individuales generan mas revenue? | Product IDs son anonimos; sirve menos para negocio que categorias. | Tabla top productos dentro de categoria |
| Baja | Que dicen los comentarios de reviews? | Los comentarios son incompletos y en portugues; puede ser version futura. | Word cloud o NLP futuro, no en v1 |

## KPIs principales

### KPI primarios

| KPI | Definicion | Fuente |
| --- | --- | --- |
| Product revenue | Suma de `order_items.price` para ordenes entregadas | `orders`, `order_items` |
| Ordenes entregadas | Count distinct `order_id` con `order_status = 'delivered'` | `orders` |
| Average order value | Product revenue / ordenes entregadas | `orders`, `order_items` |
| Clientes unicos | Count distinct `customer_unique_id` | `customers`, `orders` |
| Repeat customer rate | Clientes con mas de una orden entregada / clientes unicos | `customers`, `orders` |
| Average review score | Promedio de `review_score` en ordenes entregadas | `reviews`, `orders` |
| Late delivery rate | Ordenes entregadas despues de la fecha estimada / ordenes entregadas | `orders` |

### Metricas diagnosticas

| Metrica | Uso |
| --- | --- |
| Revenue por categoria | Priorizar categorias comerciales |
| Ordenes por categoria | Separar volumen de ticket |
| AOV por categoria | Detectar categorias premium |
| Freight share | Entender peso del costo de envio |
| Delivery days | Evaluar eficiencia operacional |
| Delay days | Medir atraso contra promesa |
| Revenue por estado | Ver concentracion geografica |
| Review score por estado/categoria/seller | Detectar riesgo de experiencia |
| Installment segment | Ver si tickets altos se financian en mas cuotas |

## Reglas de medicion

1. Los KPIs comerciales principales usaran solo ordenes `delivered`.
2. Revenue principal sera `order_items.price`, no `payment_value`.
3. `payment_value` se usara como metrica secundaria porque incluye pagos y puede mezclar componentes como flete.
4. `freight_value` se analizara separado de product revenue.
5. Recurrencia se calculara con `customer_unique_id`.
6. Items, pagos y reviews se agregaran primero a nivel `order_id` antes de unirlos.
7. Categorias sin traduccion se marcaran como `unknown`.
8. Productos individuales se trataran con cuidado porque el dataset no trae nombres comerciales, solo IDs.

## Diseno recomendado del dashboard Streamlit

### Filtros globales

- Rango de fechas.
- Estado del cliente.
- Categoria.
- Tipo de pago.
- Segmento de entrega: on-time vs late.

Mantener pocos filtros evita que el dashboard se vuelva dificil de leer. Los filtros deben afectar la mayoria de visualizaciones.

### Pagina o tab 1 - Executive Overview

Pregunta: como esta performando el negocio?

Visuales:

- KPI cards: product revenue, ordenes, AOV, clientes unicos, repeat rate, avg review score.
- Line chart: revenue mensual.
- Combo chart: ordenes y AOV mensual.
- Barras: top 10 categorias por revenue.
- Mini tabla: principales alertas comerciales/operacionales.

### Pagina o tab 2 - Sales and Category Performance

Pregunta: que categorias explican el crecimiento y el mix de ventas?

Visuales:

- Barras horizontales: revenue por categoria.
- Pareto: concentracion de revenue por categoria.
- Scatter: AOV vs ordenes por categoria.
- Tabla: top categorias con revenue, ordenes, AOV, freight share y review score.

### Pagina o tab 3 - Customer Behavior

Pregunta: los clientes vuelven a comprar y donde se concentra el valor?

Visuales:

- KPI: repeat customer rate.
- Barras: clientes por frecuencia de compra.
- Barras: revenue por segmento de frecuencia.
- RFM simple: nuevo/unico, recurrente, alto valor.
- Barras por estado: clientes y revenue.

### Pagina o tab 4 - Delivery and Satisfaction

Pregunta: que fricciones operacionales afectan la satisfaccion?

Visuales:

- KPI cards: late delivery rate, avg delivery days, avg review score.
- Barras: review score por segmento de delay.
- Boxplot o barras: delivery days por estado.
- Scatter: delivery days vs review score por estado o categoria.
- Tabla: estados/categorias con alto revenue y bajo review score.

### Pagina o tab 5 - Seller and Marketplace Risk

Pregunta: que sellers concentran valor y donde hay riesgo de calidad?

Visuales:

- Scatter: seller revenue vs avg review score, tamano por ordenes.
- Barras: top sellers por revenue.
- Barras: revenue por seller state.
- Tabla: sellers de alto revenue con baja satisfaccion o alta tardanza.

Esta tab puede ser v2 si la primera version queda muy amplia.

## Roadmap del proyecto

### Version 1 - Portfolio solido

- SQL documentado.
- Notebook EDA.
- Streamlit dashboard con 4 tabs:
  - Executive Overview
  - Sales and Categories
  - Customers
  - Delivery and Satisfaction
- README con capturas, link publico y recomendaciones.

### Version 2 - Diferenciacion

- Tab de seller risk.
- Mapa geografico por estado o prefijo postal agregado.
- Segmentacion RFM mas completa.
- Analisis basico de texto de reviews en portugues.

## Entregables finales

| Entregable | Proposito |
| --- | --- |
| SQL documentado | Demostrar joins, agregaciones y definicion de metricas |
| Notebook EDA | Mostrar limpieza, validacion y exploracion |
| Streamlit app | Permitir que reclutadores interactuen online |
| README caso de negocio | Contar problema, metodologia, hallazgos y recomendaciones |
| Capturas del dashboard | Permitir revision rapida desde GitHub |

## Fuentes externas revisadas

- [Kaggle: Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [GitHub: Vinayak16-coder/Olist-Ecommerce-PowerBI-Dashboard](https://github.com/Vinayak16-coder/Olist-Ecommerce-PowerBI-Dashboard)
- [GitHub: srishnagar/olist_ecommerce_dashboard](https://github.com/srishnagar/olist_ecommerce_dashboard)
- [GitHub: abhishekbhagat685/Olist-Ecommerce-Dashboard](https://github.com/abhishekbhagat685/Olist-Ecommerce-Dashboard)
- [GitHub: gcapart/olist-ecommerce-powerbi-dashboard](https://github.com/gcapart/olist-ecommerce-powerbi-dashboard)
- [Streamlit documentation: Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)
