"""Create the first EDA notebook for the Olist portfolio project.

Se usa JSON minimo compatible con Jupyter para evitar depender de imports
pesados durante la generacion del archivo.
"""

from __future__ import annotations

import json
from textwrap import dedent
from uuid import uuid4
from pathlib import Path


NOTEBOOK_PATH = Path("notebooks/01_eda_olist.ipynb")


def _lines(source: str) -> list[str]:
    return [line + "\n" for line in dedent(source).strip().splitlines()]


def markdown(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": uuid4().hex[:8],
        "metadata": {},
        "source": _lines(source),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "id": uuid4().hex[:8],
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _lines(source),
    }


nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

nb["cells"] = [
    markdown(
        """
        # EDA Olist - ventas, clientes y experiencia

        Este notebook valida los outputs SQL creados previamente y explora las primeras historias que podrian convertirse en dashboard.

        La intencion es mantener una lectura clara:

        1. revisar que los datos procesados cargan correctamente;
        2. validar KPIs principales;
        3. explorar ventas en el tiempo;
        4. analizar categorias;
        5. revisar recurrencia de clientes;
        6. conectar entrega y satisfaccion.
        """
    ),
    markdown(
        """
        ## tl;dr

        Este resumen se basa en las celdas ejecutadas del notebook:

        - El dataset procesado contiene 96,478 ordenes entregadas entre 2016-09-15 y 2018-08-29.
        - El product revenue total es 13.22M y el ticket promedio es 137.04.
        - La recurrencia es baja: 2,801 clientes recurrentes sobre 93,358 clientes unicos, equivalente a 3.00%.
        - Las categorias con mayor revenue son `health_beauty`, `watches_gifts`, `bed_bath_table`, `sports_leisure` y `computers_accessories`.
        - La entrega tardia parece afectar fuertemente la satisfaccion: ordenes con 8+ dias de atraso tienen review promedio 1.71.

        Estos puntos son hallazgos preliminares. Las recomendaciones finales se escribiran despues de revisar visualizaciones y construir el dashboard.
        """
    ),
    markdown(
        """
        ## 1. Contexto y metodo

        Trabajaremos sobre los CSV generados por SQL en `data/processed/`.

        Esto es importante porque el notebook no deberia repetir toda la logica de joins. SQL ya dejo listas las tablas con el grano correcto:

        - `fact_orders_delivered.csv`: una fila por orden entregada.
        - `fact_order_items_delivered.csv`: una fila por item vendido en orden entregada.
        - outputs agregados como `monthly_sales.csv`, `category_performance.csv` y `delivery_satisfaction.csv`.

        En este notebook usamos Python para validar, explorar y visualizar.
        """
    ),
    code(
        """
        from pathlib import Path

        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go

        pd.set_option("display.max_columns", 80)
        pd.set_option("display.width", 120)

        PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
        DATA_DIR = PROJECT_ROOT / "data" / "processed"
        """
    ),
    markdown(
        """
        ## 2. Cargar datos procesados

        Cada archivo viene de una consulta SQL previa. Cargarlos desde `data/processed/` permite que el notebook, el dashboard y las validaciones usen las mismas definiciones.
        """
    ),
    code(
        """
        fact_orders = pd.read_csv(DATA_DIR / "fact_orders_delivered.csv", parse_dates=["purchase_date", "purchase_week", "purchase_month"])
        fact_items = pd.read_csv(DATA_DIR / "fact_order_items_delivered.csv", parse_dates=["purchase_date", "purchase_week", "purchase_month"])
        kpi_summary = pd.read_csv(DATA_DIR / "kpi_summary.csv", parse_dates=["first_purchase_date", "last_purchase_date"])
        monthly_sales = pd.read_csv(DATA_DIR / "monthly_sales.csv", parse_dates=["purchase_month"])
        category_performance = pd.read_csv(DATA_DIR / "category_performance.csv")
        customer_frequency = pd.read_csv(DATA_DIR / "customer_frequency_summary.csv")
        customer_lifetime = pd.read_csv(DATA_DIR / "customer_lifetime.csv", parse_dates=["first_purchase_date", "last_purchase_date"])
        delivery_satisfaction = pd.read_csv(DATA_DIR / "delivery_satisfaction.csv")
        customer_state_summary = pd.read_csv(DATA_DIR / "customer_state_summary.csv")
        payment_summary = pd.read_csv(DATA_DIR / "payment_summary.csv")

        loaded_tables = {
            "fact_orders": fact_orders,
            "fact_items": fact_items,
            "kpi_summary": kpi_summary,
            "monthly_sales": monthly_sales,
            "category_performance": category_performance,
            "customer_frequency": customer_frequency,
            "customer_lifetime": customer_lifetime,
            "delivery_satisfaction": delivery_satisfaction,
            "customer_state_summary": customer_state_summary,
            "payment_summary": payment_summary,
        }

        pd.DataFrame(
            [
                {"tabla": name, "filas": len(df), "columnas": len(df.columns)}
                for name, df in loaded_tables.items()
            ]
        )
        """
    ),
    markdown(
        """
        ## 3. Validaciones rapidas

        Antes de interpretar graficos, revisamos que las dos tablas base mantengan el grano esperado:

        - ordenes: una fila por `order_id`;
        - items: una fila por combinacion `order_id + order_item_id`.

        Tambien verificamos que el revenue total sea consistente entre ambas tablas.
        """
    ),
    code(
        """
        validation_summary = {
            "ordenes_filas": len(fact_orders),
            "ordenes_distintas": fact_orders["order_id"].nunique(),
            "items_filas": len(fact_items),
            "items_distintos": fact_items[["order_id", "order_item_id"]].drop_duplicates().shape[0],
            "revenue_ordenes": round(fact_orders["product_revenue"].sum(), 2),
            "revenue_items": round(fact_items["item_revenue"].sum(), 2),
        }

        validation_summary
        """
    ),
    markdown(
        """
        ## 4. KPIs principales

        Esta tabla resume el estado general del negocio considerando solo ordenes entregadas.
        """
    ),
    code(
        """
        kpi_summary.T.rename(columns={0: "valor"})
        """
    ),
    markdown(
        """
        ## 5. Evolucion mensual de ventas

        Este grafico responde si el negocio crece, cae o muestra estacionalidad. Para el dashboard, esta sera una visualizacion central del overview.
        """
    ),
    code(
        """
        fig = px.line(
            monthly_sales,
            x="purchase_month",
            y="product_revenue",
            markers=True,
            title="Revenue mensual de ordenes entregadas",
            labels={"purchase_month": "Mes", "product_revenue": "Product revenue"},
        )
        fig.update_layout(yaxis_tickprefix="R$ ", hovermode="x unified")
        fig.show()
        """
    ),
    markdown(
        """
        ## 6. Ordenes y ticket promedio

        Revenue puede subir por mas ordenes, por mayor ticket promedio, o por ambos. Por eso revisamos volumen y AOV juntos.
        """
    ),
    code(
        """
        fig = go.Figure()
        fig.add_bar(
            x=monthly_sales["purchase_month"],
            y=monthly_sales["delivered_orders"],
            name="Ordenes entregadas",
            yaxis="y",
        )
        fig.add_trace(
            go.Scatter(
                x=monthly_sales["purchase_month"],
                y=monthly_sales["average_order_value"],
                name="AOV",
                mode="lines+markers",
                yaxis="y2",
            )
        )
        fig.update_layout(
            title="Ordenes entregadas y ticket promedio por mes",
            xaxis_title="Mes",
            yaxis={"title": "Ordenes"},
            yaxis2={"title": "AOV", "overlaying": "y", "side": "right", "tickprefix": "R$ "},
            legend={"orientation": "h"},
            hovermode="x unified",
        )
        fig.show()
        """
    ),
    markdown(
        """
        ## 7. Categorias con mayor revenue

        Para priorizar acciones comerciales, no basta con saber el revenue total. Necesitamos entender que categorias lo explican y si el volumen se concentra en pocas de ellas.
        """
    ),
    code(
        """
        top_categories = category_performance.head(12).copy()

        fig = px.bar(
            top_categories.sort_values("product_revenue"),
            x="product_revenue",
            y="category",
            orientation="h",
            title="Top categorias por product revenue",
            labels={"product_revenue": "Product revenue", "category": "Categoria"},
            hover_data=["delivered_orders", "items_sold", "average_review_score"],
        )
        fig.update_layout(xaxis_tickprefix="R$ ")
        fig.show()

        top_categories[["category", "product_revenue", "delivered_orders", "items_sold", "average_item_revenue", "average_review_score"]]
        """
    ),
    markdown(
        """
        ## 8. Concentracion de revenue por categoria

        Un Pareto ayuda a ver si pocas categorias explican gran parte del revenue. Esta lectura es util para decidir foco comercial.
        """
    ),
    code(
        """
        category_pareto = category_performance.sort_values("product_revenue", ascending=False).copy()
        category_pareto["revenue_share"] = category_pareto["product_revenue"] / category_pareto["product_revenue"].sum()
        category_pareto["cumulative_revenue_share"] = category_pareto["revenue_share"].cumsum()

        fig = go.Figure()
        fig.add_bar(
            x=category_pareto["category"].head(20),
            y=category_pareto["product_revenue"].head(20),
            name="Revenue",
        )
        fig.add_trace(
            go.Scatter(
                x=category_pareto["category"].head(20),
                y=category_pareto["cumulative_revenue_share"].head(20),
                name="Revenue acumulado",
                mode="lines+markers",
                yaxis="y2",
            )
        )
        fig.update_layout(
            title="Concentracion de revenue por categoria",
            xaxis_title="Categoria",
            yaxis={"title": "Product revenue", "tickprefix": "R$ "},
            yaxis2={"title": "Share acumulado", "overlaying": "y", "side": "right", "tickformat": ".0%"},
            legend={"orientation": "h"},
        )
        fig.show()
        """
    ),
    markdown(
        """
        ## 9. Recurrencia de clientes

        La recurrencia indica si el negocio depende casi totalmente de nuevos compradores o si logra que una parte relevante vuelva a comprar.
        """
    ),
    code(
        """
        fig = px.bar(
            customer_frequency,
            x="frequency_segment",
            y="customers",
            title="Clientes por frecuencia de compra",
            labels={"frequency_segment": "Frecuencia", "customers": "Clientes"},
            text="customer_share_pct",
            hover_data=["product_revenue", "revenue_share_pct", "average_order_value"],
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.show()

        customer_frequency
        """
    ),
    markdown(
        """
        ## 10. Valor de clientes

        Este corte es exploratorio. Sirve para mirar si existen clientes de alto valor y si vale la pena crear una segmentacion mas fina en la siguiente version.
        """
    ),
    code(
        """
        value_summary = (
            customer_lifetime
            .groupby("value_segment", as_index=False)
            .agg(
                customers=("customer_unique_id", "count"),
                product_revenue=("customer_revenue", "sum"),
                average_customer_revenue=("customer_revenue", "mean"),
                repeat_rate=("is_repeat_customer", "mean"),
            )
        )
        value_summary["product_revenue"] = value_summary["product_revenue"].round(2)
        value_summary["average_customer_revenue"] = value_summary["average_customer_revenue"].round(2)
        value_summary["repeat_rate_pct"] = (100 * value_summary["repeat_rate"]).round(2)
        value_summary.drop(columns=["repeat_rate"])
        """
    ),
    markdown(
        """
        ## 11. Entrega y satisfaccion

        Esta es una de las historias mas fuertes del proyecto: conectar un indicador operacional con una medida de experiencia del cliente.
        """
    ),
    code(
        """
        delivery_order = [
            "7+ days early",
            "1-6 days early",
            "on estimate",
            "1-3 days late",
            "4-7 days late",
            "8+ days late",
        ]

        delivery_satisfaction["delivery_delay_segment"] = pd.Categorical(
            delivery_satisfaction["delivery_delay_segment"],
            categories=delivery_order,
            ordered=True,
        )
        delivery_satisfaction = delivery_satisfaction.sort_values("delivery_delay_segment")

        fig = px.bar(
            delivery_satisfaction,
            x="delivery_delay_segment",
            y="average_review_score",
            title="Review score promedio segun atraso o adelanto de entrega",
            labels={"delivery_delay_segment": "Segmento de entrega", "average_review_score": "Review score promedio"},
            text="average_review_score",
            hover_data=["delivered_orders", "average_delivery_days", "average_delay_days"],
        )
        fig.update_yaxes(range=[0, 5])
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.show()

        delivery_satisfaction
        """
    ),
    markdown(
        """
        ## 12. Estados con mayor revenue y riesgo operacional

        Esta tabla ayuda a priorizar regiones: no solo donde hay mas revenue, sino tambien donde la entrega o satisfaccion puede afectar la experiencia.
        """
    ),
    code(
        """
        customer_state_summary.head(12)[
            [
                "customer_state",
                "product_revenue",
                "delivered_orders",
                "unique_customers",
                "average_order_value",
                "average_review_score",
                "late_delivery_rate_pct",
                "average_delivery_days",
            ]
        ]
        """
    ),
    markdown(
        """
        ## 13. Pagos y ticket promedio

        Este corte no sera necesariamente protagonista del dashboard, pero puede explicar diferencias de ticket y comportamiento de compra.
        """
    ),
    code(
        """
        payment_summary.head(12)
        """
    ),
    markdown(
        """
        ## 14. Takeaways preliminares

        1. El negocio tiene suficiente historia temporal para mostrar tendencia mensual y semanal.
        2. Las categorias top concentran una parte relevante del revenue, por lo que un analisis de mix comercial tiene sentido.
        3. La recurrencia es baja y debe ser una pregunta central del caso.
        4. La entrega tardia se asocia con una caida clara de review score, especialmente desde 4 dias de atraso.
        5. El dashboard deberia priorizar cuatro vistas: overview, categorias, clientes y entrega/satisfaccion.

        Proximo paso: convertir estas exploraciones en un dashboard Streamlit con filtros y graficos interactivos.
        """
    ),
]

NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Notebook creado en {NOTEBOOK_PATH}")
