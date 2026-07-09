from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Desempeño comercial y experiencia de clientes | Olist",
    page_icon=":bar_chart:",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

COLORS = {
    "green": "#214D27",
    "green_light": "#9DB79A",
    "cream": "#FAF7EF",
    "cream_dark": "#EEE6D5",
    "orange": "#D97706",
    "navy": "#16324F",
    "ink": "#1F2933",
    "muted": "#667085",
    "grid": "#DED8CC",
    "white": "#FFFFFF",
}

CATEGORY_LABELS = {
    "health_beauty": "Belleza y cuidado personal",
    "watches_gifts": "Relojes y regalos",
    "bed_bath_table": "Dormitorio, baño y mesa",
    "sports_leisure": "Deportes y ocio",
    "computers_accessories": "Computación y accesorios",
    "furniture_decor": "Muebles y decoración",
    "housewares": "Artículos para el hogar",
    "cool_stuff": "Productos novedosos",
    "auto": "Automóvil",
    "toys": "Juguetes",
    "garden_tools": "Jardín y herramientas",
    "baby": "Bebés",
    "perfumery": "Perfumería",
    "telephony": "Telefonía",
    "office_furniture": "Muebles de oficina",
    "stationery": "Papelería",
    "computers": "Computación",
    "pet_shop": "Mascotas",
    "musical_instruments": "Instrumentos musicales",
    "small_appliances": "Electrodomésticos pequeños",
    "unknown": "Sin categoría",
    "electronics": "Electrónica",
    "fashion_bags_accessories": "Moda, bolsos y accesorios",
    "consoles_games": "Consolas y videojuegos",
    "construction_tools_construction": "Herramientas de construcción",
    "luggage_accessories": "Equipaje y accesorios",
    "home_appliances_2": "Electrodomésticos",
    "home_construction": "Construcción y hogar",
    "home_appliances": "Electrodomésticos",
    "agro_industry_and_commerce": "Agroindustria y comercio",
    "furniture_living_room": "Muebles de sala",
    "home_confort": "Confort para el hogar",
    "fixed_telephony": "Telefonía fija",
    "air_conditioning": "Climatización",
    "audio": "Audio",
    "small_appliances_home_oven_and_coffee": "Cocina y cafeteras",
    "kitchen_dining_laundry_garden_furniture": "Muebles de cocina y jardín",
    "books_general_interest": "Libros de interés general",
    "construction_tools_lights": "Iluminación",
    "construction_tools_safety": "Seguridad y construcción",
    "industry_commerce_and_business": "Industria y negocios",
    "food": "Alimentos",
    "market_place": "Marketplace",
    "costruction_tools_garden": "Herramientas de jardín",
    "art": "Arte",
    "fashion_shoes": "Calzado",
    "drinks": "Bebidas",
    "signaling_and_security": "Señalización y seguridad",
    "furniture_bedroom": "Muebles de dormitorio",
    "books_technical": "Libros técnicos",
    "costruction_tools_tools": "Herramientas",
    "food_drink": "Alimentos y bebidas",
    "fashion_male_clothing": "Ropa masculina",
    "fashion_underwear_beach": "Ropa interior y playa",
    "christmas_supplies": "Artículos navideños",
    "tablets_printing_image": "Tablets e impresión",
    "cine_photo": "Cine y fotografía",
    "music": "Música",
    "dvds_blu_ray": "DVD y Blu-ray",
    "party_supplies": "Artículos para fiestas",
    "books_imported": "Libros importados",
    "furniture_mattress_and_upholstery": "Colchones y tapicería",
    "portateis_cozinha_e_preparadores_de_alimentos": "Preparación de alimentos",
    "fashio_female_clothing": "Ropa femenina",
    "fashion_sport": "Moda deportiva",
    "la_cuisine": "Cocina gourmet",
    "arts_and_craftmanship": "Artesanía",
    "diapers_and_hygiene": "Pañales e higiene",
    "pc_gamer": "PC gamer",
    "flowers": "Flores",
    "home_comfort_2": "Confort para el hogar",
    "cds_dvds_musicals": "CD, DVD y musicales",
    "fashion_childrens_clothes": "Ropa infantil",
    "security_and_services": "Seguridad y servicios",
}

