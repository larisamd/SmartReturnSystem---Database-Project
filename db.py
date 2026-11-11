from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import current_app
from werkzeug.security import check_password_hash

from config import Config


DEMO_USERS = [
    {
        "id": 1,
        "name": "Aisha Rahman",
        "email": "customer@example.com",
        "password_hash": "Customer123!",
        "role": "Customer",
    },
    {
        "id": 2,
        "name": "Daniel Smith",
        "email": "support@example.com",
        "password_hash": "Support123!",
        "role": "Support Staff",
    },
    {
        "id": 3,
        "name": "Priya Nair",
        "email": "admin@example.com",
        "password_hash": "Admin123!",
        "role": "Administrator",
    },
    {
        "id": 6,
        "name": "Nisha Demo",
        "email": "nisha.demo@example.com",
        "password_hash": "NishaDemo26!",
        "role": "Customer",
    },
    {
        "id": 7,
        "name": "Arjun Demo",
        "email": "arjun.demo@example.com",
        "password_hash": "ArjunDemo26!",
        "role": "Customer",
    },
    {
        "id": 8,
        "name": "Meera Demo",
        "email": "meera.demo@example.com",
        "password_hash": "MeeraDemo26!",
        "role": "Customer",
    },
    {
        "id": 9,
        "name": "Kabir Demo",
        "email": "kabir.demo@example.com",
        "password_hash": "KabirDemo26!",
        "role": "Customer",
    },
    {
        "id": 10,
        "name": "Tara Demo",
        "email": "tara.demo@example.com",
        "password_hash": "TaraDemo26!",
        "role": "Customer",
    },
]

DEMO_PRODUCTS = [
    {"id": 101, "name": "Aurora Smartwatch", "category": "Electronics", "description": "Connected wearable with advanced fitness analytics.", "price": 149.99, "availability": True},
    {"id": 102, "name": "Nimbus Bluetooth Speaker", "category": "Audio", "description": "Portable speaker with deep bass and 18-hour battery life.", "price": 89.50, "availability": True},
    {"id": 103, "name": "Terra Yoga Mat", "category": "Fitness", "description": "Eco-friendly non-slip mat for daily workouts.", "price": 34.00, "availability": False},
    {"id": 104, "name": "Quill Mechanical Keyboard", "category": "Accessories", "description": "Silent mechanical keyboard designed for productivity.", "price": 119.00, "availability": True},
]

DEMO_ORDERS = [
    {"id": 5001, "customer_id": 1, "order_date": "2026-06-18", "status": "Delivered", "total": 149.99, "item_ids": "1"},
    {"id": 5002, "customer_id": 1, "order_date": "2026-08-20", "status": "Shipped", "total": 89.50, "item_ids": "2"},
    {"id": 5003, "customer_id": 6, "order_date": "2026-10-15", "status": "Delivered", "total": 358.49, "item_ids": "5, 6, 7"},
    {"id": 5004, "customer_id": 7, "order_date": "2026-10-16", "status": "Delivered", "total": 358.49, "item_ids": "8, 9, 10"},
    {"id": 5005, "customer_id": 8, "order_date": "2026-10-17", "status": "Delivered", "total": 358.49, "item_ids": "11, 12, 13"},
    {"id": 5006, "customer_id": 9, "order_date": "2026-10-18", "status": "Delivered", "total": 358.49, "item_ids": "14, 15, 16"},
    {"id": 5007, "customer_id": 10, "order_date": "2026-10-19", "status": "Delivered", "total": 358.49, "item_ids": "17, 18, 19"},
]

DEMO_RETURN_REQUESTS = [
    {"id": 7001, "order_item_id": 1, "customer_id": 1, "reason": "Defective display", "status": "Pending", "created_at": "2026-09-14 12:30:00"},
    {"id": 7002, "order_item_id": 2, "customer_id": 1, "reason": "Audio issue", "status": "Approved", "created_at": "2026-09-16 08:15:00"},
]

DEMO_COMPLAINTS = [
    {"id": 9001, "customer_id": 1, "product_id": 101, "order_item_id": 1, "assigned_staff_id": 2, "category": "Product Quality", "status": "Open", "created_at": "2026-09-15 09:45:00"},
    {"id": 9002, "customer_id": 1, "product_id": 102, "order_item_id": 2, "assigned_staff_id": 2, "category": "Shipping Delay", "status": "In Progress", "created_at": "2026-09-18 10:10:00"},
]

