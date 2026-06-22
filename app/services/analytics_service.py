from sqlalchemy import text
from sqlalchemy.orm import Session


def refresh_analytics(db: Session):
    refresh_summary(db)
    refresh_revenue_trends(db)
    refresh_top_customers(db)

    return {
        "message": "Analytics refreshed successfully"
    }


def refresh_summary(db: Session):
    db.execute(text("DELETE FROM analytics_summary"))

    db.execute(
        text(
            """
            INSERT INTO analytics_summary (
                id,
                total_orders,
                total_revenue,
                total_refunds,
                net_revenue,
                average_order_value,
                repeat_customer_revenue,
                updated_at
            )
            SELECT
                1 AS id,

                COUNT(*) AS total_orders,

                COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) AS total_revenue,

                (
                    SELECT COALESCE(SUM(amount), 0)
                    FROM refunds
                ) AS total_refunds,

                COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0)
                -
                (
                    SELECT COALESCE(SUM(amount), 0)
                    FROM refunds
                ) AS net_revenue,

                COALESCE(AVG(CASE WHEN status = 'completed' THEN amount END), 0) AS average_order_value,

                (
                    SELECT COALESCE(SUM(amount), 0)
                    FROM orders
                    WHERE status = 'completed'
                    AND customer_id IN (
                        SELECT customer_id
                        FROM orders
                        WHERE status = 'completed'
                        GROUP BY customer_id
                        HAVING COUNT(*) > 1
                    )
                ) AS repeat_customer_revenue,

                NOW() AS updated_at
            FROM orders
            """
        )
    )

    db.commit()


def refresh_revenue_trends(db: Session):
    db.execute(text("DELETE FROM revenue_trends"))

    db.execute(
        text(
            """
            INSERT INTO revenue_trends (
                date,
                revenue,
                refunds,
                net_revenue
            )
            SELECT
                order_dates.date,

                COALESCE(order_dates.revenue, 0) AS revenue,

                COALESCE(refund_dates.refunds, 0) AS refunds,

                COALESCE(order_dates.revenue, 0)
                -
                COALESCE(refund_dates.refunds, 0) AS net_revenue

            FROM (
                SELECT
                    DATE(created_at) AS date,
                    SUM(amount) AS revenue
                FROM orders
                WHERE status = 'completed'
                GROUP BY DATE(created_at)
            ) order_dates

            LEFT JOIN (
                SELECT
                    DATE(created_at) AS date,
                    SUM(amount) AS refunds
                FROM refunds
                GROUP BY DATE(created_at)
            ) refund_dates
            ON order_dates.date = refund_dates.date

            ORDER BY order_dates.date
            """
        )
    )

    db.commit()


def refresh_top_customers(db: Session, limit: int = 100):
    db.execute(text("DELETE FROM top_customers"))

    db.execute(
        text(
            """
            INSERT INTO top_customers (
                customer_id,
                customer_name,
                email,
                total_spend,
                order_count
            )
            SELECT
                c.id AS customer_id,
                c.name AS customer_name,
                c.email AS email,
                SUM(o.amount) AS total_spend,
                COUNT(o.id) AS order_count
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            WHERE o.status = 'completed'
            GROUP BY c.id, c.name, c.email
            ORDER BY total_spend DESC
            LIMIT :limit
            """
        ),
        {
            "limit": limit
        },
    )

    db.commit()