DELIVERY_SEGMENT_LABELS = {
    "7+ days early": "7+ días antes",
    "1-6 days early": "1 a 6 días antes",
    "on estimate": "En la fecha estimada",
    "1-3 days late": "1 a 3 días tarde",
    "4-7 days late": "4 a 7 días tarde",
    "8+ days late": "8+ días tarde",
}


@st.cache_data(show_spinner=False)
def load_dashboard_data() -> dict[str, pd.DataFrame]:
    """Carga los resultados agregados y validados previamente en SQL."""

    return {
        "kpi": pd.read_csv(DATA_DIR / "kpi_summary.csv", parse_dates=["first_purchase_date", "last_purchase_date"]),
        "monthly": pd.read_csv(DATA_DIR / "monthly_sales.csv", parse_dates=["purchase_month"]),
        "category": pd.read_csv(DATA_DIR / "category_performance.csv"),
        "customer_frequency": pd.read_csv(DATA_DIR / "customer_frequency_summary.csv"),
        "customer_repeat_timing": pd.read_csv(DATA_DIR / "customer_repeat_timing.csv"),
        "customer_repeat_rate_by_state": pd.read_csv(DATA_DIR / "customer_repeat_rate_by_state.csv"),
        "customer_state": pd.read_csv(DATA_DIR / "customer_state_summary.csv"),
        "delivery": pd.read_csv(DATA_DIR / "delivery_satisfaction.csv"),
    }


def format_currency(value: float) -> str:
    return f"R$ {value:,.0f}"


def format_compact_currency(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.1f}K"
    return format_currency(value)


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def apply_chart_style(fig: go.Figure, *, height: int = 420) -> go.Figure:
    """Da a los gráficos una jerarquía visual consistente con el dashboard."""

    fig.update_layout(
        height=height,
        paper_bgcolor=COLORS["cream"],
        plot_bgcolor=COLORS["cream"],
        font={"family": "Arial, sans-serif", "color": COLORS["ink"]},
        title={"x": 0, "xanchor": "left", "font": {"size": 18, "color": COLORS["navy"]}},
        margin={"l": 12, "r": 12, "t": 58, "b": 12},
        legend={"orientation": "h", "y": 1.12, "x": 0, "bgcolor": "rgba(0,0,0,0)"},
        hoverlabel={"bgcolor": COLORS["white"], "font_color": COLORS["ink"]},
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=COLORS["grid"], tickfont={"color": COLORS["muted"]})
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"], tickfont={"color": COLORS["muted"]})
    return fig


def calculate_repeat_rate(customer_frequency: pd.DataFrame) -> float:
    total_customers = customer_frequency["customers"].sum()
    repeat_customers = customer_frequency.loc[
        customer_frequency["frequency_segment"] != "1 order", "customers"
    ].sum()
    return repeat_customers / total_customers * 100


def apply_month_filter(monthly: pd.DataFrame, selected_months: tuple[pd.Timestamp, pd.Timestamp]) -> pd.DataFrame:
    start_month, end_month = selected_months
    return monthly.loc[
        (monthly["purchase_month"] >= start_month) & (monthly["purchase_month"] <= end_month)
    ].copy()


def prepare_category_data(category: pd.DataFrame) -> pd.DataFrame:
    prepared = category.copy()
    prepared["category_label"] = prepared["category"].map(CATEGORY_LABELS).fillna(prepared["category"])
    return prepared