DEMO_REFUNDS = [
    {"id": 30, "return_id": 7002, "amount": 89.50, "status": "Processed"},
]

_ACTIVITY_LOG_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="complaint-activity")


def get_demo_user(email: str) -> Optional[Dict[str, Any]]:
    for user in DEMO_USERS:
        if user["email"] == email:
            return user
    return None


def validate_demo_password(email: str, password: str) -> bool:
    user = get_demo_user(email)
    if not user:
        return False
    if user["password_hash"] == password:
        return True
    return user["password_hash"] == password


def get_mysql_connection():
    try:
        import mysql.connector
    except ImportError:
        return None

    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            autocommit=False,
        )
        return conn
    except Exception:
        return None


def get_mongo_client():
    try:
        from pymongo import MongoClient
    except ImportError:
        return None

    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return client
    except Exception:
        return None


def get_demo_products() -> List[Dict[str, Any]]:
    return DEMO_PRODUCTS


def get_demo_orders_for_customer(customer_id: int) -> List[Dict[str, Any]]:
    return [order for order in DEMO_ORDERS if order["customer_id"] == customer_id]


def get_demo_returns_for_customer(customer_id: int) -> List[Dict[str, Any]]:
    return [one for one in DEMO_RETURN_REQUESTS if one["customer_id"] == customer_id]


def get_demo_complaints_for_customer(customer_id: int) -> List[Dict[str, Any]]:
    return [item for item in DEMO_COMPLAINTS if item["customer_id"] == customer_id]


def get_demo_complaints_for_staff(staff_id: int) -> List[Dict[str, Any]]:
    return [item for item in DEMO_COMPLAINTS if item["assigned_staff_id"] == staff_id]


def get_dashboard_summary():
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM Users u JOIN Roles r ON r.RoleID = u.RoleID WHERE r.RoleName = 'Customer') AS customers, "
                "(SELECT COUNT(*) FROM Users u JOIN Roles r ON r.RoleID = u.RoleID WHERE r.RoleName = 'Support Staff') AS support_staff, "
                "(SELECT COUNT(*) FROM Products) AS products, "
                "(SELECT COUNT(*) FROM ReturnRequests) AS return_requests, "
                "(SELECT COUNT(*) FROM Complaints) AS complaints, "
                "(SELECT COUNT(*) FROM Refunds) AS refunds;"
            )
            return cursor.fetchone()
        finally:
            conn.close()
    return {
        "customers": len([u for u in DEMO_USERS if u["role"] == "Customer"]),
        "support_staff": len([u for u in DEMO_USERS if u["role"] == "Support Staff"]),
        "products": len(DEMO_PRODUCTS),
        "return_requests": len(DEMO_RETURN_REQUESTS),
        "complaints": len(DEMO_COMPLAINTS),
        "refunds": len(DEMO_REFUNDS),
    }


def get_users_for_admin():
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT u.UserID AS id, u.Name AS name, u.Email AS email, r.RoleName AS role, "
                "u.IsActive AS is_active FROM Users u JOIN Roles r ON r.RoleID = u.RoleID "
                "ORDER BY r.RoleName, u.Name;"
            )
            return cursor.fetchall()
        finally:
            conn.close()
    return [
        {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"], "is_active": True}
        for user in DEMO_USERS
    ]


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    demo_user = get_demo_user(email)
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT u.UserID AS id, u.Name AS name, u.Email AS email, u.PasswordHash AS password_hash, r.RoleName AS role FROM Users u JOIN Roles r ON r.RoleID = u.RoleID WHERE u.Email = %s LIMIT 1;", (email,))
            user = cursor.fetchone()
            if user:
                stored_password = user["password_hash"]
                if stored_password == password or (
                    ":" in stored_password and check_password_hash(stored_password, password)
                ):
                    return user
            return None
        finally:
            conn.close()

    if demo_user and demo_user["password_hash"] == password:
        return demo_user
    return None


def get_products():
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT ProductID AS id, Name AS name, Description AS description, Category AS category, Price AS price, Availability AS availability FROM Products ORDER BY ProductID;")
            return cursor.fetchall()
        finally:
            conn.close()
    return get_demo_products()


def get_orders_for_customer(customer_id: int):
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT o.OrderID AS id, o.CustomerID AS customer_id, o.OrderDate AS order_date, "
                "o.OrderStatus AS status, o.TotalAmount AS total, "
                "GROUP_CONCAT(oi.OrderItemID ORDER BY oi.OrderItemID SEPARATOR ', ') AS item_ids "
                "FROM Orders o LEFT JOIN OrderItems oi ON oi.OrderID = o.OrderID "
                "WHERE o.CustomerID = %s GROUP BY o.OrderID, o.CustomerID, o.OrderDate, "
                "o.OrderStatus, o.TotalAmount ORDER BY o.OrderDate DESC;",
                (customer_id,),
            )
            return cursor.fetchall()
        finally:
            conn.close()
    return get_demo_orders_for_customer(customer_id)


