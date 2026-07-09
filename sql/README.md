# SQL Layer

Esta carpeta contiene consultas SQL reproducibles usando DuckDB.

La estrategia del proyecto es construir tablas analiticas limpias antes de usarlas en notebooks o Streamlit. Esto ayuda a que las metricas cuadren entre SQL, Python y dashboard.

Orden sugerido:

1. `01_create_order_base.sql`: crea una tabla a nivel orden entregada.
2. `02_validate_order_base.sql`: valida grano, reconciliacion y KPIs base.
3. `03_create_order_items_base.sql`: crea una tabla a nivel item vendido.
4. `04_validate_order_items_base.sql`: valida grano, reconciliacion y categorias.
5. `05_business_question_outputs.sql`: crea datasets agregados para notebook y dashboard.

## Como ejecutar una consulta SQL con DuckDB desde Python

Desde la raiz del proyecto:

```bash
source .venv/bin/activate
python -c "import duckdb; con = duckdb.connect(); con.execute(open('sql/01_create_order_base.sql').read())"
```

El resultado se guarda en:

```text
data/processed/fact_orders_delivered.csv
```

Para ejecutar las validaciones:

```bash
python -c "import duckdb; con = duckdb.connect(); con.execute(open('sql/02_validate_order_base.sql').read())"
```

Para crear la tabla de items:

```bash
python -c "import duckdb; con = duckdb.connect(); con.execute(open('sql/03_create_order_items_base.sql').read())"
```

Para crear los outputs de negocio:

```bash
python -c "import duckdb; con = duckdb.connect(); con.execute(open('sql/05_business_question_outputs.sql').read())"
```