def revenue_trend_chart(monthly: pd.DataFrame) -> go.Figure:
    fig = px.area(
        monthly,
        x="purchase_month",
        y="product_revenue",
        title="Evolución mensual del revenue",
        labels={"purchase_month": "Mes de compra", "product_revenue": "Revenue de productos"},
    )
    fig.update_traces(
        line={"color": COLORS["green"], "width": 3},
        fillcolor="rgba(33, 77, 39, 0.18)",
        hovertemplate="%{x|%b %Y}<br>Revenue: R$ %{y:,.0f}<extra></extra>",
    )
    fig.update_layout(yaxis_tickprefix="R$ ", hovermode="x unified")
    return apply_chart_style(fig)


def orders_aov_chart(monthly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=monthly["purchase_month"],
        y=monthly["delivered_orders"],
        name="Órdenes entregadas",
        marker_color=COLORS["green_light"],
        hovertemplate="%{x|%b %Y}<br>Órdenes entregadas: %{y:,.0f}<extra></extra>",
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["purchase_month"],
            y=monthly["average_order_value"],
            name="Ticket promedio",
            mode="lines+markers",
            marker={"color": COLORS["orange"], "size": 7},
            line={"color": COLORS["orange"], "width": 3},
            yaxis="y2",
            hovertemplate="%{x|%b %Y}<br>Ticket promedio: R$ %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Volumen de órdenes y ticket promedio",
        xaxis_title="Mes de compra",
        yaxis={"title": "Órdenes entregadas"},
        yaxis2={"title": "Ticket promedio", "overlaying": "y", "side": "right", "tickprefix": "R$ "},
        hovermode="x unified",
    )
    return apply_chart_style(fig)


def top_categories_chart(category: pd.DataFrame, top_n: int) -> go.Figure:
    chart_data = category.nlargest(top_n, "product_revenue").sort_values("product_revenue")
    fig = px.bar(
        chart_data,
        x="product_revenue",
        y="category_label",
        orientation="h",
        title=f"Categorías con mayor revenue (top {top_n})",
        labels={"product_revenue": "Revenue de productos", "category_label": "Categoría"},
        hover_data={
            "delivered_orders": ":,",
            "items_sold": ":,",
            "average_review_score": ".2f",
            "late_delivery_rate_pct": ".1f",
            "product_revenue": ":,.0f",
        },
    )
    fig.update_traces(
        marker_color=COLORS["green"],
        customdata=chart_data[["delivered_orders", "items_sold", "average_review_score", "late_delivery_rate_pct"]].to_numpy(),
        hovertemplate=(
            "<b>%{y}</b><br>Revenue: R$ %{x:,.0f}<br>Órdenes: %{customdata[0]:,.0f}"
            "<br>Ítems: %{customdata[1]:,.0f}<br>Calificación: %{customdata[2]:.2f} / 5"
            "<br>Entrega tardía: %{customdata[3]:.1f}%<extra></extra>"
        ),
    )
    fig.update_layout(xaxis_tickprefix="R$ ")
    return apply_chart_style(fig)


def category_opportunity_chart(category: pd.DataFrame, top_n: int) -> go.Figure:
    chart_data = category.nlargest(top_n, "product_revenue").copy()
    fig = px.scatter(
        chart_data,
        x="average_review_score",
        y="product_revenue",
        size="delivered_orders",
        color="late_delivery_rate_pct",
        hover_name="category_label",
        size_max=48,
        color_continuous_scale=[COLORS["green"], COLORS["orange"]],
        title="Ingresos, satisfacción y atraso por categoría",
        labels={
            "average_review_score": "Calificación promedio (1 a 5)",
            "product_revenue": "Revenue de productos",
            "late_delivery_rate_pct": "Entrega tardía (%)",
        },
        hover_data={
            "category_label": False,
            "delivered_orders": ":,",
            "items_sold": ":,",
            "average_review_score": ".2f",
            "late_delivery_rate_pct": ".1f",
            "product_revenue": ":,.0f",
        },
    )
    fig.update_traces(
        marker={"line": {"color": COLORS["white"], "width": 1.5}, "opacity": 0.85},
        customdata=chart_data[["delivered_orders", "items_sold"]].to_numpy(),
        hovertemplate=(
            "<b>%{hovertext}</b><br>Revenue: R$ %{y:,.0f}<br>Calificación: %{x:.2f} / 5"
            "<br>Órdenes: %{customdata[0]:,.0f}<br>Ítems: %{customdata[1]:,.0f}"
            "<br>Entrega tardía: %{marker.color:.1f}%<extra></extra>"
        ),
    )
    fig.update_layout(yaxis_tickprefix="R$ ", coloraxis_colorbar={"title": "Entrega<br>tardía"})
    fig.update_xaxes(range=[3.6, 4.35])
    return apply_chart_style(fig, height=500)