def get_returns_for_customer(customer_id: int):
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT ReturnID AS id, OrderItemID AS order_item_id, CustomerID AS customer_id, Reason AS reason, Status AS status, CreatedAt AS created_at FROM ReturnRequests WHERE CustomerID = %s ORDER BY CreatedAt DESC;", (customer_id,))
            return cursor.fetchall()
        finally:
            conn.close()
    return get_demo_returns_for_customer(customer_id)


def get_complaints_for_customer(customer_id: int):
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT c.ComplaintID AS id, c.CustomerID AS customer_id, c.ProductID AS product_id, "
                "p.Name AS product_name, c.OrderItemID AS order_item_id, c.AssignedStaffID AS assigned_staff_id, "
                "c.Category AS category, c.Status AS status, c.CreatedAt AS created_at, u.Name AS customer_name, "
                "c.ClosedAt AS closed_at, c.ParentComplaintID AS parent_complaint_id, "
                "(c.Status = 'Closed' AND c.ClosedAt >= DATE_SUB(NOW(), INTERVAL 7 DAY)) AS can_reopen "
                "FROM Complaints c JOIN Products p ON p.ProductID = c.ProductID "
                "JOIN Users u ON u.UserID = c.CustomerID "
                "WHERE c.CustomerID = %s ORDER BY c.CreatedAt DESC;",
                (customer_id,),
            )
            return _attach_complaint_details(cursor.fetchall())
        finally:
            conn.close()
    return get_demo_complaints_for_customer(customer_id)


def get_complaints_for_staff(staff_id: int):
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT c.ComplaintID AS id, c.CustomerID AS customer_id, c.ProductID AS product_id, "
                "p.Name AS product_name, c.OrderItemID AS order_item_id, c.AssignedStaffID AS assigned_staff_id, "
                "c.Category AS category, c.Status AS status, c.CreatedAt AS created_at, u.Name AS customer_name, "
                "c.ClosedAt AS closed_at, c.ParentComplaintID AS parent_complaint_id "
                "FROM Complaints c JOIN Products p ON p.ProductID = c.ProductID "
                "JOIN Users u ON u.UserID = c.CustomerID "
                "WHERE c.AssignedStaffID = %s ORDER BY c.CreatedAt DESC;",
                (staff_id,),
            )
            return _attach_complaint_details(cursor.fetchall())
        finally:
            conn.close()
    return get_demo_complaints_for_staff(staff_id)


def get_complaints_for_admin():
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT c.ComplaintID AS id, c.CustomerID AS customer_id, c.ProductID AS product_id, "
                "p.Name AS product_name, c.OrderItemID AS order_item_id, c.AssignedStaffID AS assigned_staff_id, "
                "staff.Name AS assigned_staff_name, c.Category AS category, c.Status AS status, "
                "c.CreatedAt AS created_at, customer.Name AS customer_name, "
                "c.ClosedAt AS closed_at, c.ParentComplaintID AS parent_complaint_id "
                "FROM Complaints c JOIN Products p ON p.ProductID = c.ProductID "
                "JOIN Users customer ON customer.UserID = c.CustomerID "
                "LEFT JOIN Users staff ON staff.UserID = c.AssignedStaffID "
                "ORDER BY c.CreatedAt DESC;"
            )
            return _attach_complaint_details(cursor.fetchall())
        finally:
            conn.close()
    return DEMO_COMPLAINTS


