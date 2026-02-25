"""
Streamlit Dashboard — E-commerce DevOps Analytics Platform
Run with: streamlit run frontend/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.api import (
    get_sales_summary,
    get_top_products,
    get_order_status_breakdown,
    get_revenue_by_category,
    get_api_metrics,
    get_recent_orders,
    get_payment_method_breakdown,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("📊 Analytics Platform")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "📦 Products", "👥 Users & Orders", "⚙️ DevOps Metrics"],
)
st.sidebar.markdown("---")
st.sidebar.caption("E-commerce DevOps Analytics Platform v1.0")

# ── Helper ────────────────────────────────────────────────────────────────────
def metric_card(label, value, delta=None):
    if delta:
        st.metric(label=label, value=value, delta=delta)
    else:
        st.metric(label=label, value=value)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Overview
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🏠 Business Overview")
    st.caption("High-level KPIs and revenue trends")
    st.markdown("---")

    # KPI Row
    summary = get_sales_summary()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Revenue", f"₹{summary.get('total_revenue', 0):,.0f}")
    with col2:
        metric_card("Total Orders", f"{summary.get('total_orders', 0):,}")
    with col3:
        metric_card("Avg Order Value", f"₹{summary.get('avg_order_value', 0):,.0f}")
    with col4:
        metric_card("Total Users", f"{summary.get('total_users', 0):,}")

    st.markdown("---")

    # Revenue over time
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Revenue Over Time (Daily)")
        daily = summary.get("daily_revenue", [])
        if daily:
            df_daily = pd.DataFrame(daily)
            df_daily["date"] = pd.to_datetime(df_daily["date"])
            fig = px.area(
                df_daily, x="date", y="revenue",
                color_discrete_sequence=["#4F8BF9"],
                labels={"revenue": "Revenue (₹)", "date": "Date"},
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No daily revenue data yet.")

    with col_b:
        st.subheader("Order Status")
        status_data = get_order_status_breakdown()
        if status_data:
            df_status = pd.DataFrame(status_data)
            fig = px.pie(
                df_status, names="status", values="count",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4,
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No order data yet.")

    # Revenue by category
    st.subheader("Revenue by Category")
    cat_data = get_revenue_by_category()
    if cat_data:
        df_cat = pd.DataFrame(cat_data).sort_values("revenue", ascending=True)
        fig = px.bar(
            df_cat, x="revenue", y="category", orientation="h",
            color="revenue", color_continuous_scale="Blues",
            labels={"revenue": "Revenue (₹)", "category": "Category"},
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Products
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Products":
    st.title("📦 Product Performance")
    st.caption("Top selling products and category breakdown")
    st.markdown("---")

    top_n = st.slider("Show top N products", min_value=5, max_value=20, value=10)
    products = get_top_products(limit=top_n)

    if products:
        df_prod = pd.DataFrame(products)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Top {top_n} Products by Revenue")
            fig = px.bar(
                df_prod.sort_values("total_revenue", ascending=True),
                x="total_revenue", y="product_name", orientation="h",
                color="category",
                labels={"total_revenue": "Revenue (₹)", "product_name": "Product"},
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=420)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader(f"Top {top_n} Products by Units Sold")
            fig = px.bar(
                df_prod.sort_values("total_units", ascending=True),
                x="total_units", y="product_name", orientation="h",
                color="category",
                labels={"total_units": "Units Sold", "product_name": "Product"},
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=420)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Product Data Table")
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("No product data available.")

    # Payment method breakdown
    st.markdown("---")
    st.subheader("Payment Method Distribution")
    pay_data = get_payment_method_breakdown()
    if pay_data:
        df_pay = pd.DataFrame(pay_data)
        fig = px.pie(
            df_pay, names="payment_method", values="count",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.35,
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Users & Orders
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Users & Orders":
    st.title("👥 Users & Orders")
    st.caption("Order activity and recent transactions")
    st.markdown("---")

    recent = get_recent_orders(limit=50)
    if recent:
        df_orders = pd.DataFrame(recent)
        df_orders["created_at"] = pd.to_datetime(df_orders["created_at"])

        st.subheader("Recent 50 Orders")
        st.dataframe(df_orders, use_container_width=True)

        st.subheader("Orders by Status Over Time")
        df_grouped = (
            df_orders
            .groupby([df_orders["created_at"].dt.date, "status"])
            .size()
            .reset_index(name="count")
        )
        fig = px.bar(
            df_grouped, x="created_at", y="count", color="status",
            barmode="stack",
            labels={"created_at": "Date", "count": "Orders"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No order data available.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DevOps Metrics
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ DevOps Metrics":
    st.title("⚙️ DevOps & API Health")
    st.caption("Request latency, error rates, and endpoint usage")
    st.markdown("---")

    metrics = get_api_metrics()

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total API Calls", f"{metrics.get('total_requests', 0):,}")
    with col2:
        metric_card("Avg Latency", f"{metrics.get('avg_response_time_ms', 0):.1f} ms")
    with col3:
        error_rate = metrics.get("error_rate_pct", 0)
        metric_card("Error Rate", f"{error_rate:.1f}%")
    with col4:
        metric_card("Endpoints Tracked", f"{metrics.get('unique_paths', 0)}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Avg Response Time by Endpoint")
        endpoint_data = metrics.get("by_endpoint", [])
        if endpoint_data:
            df_ep = pd.DataFrame(endpoint_data).sort_values("avg_ms", ascending=True)
            fig = px.bar(
                df_ep, x="avg_ms", y="path", orientation="h",
                color="avg_ms", color_continuous_scale="RdYlGn_r",
                labels={"avg_ms": "Avg Response Time (ms)", "path": "Endpoint"},
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No API log data yet — make some requests first.")

    with col_b:
        st.subheader("HTTP Status Code Distribution")
        status_data = metrics.get("by_status_code", [])
        if status_data:
            df_sc = pd.DataFrame(status_data)
            df_sc["status_code"] = df_sc["status_code"].astype(str)
            fig = px.pie(
                df_sc, names="status_code", values="count",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4,
            )
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Request Volume Over Time (Hourly)")
    hourly = metrics.get("hourly_requests", [])
    if hourly:
        df_hourly = pd.DataFrame(hourly)
        df_hourly["hour"] = pd.to_datetime(df_hourly["hour"])
        fig = px.line(
            df_hourly, x="hour", y="count",
            color_discrete_sequence=["#4F8BF9"],
            labels={"hour": "Hour", "count": "Requests"},
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hourly data yet.")