def customer_repeat_timing_chart(repeat_timing: pd.DataFrame) -> go.Figure:
    """Muestra el intervalo entre primera y última compra de quienes sí repitieron."""

    fig = px.histogram(
        repeat_timing,
        x="customer_lifespan_days",
        nbins=24,
        title="Recompra: días entre compras",
        labels={"customer_lifespan_days": "Días transcurridos", "count": "Clientes recurrentes"},
    )
    fig.update_traces(
        marker_color=COLORS["green"],
        hovertemplate="Días transcurridos: %{x}<br>Clientes recurrentes: %{y:,.0f}<extra></extra>",
    )
    return apply_chart_style(fig)


def state_repeat_rate_chart(repeat_rate_by_state: pd.DataFrame, top_n: int) -> go.Figure:
    """Compara la recompra entre los estados con una base de clientes material."""

    chart_data = (
        repeat_rate_by_state.nlargest(top_n, "unique_customers")
        .sort_values("repeat_customer_rate_pct")
        .copy()
    )

    fig = px.bar(
        chart_data,
        x="repeat_customer_rate_pct",
        y="customer_state",
        orientation="h",
        title="Tasa de recompra por estado",
        labels={"repeat_customer_rate_pct": "Clientes que vuelven a comprar", "customer_state": "Estado"},
        hover_data={"unique_customers": ":,", "repeat_customers": ":,", "repeat_customer_rate_pct": ".2f"},
    )
    fig.update_traces(
        marker_color=COLORS["navy"],
        customdata=chart_data[["unique_customers", "repeat_customers"]].to_numpy(),
        hovertemplate=(
            "<b>%{y}</b><br>Tasa de recompra: %{x:.2f}%<br>Clientes: %{customdata[0]:,.0f}"
            "<br>Clientes recurrentes: %{customdata[1]:,.0f}<extra></extra>"
        ),
    )
    fig.update_layout(xaxis_ticksuffix="%")
    return apply_chart_style(fig)


def delivery_satisfaction_chart(delivery: pd.DataFrame) -> go.Figure:
    order = ["7+ days early", "1-6 days early", "on estimate", "1-3 days late", "4-7 days late", "8+ days late"]
    chart_data = delivery.copy()
    chart_data["delivery_delay_segment"] = pd.Categorical(
        chart_data["delivery_delay_segment"], categories=order, ordered=True
    )
    chart_data = chart_data.sort_values("delivery_delay_segment")
    chart_data["segmento"] = chart_data["delivery_delay_segment"].astype(str).map(DELIVERY_SEGMENT_LABELS)

    fig = px.line(
        chart_data,
        x="segmento",
        y="average_review_score",
        markers=True,
        title="A mayor atraso, menor satisfacción",
        labels={"segmento": "Cumplimiento de la entrega", "average_review_score": "Calificación promedio"},
        hover_data={"delivered_orders": ":,", "average_delivery_days": ".1f", "average_delay_days": ".1f"},
    )
    fig.update_traces(
        line={"color": COLORS["navy"], "width": 3},
        marker={"color": COLORS["orange"], "size": 10},
        hovertemplate=(
            "<b>%{x}</b><br>Calificación promedio: %{y:.2f} / 5<br>Órdenes: %{customdata[0]:,.0f}"
            "<br>Días de entrega: %{customdata[1]:.1f}<br>Desviación: %{customdata[2]:.1f} días<extra></extra>"
        ),
    )
    fig.update_layout(yaxis_range=[1, 5])
    return apply_chart_style(fig)