def _attach_complaint_details(complaints):
    if not complaints:
        return complaints
    client = get_mongo_client()
    if client is None:
        return complaints
    try:
        detail_rows = client[Config.MONGO_DATABASE]["complaint_details"].find(
            {"complaint_id": {"$in": [item["id"] for item in complaints]}}
        )
        details = {item["complaint_id"]: item for item in detail_rows}
        for complaint in complaints:
            detail = details.get(complaint["id"], {})
            complaint["description"] = detail.get("detailed_description", "")
            complaint["evidence"] = detail.get("evidence_metadata", {})
        return complaints
    except Exception:
        return complaints
    finally:
        client.close()


def get_complaint_responses(complaint_ids):
    if not complaint_ids:
        return {}
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            placeholders = ",".join(["%s"] * len(complaint_ids))
            cursor.execute(
                "SELECT cr.ComplaintID AS complaint_id, cr.AuthorUserID AS author_id, "
                "u.Name AS author_name, r.RoleName AS author_role, cr.Message AS message, "
                "cr.CreatedAt AS created_at FROM ComplaintResponses cr "
                "JOIN Users u ON u.UserID = cr.AuthorUserID "
                "JOIN Roles r ON r.RoleID = u.RoleID "
                f"WHERE cr.ComplaintID IN ({placeholders}) ORDER BY cr.CreatedAt;",
                tuple(complaint_ids),
            )
            responses = {}
            for row in cursor.fetchall():
                responses.setdefault(row["complaint_id"], []).append(row)
            return responses
        finally:
            conn.close()
    return {}


def get_closed_followup_candidates(customer_id: int):
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT c.ComplaintID AS id, c.Category AS category, c.ClosedAt AS closed_at, "
                "c.ProductID AS product_id, p.Name AS product_name "
                "FROM Complaints c JOIN Products p ON p.ProductID = c.ProductID "
                "WHERE c.CustomerID = %s AND c.Status = 'Closed' "
                "AND c.ClosedAt < DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY c.ClosedAt DESC;",
                (customer_id,),
            )
            return cursor.fetchall()
        finally:
            conn.close()
    return []


def get_support_staff():
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT u.UserID AS id, u.Name AS name FROM Users u "
                "JOIN Roles r ON r.RoleID = u.RoleID "
                "WHERE r.RoleName = 'Support Staff' AND u.IsActive = 1 ORDER BY u.Name;"
            )
            return cursor.fetchall()
        finally:
            conn.close()
    return [{"id": user["id"], "name": user["name"]} for user in DEMO_USERS if user["role"] == "Support Staff"]


def _get_return_rows(where_clause="", params=()):
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT rr.ReturnID AS id, rr.OrderItemID AS order_item_id, rr.CustomerID AS customer_id, "
                "customer.Name AS customer_name, rr.Reason AS reason, rr.Status AS status, "
                "rr.ApprovedBy AS approved_by, rr.CreatedAt AS created_at, oi.OrderID AS order_id, "
                "p.Name AS product_name, (oi.UnitPrice * oi.Quantity) AS amount, "
                "COALESCE(rf.Status, '') AS refund_status "
                "FROM ReturnRequests rr JOIN Users customer ON customer.UserID = rr.CustomerID "
                "JOIN OrderItems oi ON oi.OrderItemID = rr.OrderItemID "
                "JOIN Products p ON p.ProductID = oi.ProductID "
                "LEFT JOIN Refunds rf ON rf.ReturnID = rr.ReturnID "
                f"{where_clause} ORDER BY rr.CreatedAt DESC;",
                params,
            )
            return cursor.fetchall()
        finally:
            conn.close()
    return None


def get_returns_for_staff():
    rows = _get_return_rows("WHERE rr.Status = 'Pending'")
    if rows is not None:
        return rows
    return [item for item in DEMO_RETURN_REQUESTS if item["status"] == "Pending"]


def get_returns_for_admin():
    rows = _get_return_rows()
    return rows if rows is not None else DEMO_RETURN_REQUESTS


