"""
API service layer for the Streamlit frontend.
All calls to the FastAPI backend go through here — keeps app.py clean.
"""

import requests
import streamlit as st

BASE_URL = "http://localhost:8000"  # Change to your deployed URL if needed


def _get(path: str, params: dict = None) -> dict | list:
    """Generic GET with error handling."""
    try:
        res = requests.get(f"{BASE_URL}{path}", params=params, timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Make sure FastAPI is running on port 8000.")
        return {}
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e}")
        return {}
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return {}


def get_sales_summary() -> dict:
    return _get("/analytics/sales-summary")

def get_top_products(limit: int = 10) -> list:
    return _get("/analytics/top-products", params={"limit": limit})

def get_order_status_breakdown() -> list:
    return _get("/analytics/order-status")

def get_revenue_by_category() -> list:
    return _get("/analytics/revenue-by-category")

def get_api_metrics() -> dict:
    return _get("/analytics/api-metrics")

def get_recent_orders(limit: int = 50) -> list:
    return _get("/analytics/recent-orders", params={"limit": limit})

def get_payment_method_breakdown() -> list:
    return _get("/analytics/payment-methods")