def state_delivery_chart(customer_state: pd.DataFrame, top_n: int) -> go.Figure:
    chart_data = customer_state.nlargest(top_n, "product_revenue").copy()
    fig = px.scatter(
        chart_data,
        x="average_delivery_days",
        y="average_review_score",
        size="product_revenue",
        color="late_delivery_rate_pct",
        hover_name="customer_state",
        size_max=55,
        color_continuous_scale=[COLORS["green"], COLORS["orange"]],
        title="Experiencia logística por estado",
        labels={
            "average_delivery_days": "Días promedio de entrega",
            "average_review_score": "Calificación promedio",
            "late_delivery_rate_pct": "Entrega tardía (%)",
        },
        hover_data={
            "customer_state": False,
            "product_revenue": ":,.0f",
            "delivered_orders": ":,",
            "late_delivery_rate_pct": ".1f",
        },
    )
    fig.update_traces(
        marker={"line": {"color": COLORS["white"], "width": 1.5}, "opacity": 0.85},
        customdata=chart_data[["product_revenue", "delivered_orders", "late_delivery_rate_pct"]].to_numpy(),
        hovertemplate=(
            "<b>%{hovertext}</b><br>Días de entrega: %{x:.1f}<br>Calificación: %{y:.2f} / 5"
            "<br>Revenue: R$ %{customdata[0]:,.0f}<br>Órdenes: %{customdata[1]:,.0f}"
            "<br>Entrega tardía: %{customdata[2]:.1f}%<extra></extra>"
        ),
    )
    fig.update_layout(coloraxis_colorbar={"title": "Entrega<br>tardía"})
    fig.update_yaxes(range=[3.6, 4.35])
    return apply_chart_style(fig)


def render_takeaways(items: list[tuple[str, str]]) -> None:
    """Muestra hallazgos breves para acompañar, sin reemplazar, la evidencia visual."""

    st.markdown("<div class='takeaway-title'>Principales hallazgos</div>", unsafe_allow_html=True)
    columns = st.columns(len(items))
    for column, (title, text) in zip(columns, items, strict=True):
        with column:
            st.markdown(
                f"<div class='takeaway'><strong>{title}</strong><br><span>{text}</span></div>",
                unsafe_allow_html=True,
            )


st.markdown(
    """
    <style>
        .stApp { background: #FAF7EF; }
        [data-testid="stSidebar"] { background: #F1EBDD; }
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E4DDCE;
            border-radius: 6px;
            padding: 14px 16px;
        }
        [data-testid="stMetricLabel"] { color: #667085; }
        [data-testid="stMetricValue"] { color: #16324F; }
        .takeaway-title { color: #16324F; font-size: 1.05rem; font-weight: 600; margin: 16px 0 4px; }
        .takeaway {
            background: #FFFFFF;
            border-left: 4px solid #D97706;
            border-radius: 4px;
            color: #1F2933;
            line-height: 1.45;
            min-height: 104px;
            padding: 14px 16px;
        }
        .takeaway strong { color: #214D27; }
        .takeaway span { color: #667085; font-size: 0.92rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] { color: #44505C; font-weight: 600; }
        .stTabs [aria-selected="true"] { color: #214D27; }
    </style>
    """,
    unsafe_allow_html=True,
)

data = load_dashboard_data()
kpi = data["kpi"].iloc[0]
monthly = data["monthly"]
category = prepare_category_data(data["category"])
customer_frequency = data["customer_frequency"]
customer_repeat_timing = data["customer_repeat_timing"]
customer_repeat_rate_by_state = data["customer_repeat_rate_by_state"]
customer_state = data["customer_state"]
delivery = data["delivery"]