def create_return_request(customer_id: int, order_item_id: int, reason: str):
    if order_item_id < 1 or not reason.strip():
        return {"success": False, "message": "Choose a valid order item and provide a return reason."}

    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT OrderItemID FROM OrderItems oi JOIN Orders o ON o.OrderID = oi.OrderID "
                "WHERE oi.OrderItemID = %s AND o.CustomerID = %s FOR UPDATE;",
                (order_item_id, customer_id),
            )
            if cursor.fetchone() is None:
                conn.rollback()
                return {"success": False, "message": "That order item does not belong to your account."}

            cursor.execute(
                "SELECT ReturnID FROM ReturnRequests WHERE OrderItemID = %s "
                "AND Status IN ('Pending', 'Approved', 'Processing', 'Completed') LIMIT 1;",
                (order_item_id,),
            )
            if cursor.fetchone() is not None:
                conn.rollback()
                return {"success": False, "message": "A return request already exists for this order item."}

            cursor.execute(
                "INSERT INTO ReturnRequests (OrderItemID, CustomerID, Reason, Status, CreatedAt, UpdatedAt) "
                "VALUES (%s, %s, %s, 'Pending', NOW(), NOW());",
                (order_item_id, customer_id, reason.strip()),
            )
            conn.commit()
            return {"success": True, "message": "Return request submitted."}
        except Exception as exc:
            conn.rollback()
            if getattr(exc, "errno", None) == 1062:
                return {"success": False, "message": "A return request already exists for this order item."}
            raise
        finally:
            conn.close()
    if any(
        item["order_item_id"] == order_item_id
        and item["customer_id"] == customer_id
        and item["status"] in {"Pending", "Approved", "Processing", "Completed"}
        for item in DEMO_RETURN_REQUESTS
    ):
        return {"success": False, "message": "A return request already exists for this order item."}
    belongs_to_customer = any(
        order["customer_id"] == customer_id
        and str(order_item_id) in {
            item_id.strip() for item_id in (order.get("item_ids") or "").split(",")
        }
        for order in DEMO_ORDERS
    )
    if not belongs_to_customer:
        return {"success": False, "message": "That order item does not belong to your account."}

    return_id = max((item["id"] for item in DEMO_RETURN_REQUESTS), default=7000) + 1
    DEMO_RETURN_REQUESTS.append({
        "id": return_id,
        "order_item_id": order_item_id,
        "customer_id": customer_id,
        "reason": reason.strip(),
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    return {"success": True, "message": "Return request submitted using demo mode."}


def create_complaint(
    customer_id: int,
    product_id: int,
    category: str,
    description: str,
    evidence: str,
    parent_complaint_id: Optional[int] = None,
):
    if product_id < 1 or not description.strip():
        return {"success": False, "message": "Choose a valid product and provide a complaint description."}

    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT ProductID FROM Products WHERE ProductID = %s;", (product_id,))
            if cursor.fetchone() is None:
                conn.rollback()
                return {"success": False, "message": "The selected product no longer exists. Refresh and choose another product."}

            if parent_complaint_id is not None:
                cursor.execute(
                    "SELECT ComplaintID FROM Complaints WHERE ComplaintID = %s AND CustomerID = %s "
                    "AND ProductID = %s AND Status = 'Closed' "
                    "AND ClosedAt < DATE_SUB(NOW(), INTERVAL 7 DAY);",
                    (parent_complaint_id, customer_id, product_id),
                )
                if cursor.fetchone() is None:
                    conn.rollback()
                    return {"success": False, "message": "Choose one of your complaints that has been closed for more than 7 days, and select its product."}

            cursor.execute(
                "INSERT INTO Complaints (CustomerID, ProductID, Category, Status, ParentComplaintID, CreatedAt, UpdatedAt) "
                "VALUES (%s, %s, %s, 'Open', %s, NOW(), NOW());",
                (customer_id, product_id, category, parent_complaint_id),
            )
            complaint_id = cursor.lastrowid
            conn.commit()
            mongo_client = get_mongo_client()
            if mongo_client:
                mongo_client[Config.MONGO_DATABASE]["complaint_details"].insert_one({
                    "complaint_id": complaint_id,
                    "detailed_description": description,
                    "evidence_metadata": {"source": evidence},
                    "product_condition": "Unknown",
                    "tags": [category.lower()],
                    "extra_details": {"parent_complaint_id": parent_complaint_id},
                })
                mongo_client[Config.MONGO_DATABASE]["activity_logs"].insert_one({
                    "complaint_id": complaint_id,
                    "event_type": "submitted",
                    "actor_id": customer_id,
                    "event_details": description,
                    "timestamp": __import__("datetime").datetime.utcnow(),
                })
            return {"success": True, "id": complaint_id, "message": "Complaint submitted successfully."}
        except Exception as exc:
            conn.rollback()
            if getattr(exc, "errno", None) == 1452:
                return {"success": False, "message": "The selected product or customer record is no longer available. Refresh and try again."}
            raise
        finally:
            conn.close()
    if not any(product["id"] == product_id for product in DEMO_PRODUCTS):
        return {"success": False, "message": "Select a product from the catalog."}
    if parent_complaint_id is not None:
        return {"success": False, "message": "Linked follow-ups require the MySQL database."}
    return {"success": True, "id": 999, "message": "Complaint submitted successfully in demo mode."}


def _log_complaint_activity(complaint_id: int, event_type: str, actor_id: int, event_details: str):
    app = current_app._get_current_object()
    _ACTIVITY_LOG_EXECUTOR.submit(
        _write_complaint_activity,
        app,
        complaint_id,
        event_type,
        actor_id,
        event_details,
    )


def _write_complaint_activity(app, complaint_id: int, event_type: str, actor_id: int, event_details: str):
    with app.app_context():
        _write_complaint_activity_to_mongo(complaint_id, event_type, actor_id, event_details)


def _write_complaint_activity_to_mongo(complaint_id: int, event_type: str, actor_id: int, event_details: str):
    client = get_mongo_client()
    if client is None:
        return
    try:
        client[Config.MONGO_DATABASE]["activity_logs"].insert_one({
            "complaint_id": complaint_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "event_details": event_details,
            "timestamp": __import__("datetime").datetime.utcnow(),
        })
    except Exception:
        current_app.logger.exception("Could not write complaint activity to MongoDB")
    finally:
        client.close()


def assign_complaint(complaint_id: int, staff_id: int, admin_id: int):
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT u.UserID FROM Users u JOIN Roles r ON r.RoleID = u.RoleID "
                "WHERE u.UserID = %s AND u.IsActive = 1 AND r.RoleName = 'Support Staff';",
                (staff_id,),
            )
            if cursor.fetchone() is None:
                conn.rollback()
                return {"success": False, "message": "Select an active support staff account."}
            cursor.execute("SELECT ComplaintID FROM Complaints WHERE ComplaintID = %s FOR UPDATE;", (complaint_id,))
            if cursor.fetchone() is None:
                conn.rollback()
                return {"success": False, "message": "Complaint not found."}
            cursor.execute(
                "UPDATE Complaints SET AssignedStaffID = %s WHERE ComplaintID = %s;",
                (staff_id, complaint_id),
            )
            cursor.execute(
                "INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details) "
                "VALUES (%s, 'Assigned complaint', 'Complaints', %s, %s);",
                (admin_id, complaint_id, f"Assigned to support staff user {staff_id}"),
            )
            conn.commit()
            _log_complaint_activity(complaint_id, "assigned", admin_id, f"Assigned to staff {staff_id}")
            return {"success": True, "message": "Complaint assigned."}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    complaint = next((item for item in DEMO_COMPLAINTS if item["id"] == complaint_id), None)
    staff = get_demo_user_by_id(staff_id)
    if complaint is None or not staff or staff["role"] != "Support Staff":
        return {"success": False, "message": "Complaint or support staff account not found."}
    complaint["assigned_staff_id"] = staff_id
    return {"success": True, "message": "Complaint assigned in demo mode."}


def get_demo_user_by_id(user_id: int):
    return next((user for user in DEMO_USERS if user["id"] == user_id), None)


def update_complaint_status(complaint_id: int, status: str, actor_id: int, actor_role: str):
    allowed_statuses = {"Open", "In Progress", "Resolved", "Closed", "Escalated"}
    if status not in allowed_statuses:
        return {"success": False, "message": "Choose a valid complaint status."}
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT AssignedStaffID FROM Complaints WHERE ComplaintID = %s FOR UPDATE;",
                (complaint_id,),
            )
            complaint = cursor.fetchone()
            if complaint is None:
                conn.rollback()
                return {"success": False, "message": "Complaint not found."}
            if actor_role == "Support Staff" and complaint["AssignedStaffID"] != actor_id:
                conn.rollback()
                return {"success": False, "message": "This complaint is not assigned to you."}
            cursor.execute(
                "UPDATE Complaints SET Status = %s, "
                "ClosedAt = CASE WHEN %s = 'Closed' THEN COALESCE(ClosedAt, NOW()) ELSE NULL END, "
                "UpdatedAt = NOW() WHERE ComplaintID = %s;",
                (status, status, complaint_id),
            )
            cursor.execute(
                "INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details) "
                "VALUES (%s, %s, 'Complaints', %s, %s);",
                (actor_id, "Updated complaint status", complaint_id, f"Status set to {status}"),
            )
            conn.commit()
            _log_complaint_activity(complaint_id, "status_update", actor_id, f"Status set to {status}")
            return {"success": True, "message": "Complaint status updated."}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    complaint = next((item for item in DEMO_COMPLAINTS if item["id"] == complaint_id), None)
    if complaint is None or (actor_role == "Support Staff" and complaint["assigned_staff_id"] != actor_id):
        return {"success": False, "message": "Complaint not found or not assigned to you."}
    complaint["status"] = status
    complaint["closed_at"] = __import__("datetime").datetime.utcnow() if status == "Closed" else None
    return {"success": True, "message": "Complaint status updated in demo mode."}


