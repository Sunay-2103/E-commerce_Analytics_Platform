import streamlit as st
import requests
import pandas as pd

# Page config
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

st.title("🛒 E-commerce Analytics Dashboard")

API_URL = "http://127.0.0.1:8000/products"

# Fetch data
try:
    res = requests.get(API_URL)
    data = res.json()
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

df = pd.DataFrame(data)

if df.empty:
    st.warning("No data available. Add products via FastAPI.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

if "price" in df.columns:
    min_price = int(df["price"].min())
    max_price = int(df["price"].max())

    selected_price = st.sidebar.slider(
        "Select Price Range",
        min_price,
        max_price,
        (min_price, max_price)
    )

    df = df[(df["price"] >= selected_price[0]) & (df["price"] <= selected_price[1])]

# --- KPIs ---
col1, col2, col3 = st.columns(3)

col1.metric("📦 Total Products", len(df))
col2.metric("💰 Total Revenue", int(df["price"].sum()))
col3.metric("📊 Avg Price", int(df["price"].mean()))

# --- TABLE ---
st.subheader("📋 Product Data")
st.dataframe(df, use_container_width=True)

# --- CHARTS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Price Distribution")
    st.bar_chart(df["price"])

with col2:
    st.subheader("📊 Top 5 Products")
    if "name" in df.columns:
        top_df = df.sort_values(by="price", ascending=False).head(5)
        st.bar_chart(top_df.set_index("name")["price"])

# --- INSIGHTS ---
st.subheader("📌 Insights")

st.write(f"""
- Highest Price Product: {df.loc[df['price'].idxmax()]['name']}
- Lowest Price Product: {df.loc[df['price'].idxmin()]['name']}
- Revenue Generated: ₹{df['price'].sum()}
""")