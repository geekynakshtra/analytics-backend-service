from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Index,
    Date,
)
from sqlalchemy.sql import func

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    country = Column(String(80), nullable=False)
    created_at = Column(DateTime, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False)


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String(120), nullable=False)
    created_at = Column(DateTime, nullable=False)


class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"

    id = Column(Integer, primary_key=True)
    total_orders = Column(Integer, nullable=False, default=0)
    total_revenue = Column(Numeric(14, 2), nullable=False, default=0)
    total_refunds = Column(Numeric(14, 2), nullable=False, default=0)
    net_revenue = Column(Numeric(14, 2), nullable=False, default=0)
    average_order_value = Column(Numeric(14, 2), nullable=False, default=0)
    repeat_customer_revenue = Column(Numeric(14, 2), nullable=False, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RevenueTrend(Base):
    __tablename__ = "revenue_trends"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    revenue = Column(Numeric(14, 2), nullable=False, default=0)
    refunds = Column(Numeric(14, 2), nullable=False, default=0)
    net_revenue = Column(Numeric(14, 2), nullable=False, default=0)


class TopCustomer(Base):
    __tablename__ = "top_customers"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    customer_name = Column(String(120), nullable=False)
    email = Column(String(150), nullable=False)
    total_spend = Column(Numeric(14, 2), nullable=False)
    order_count = Column(Integer, nullable=False)


Index("idx_orders_customer_id", Order.customer_id)
Index("idx_orders_created_at", Order.created_at)
Index("idx_orders_status", Order.status)

Index("idx_refunds_order_id", Refund.order_id)
Index("idx_refunds_customer_id", Refund.customer_id)
Index("idx_refunds_created_at", Refund.created_at)

Index("idx_revenue_trends_date", RevenueTrend.date)
Index("idx_top_customers_spend", TopCustomer.total_spend.desc())