def add_complaint_response(complaint_id: int, author_id: int, author_role: str, message: str):
    message = message.strip()
    if not message:
        return {"success": False, "message": "Response cannot be empty."}
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT CustomerID, AssignedStaffID, Status FROM Complaints WHERE ComplaintID = %s FOR UPDATE;",
                (complaint_id,),
            )
            complaint = cursor.fetchone()
            permitted = complaint is not None and (
                author_role == "Administrator"
                or (author_role == "Customer" and complaint["CustomerID"] == author_id)
                or (author_role == "Support Staff" and complaint["AssignedStaffID"] == author_id)
            )
            if not permitted:
                conn.rollback()
                return {"success": False, "message": "You do not have access to this complaint."}
            if complaint["Status"] == "Closed":
                conn.rollback()
                return {"success": False, "message": "This complaint is closed. Reopen it within 7 days to continue the conversation."}
            cursor.execute(
                "INSERT INTO ComplaintResponses (ComplaintID, AuthorUserID, Message) VALUES (%s, %s, %s);",
                (complaint_id, author_id, message),
            )
            reopened = author_role == "Customer" and complaint["Status"] == "Resolved"
            if reopened:
                cursor.execute(
                    "UPDATE Complaints SET Status = 'In Progress', UpdatedAt = NOW() WHERE ComplaintID = %s;",
                    (complaint_id,),
                )
                cursor.execute(
                    "INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details) "
                    "VALUES (%s, 'Reopened complaint', 'Complaints', %s, 'Customer replied to a resolved complaint');",
                    (author_id, complaint_id),
                )
            cursor.execute(
                "INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details) "
                "VALUES (%s, 'Added complaint response', 'Complaints', %s, 'Response added');",
                (author_id, complaint_id),
            )
            conn.commit()
            _log_complaint_activity(complaint_id, "response_added", author_id, message)
            if reopened:
                _log_complaint_activity(complaint_id, "reopened", author_id, "Customer replied to a resolved complaint")
                return {"success": True, "message": "Reply sent. The complaint has been reopened and returned to In Progress."}
            return {"success": True, "message": "Response sent."}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    complaint = next((item for item in DEMO_COMPLAINTS if item["id"] == complaint_id), None)
    if complaint is not None and complaint["status"] == "Closed":
        return {"success": False, "message": "This complaint is closed. Reopen it within 7 days to continue the conversation."}
    permitted = complaint is not None and (
        author_role == "Administrator"
        or (author_role == "Customer" and complaint["customer_id"] == author_id)
        or (author_role == "Support Staff" and complaint["assigned_staff_id"] == author_id)
    )
    if not permitted:
        return {"success": False, "message": "You do not have access to this complaint."}
    if author_role == "Customer" and complaint["status"] == "Resolved":
        complaint["status"] = "In Progress"
        return {"success": True, "message": "Reply sent. The complaint has been reopened in demo mode."}
    return {"success": True, "message": "Response sent in demo mode."}