repeat_rate = calculate_repeat_rate(customer_frequency)
repeat_customers = customer_frequency.loc[customer_frequency["frequency_segment"] != "1 order", "customers"].sum()
top_five_share = category.nlargest(5, "product_revenue")["product_revenue"].sum() / category["product_revenue"].sum() * 100
late_reviews = delivery.loc[delivery["delivery_delay_segment"] == "8+ days late", "average_review_score"].iloc[0]
early_order_share = (
    delivery.loc[delivery["delivery_delay_segment"] == "7+ days early", "delivered_orders"].iloc[0]
    / kpi["delivered_orders"]
    * 100
)

st.title("Desempeño comercial y experiencia de clientes en Olist")
st.caption(
    "Dashboard de portafolio de análisis de datos construido con SQL, Python, Streamlit y Plotly. "
    "Los KPIs principales usan los datos de órdenes entregadas y revenue de productos del dataset público Olist."
)

with st.sidebar:
    st.header("Explorar el dashboard")
    top_n_categories = st.slider("Categorías a mostrar", min_value=5, max_value=15, value=10, step=1)
    top_n_states = st.slider("Estados a mostrar", min_value=8, max_value=20, value=15, step=1)

    min_month = monthly["purchase_month"].min().to_pydatetime()
    max_month = monthly["purchase_month"].max().to_pydatetime()
    selected_months = st.slider(
        "Período de las tendencias",
        min_value=min_month,
        max_value=max_month,
        value=(min_month, max_month),
        format="MMM YYYY",
    )

    st.divider()
    st.caption("Fuente: Olist Brazilian E-commerce Public Dataset. Período: septiembre de 2016 a agosto de 2018.")
    st.caption("Revenue = suma del precio de los productos; no incluye el costo de envío.")

filtered_monthly = apply_month_filter(monthly, tuple(pd.to_datetime(selected_months)))

overview_tab, sales_tab, customers_tab, delivery_tab = st.tabs(
    ["Resumen ejecutivo", "Ventas y categorías", "Clientes", "Entrega y satisfacción"]
)

with overview_tab:
    metric_columns = st.columns(3)
    metric_columns[0].metric("Revenue de productos", format_compact_currency(kpi["product_revenue"]))
    metric_columns[1].metric("Órdenes entregadas", format_number(kpi["delivered_orders"]))
    metric_columns[2].metric("Ticket promedio", format_currency(kpi["average_order_value"]))

    metric_columns = st.columns(3)
    metric_columns[0].metric("Clientes únicos", format_number(kpi["unique_customers"]))
    metric_columns[1].metric("Clientes recurrentes", format_percent(repeat_rate))
    metric_columns[2].metric("Satisfacción promedio", f"{kpi['average_review_score']:.2f} / 5")

    st.caption(
        "Los KPIs representan todo el período validado. El filtro de fechas solo modifica las tendencias mensuales, "
        "para no duplicar clientes únicos al sumar meses."
    )

    left_col, right_col = st.columns((1.15, 1))
    with left_col:
        st.plotly_chart(revenue_trend_chart(filtered_monthly), use_container_width=True, config={"displaylogo": False})
    with right_col:
        st.plotly_chart(orders_aov_chart(filtered_monthly), use_container_width=True, config={"displaylogo": False})

    render_takeaways(
        [
            (
                "La recompra es la principal oportunidad",
                f"Solo {format_percent(repeat_rate)} de los clientes vuelve a comprar ({format_number(repeat_customers)} personas).",
            ),
            (
                "El negocio tiene categorías motoras",
                f"Las cinco categorías líderes concentran {format_percent(top_five_share)} del revenue de productos.",
            ),
            (
                "La promesa de entrega protege la satisfacción",
                f"Cuando el atraso supera 8 días, la calificación promedio cae a {late_reviews:.2f} de 5.",
            ),
        ]
    )

