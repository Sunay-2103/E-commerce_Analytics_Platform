"""
app/routes/analytics.py
Analytics endpoints that power the Streamlit dashboard.
Add to main.py: from app.routes import analytics
               app.include_router(analytics.router)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import get_db
from app.models.models import Order, OrderItem, Product, Payment, RequestLog, User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/sales-summary")
def sales_summary(db: Session = Depends(get_db)):
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status != "cancelled"
    ).scalar() or 0

    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    avg_order_value = float(total_revenue) / total_orders if total_orders else 0

    daily_revenue = db.execute(text("""
        SELECT DATE(created_at) as date, SUM(total_amount) as revenue
        FROM orders
        WHERE status != 'cancelled'
        GROUP BY DATE(created_at)
        ORDER BY date
    """)).fetchall()

    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": total_orders,
        "total_users": total_users,
        "avg_order_value": round(avg_order_value, 2),
        "daily_revenue": [{"date": str(r.date), "revenue": float(r.revenue)} for r in daily_revenue],
    }


@router.get("/top-products")
def top_products(limit: int = 10, db: Session = Depends(get_db)):
    results = db.execute(text("""
        SELECT
            p.name AS product_name,
            p.category,
            SUM(oi.quantity * oi.price) AS total_revenue,
            SUM(oi.quantity) AS total_units
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY p.id, p.name, p.category
        ORDER BY total_revenue DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    return [
        {
            "product_name": r.product_name,
            "category": r.category,
            "total_revenue": round(float(r.total_revenue), 2),
            "total_units": int(r.total_units),
        }
        for r in results
    ]


@router.get("/order-status")
def order_status_breakdown(db: Session = Depends(get_db)):
    results = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    return [{"status": r[0], "count": r[1]} for r in results]


@router.get("/revenue-by-category")
def revenue_by_category(db: Session = Depends(get_db)):
    results = db.execute(text("""
        SELECT p.category, SUM(oi.quantity * oi.price) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status != 'cancelled'
        GROUP BY p.category
        ORDER BY revenue DESC
    """)).fetchall()
    return [{"category": r.category, "revenue": round(float(r.revenue), 2)} for r in results]


@router.get("/payment-methods")
def payment_methods(db: Session = Depends(get_db)):
    results = db.query(Payment.payment_method, func.count(Payment.id)).group_by(
        Payment.payment_method
    ).all()
    return [{"payment_method": r[0], "count": r[1]} for r in results]


@router.get("/recent-orders")
def recent_orders(limit: int = 50, db: Session = Depends(get_db)):
    results = db.execute(text("""
        SELECT o.id, u.name AS user_name, o.total_amount, o.status, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    return [
        {
            "id": r.id,
            "user_name": r.user_name,
            "total_amount": float(r.total_amount),
            "status": r.status,
            "created_at": str(r.created_at),
        }
        for r in results
    ]


@router.get("/api-metrics")
def api_metrics(db: Session = Depends(get_db)):
    total = db.query(func.count(RequestLog.id)).scalar() or 0
    avg_ms = db.query(func.avg(RequestLog.response_time_ms)).scalar() or 0
    errors = db.query(func.count(RequestLog.id)).filter(RequestLog.status_code >= 400).scalar() or 0
    unique_paths = db.query(func.count(func.distinct(RequestLog.path))).scalar() or 0
    error_rate = (errors / total * 100) if total else 0

    by_endpoint = db.execute(text("""
        SELECT path, AVG(response_time_ms) AS avg_ms, COUNT(*) AS total
        FROM request_logs
        GROUP BY path
        ORDER BY avg_ms DESC
        LIMIT 15
    """)).fetchall()

    by_status = db.execute(text("""
        SELECT status_code, COUNT(*) AS count
        FROM request_logs
        GROUP BY status_code
        ORDER BY count DESC
    """)).fetchall()

    hourly = db.execute(text("""
        SELECT DATE_TRUNC('hour', created_at) AS hour, COUNT(*) AS count
        FROM request_logs
        GROUP BY 1
        ORDER BY 1
    """)).fetchall()

    return {
        "total_requests": total,
        "avg_response_time_ms": round(float(avg_ms), 2),
        "error_rate_pct": round(error_rate, 2),
        "unique_paths": unique_paths,
        "by_endpoint": [{"path": r.path, "avg_ms": round(float(r.avg_ms), 2)} for r in by_endpoint],
        "by_status_code": [{"status_code": r.status_code, "count": r.count} for r in by_status],
        "hourly_requests": [{"hour": str(r.hour), "count": r.count} for r in hourly],
    }