def reopen_complaint(complaint_id: int, customer_id: int, reason: str):
    reason = reason.strip()
    if not reason:
        return {"success": False, "message": "Please explain why this complaint needs to be reopened."}
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT ComplaintID FROM Complaints WHERE ComplaintID = %s AND CustomerID = %s "
                "AND Status = 'Closed' AND ClosedAt >= DATE_SUB(NOW(), INTERVAL 7 DAY) FOR UPDATE;",
                (complaint_id, customer_id),
            )
            if cursor.fetchone() is None:
                conn.rollback()
                return {"success": False, "message": "This complaint cannot be reopened. The 7-day reopen period may have expired."}
            cursor.execute(
                "INSERT INTO ComplaintResponses (ComplaintID, AuthorUserID, Message) VALUES (%s, %s, %s);",
                (complaint_id, customer_id, f"Reopen request: {reason}"),
            )
            cursor.execute(
                "UPDATE Complaints SET Status = 'In Progress', ClosedAt = NULL, UpdatedAt = NOW() "
                "WHERE ComplaintID = %s;",
                (complaint_id,),
            )
            cursor.execute(
                "INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details) "
                "VALUES (%s, 'Reopened complaint', 'Complaints', %s, %s);",
                (customer_id, complaint_id, reason),
            )
            conn.commit()
            _log_complaint_activity(complaint_id, "reopened", customer_id, reason)
            return {"success": True, "message": "Complaint reopened and returned to In Progress."}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    complaint = next((item for item in DEMO_COMPLAINTS if item["id"] == complaint_id), None)
    if complaint is None or complaint["customer_id"] != customer_id or complaint["status"] != "Closed":
        return {"success": False, "message": "This complaint cannot be reopened in demo mode."}
    return {"success": False, "message": "Reopening a closed complaint requires MySQL."}