with sales_tab:
    st.subheader("Categorías que sostienen el crecimiento")
    st.caption(
        "En la gráfica de dispersión, cada punto es una categoría: arriba significa mayor revenue, "
        "a la derecha mejor calificación, el tamaño representa órdenes entregadas y el color indica la tasa de entregas tardías."
    )

    left_col, right_col = st.columns((0.95, 1.25))
    with left_col:
        st.plotly_chart(top_categories_chart(category, top_n_categories), use_container_width=True, config={"displaylogo": False})
    with right_col:
        st.plotly_chart(category_opportunity_chart(category, top_n_categories), use_container_width=True, config={"displaylogo": False})

    render_takeaways(
        [
            (
                "Priorizar las categorías de alto volumen",
                "Son las que combinan una mayor contribución al revenue con suficiente base de órdenes para generar impacto.",
            ),
            (
                "No mirar el revenue aislado",
                "Una categoría relevante con reviews más bajos o atrasos elevados merece una revisión operativa antes de escalarla.",
            ),
            (
                "Usar la matriz como filtro de inversión",
                "Las categorías altas y a la derecha combinan revenue relevante con mejor experiencia de cliente.",
            ),
        ]
    )

with customers_tab:
    st.subheader("La recompra es limitada y ayuda a definir dónde actuar")
    st.caption(
        "El histograma muestra los días entre la primera y última compra de quienes sí repitieron. "
        "El gráfico de estados compara porcentajes de recompra; no usa tamaño ni color como variables adicionales."
    )

    metric_columns = st.columns(3)
    metric_columns[0].metric("Clientes únicos", format_number(kpi["unique_customers"]))
    metric_columns[1].metric("Compra única", "97%")
    metric_columns[2].metric("Recompra", "3%")

    left_col, right_col = st.columns((1, 1.2))
    with left_col:
        st.plotly_chart(customer_repeat_timing_chart(customer_repeat_timing), use_container_width=True, config={"displaylogo": False})
    with right_col:
        st.plotly_chart(state_repeat_rate_chart(customer_repeat_rate_by_state, top_n_states), use_container_width=True, config={"displaylogo": False})

    render_takeaways(
        [
            (
                "Retener vale más que solo adquirir",
                f"La segunda compra aparece en solo {format_percent(repeat_rate)} de la base, por lo que existe espacio para activar recompra post-entrega.",
            ),
            (
                "La ventana de reactivación importa",
                "El tiempo entre compras de quienes vuelven permite plantear campañas de seguimiento con un momento definido.",
            ),
            (
                "La recompra no es igual en todos los estados",
                "La comparación se limita a los estados con más clientes para evitar interpretar tasas altas sobre bases muy pequeñas.",
            ),
        ]
    )

with delivery_tab:
    st.subheader("La logística condiciona la experiencia")
    st.caption(
        "En la gráfica por estado, cada punto representa un estado: a la derecha hay más días de entrega, "
        "arriba una mejor calificación, el tamaño representa revenue y el color la tasa de entregas tardías."
    )

    metric_columns = st.columns(3)
    metric_columns[0].metric("Entregas tardías", format_percent(kpi["late_delivery_rate_pct"]))
    metric_columns[1].metric("Días promedio de entrega", f"{kpi['average_delivery_days']:.1f}")
    metric_columns[2].metric("Entregas 7+ días antes", format_percent(early_order_share))

    left_col, right_col = st.columns((1, 1.2))
    with left_col:
        st.plotly_chart(delivery_satisfaction_chart(delivery), use_container_width=True, config={"displaylogo": False})
    with right_col:
        st.plotly_chart(state_delivery_chart(customer_state, top_n_states), use_container_width=True, config={"displaylogo": False})

    render_takeaways(
        [
            (
                "El atraso tiene un costo claro",
                f"Las órdenes 8+ días tarde reciben {late_reviews:.2f} estrellas en promedio, muy por debajo del total ({kpi['average_review_score']:.2f}).",
            ),
            (
                "La anticipación es una fortaleza",
                f"{format_percent(early_order_share)} de las órdenes se entrega al menos siete días antes de la fecha estimada.",
            ),
            (
                "La mejora debe ser focalizada",
                "Los estados más lentos o con mayor tasa de atraso son una oportunidad para revisar cobertura, promesa y desempeño logístico.",
            ),
        ]
    )