def decide_return(return_id: int, decision: str, actor_id: int):
    if decision not in {"Approved", "Rejected"}:
        return {"success": False, "message": "Choose approve or reject."}
    conn = get_mysql_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT rr.Status AS status, oi.UnitPrice * oi.Quantity AS amount "
                "FROM ReturnRequests rr JOIN OrderItems oi ON oi.OrderItemID = rr.OrderItemID "
                "WHERE rr.ReturnID = %s FOR UPDATE;",
                (return_id,),
            )
            item = cursor.fetchone()
            if item is None or item["status"] != "Pending":
                conn.rollback()
                return {"success": False, "message": "This return is no longer pending."}
            cursor.execute(
                "UPDATE ReturnRequests SET Status = %s, ApprovedBy = %s, UpdatedAt = NOW() "
                "WHERE ReturnID = %s AND Status = 'Pending';",
                (decision, actor_id, return_id),
            )
            if decision == "Approved":
                cursor.execute(
                    "INSERT INTO Refunds (ReturnID, Amount, Status) VALUES (%s, %s, 'Processing');",
                    (return_id, item["amount"]),
                )
            cursor.execute(
                "INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details) "
                "VALUES (%s, %s, 'ReturnRequests', %s, %s);",
                (actor_id, f"{decision} return", return_id, f"Return {decision.lower()}"),
            )
            conn.commit()
            return {"success": True, "message": f"Return {decision.lower()}."}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    item = next((item for item in DEMO_RETURN_REQUESTS if item["id"] == return_id), None)
    if item is None or item["status"] != "Pending":
        return {"success": False, "message": "This return is no longer pending."}
    item["status"] = decision
    return {"success": True, "message": f"Return {decision.lower()} in demo mode."}


def get_db_health():
    mysql_ok = get_mysql_connection() is not None
    mongo_ok = get_mongo_client() is not None
    return {"mysql": mysql_ok, "mongodb": mongo_ok}
