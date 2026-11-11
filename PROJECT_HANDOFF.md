# Smart Product Return & Complaint Management System

## Project Summary

This is a college project that demonstrates how an online store could manage product returns and customer complaints. Customers can look at products and their own orders, ask to return an item, and submit or reply to a complaint. Support staff handle complaints assigned to them and review pending return requests. Administrators can see all complaints and returns, assign complaints to support staff, and review system-level counts.

The application is a working prototype, not a complete production store. It does not take orders, ship goods, make payments, or upload evidence files.

## Technology Stack

- **Frontend:** HTML templates rendered by Flask, Bootstrap 5, custom CSS, and a small JavaScript file.
- **Backend:** Python and Flask. Routes handle browser requests, check the signed-in user's role, call database functions, then render pages or show feedback.
- **Relational database:** MySQL. It stores accounts, catalog products, orders, return requests, complaints, responses, refunds, and audit entries.
- **Document database:** MongoDB Atlas. It stores flexible complaint details and complaint activity events.
- **Configuration:** `.env` stores local credentials and the Flask secret. It is ignored by Git. Do not give `.env` to teammates; share `.env.example` and have each person configure their own credentials.

## How to Start It

From the project directory, install requirements, configure `.env`, then run:

```powershell
c:/python314/python.exe -m pip install -r requirements.txt
c:/python314/python.exe app.py
```

Open `http://localhost:5000/login`. MySQL should be running with the `smart_return_system` database initialized. Configure `MONGO_URI` to the Atlas connection string if MongoDB is to be used. Never put the Atlas password or Flask secret into source code or a shared chat.

`schema.sql` is an initialization script and begins by dropping and recreating `smart_return_system`. Do not run it against a database containing work you want to keep. For an existing installation, apply `complaint_closure_migration.sql` once; fresh schemas already include its columns. `advanced_queries.sql` contains academic examples and is separate from normal app startup.

## Database Responsibilities

### MySQL: authoritative application records

MySQL is the source of truth for ownership, statuses, transactions, and relationships. The schema has ten tables:

| Table | Purpose and relationships |
|---|---|
| `Roles` | Names the Customer, Support Staff, and Administrator roles. |
| `Users` | Account identity and password hash; each user references one role. |
| `Products` | Product catalog, category, price, and availability. |
| `Orders` | Belongs to a customer. |
| `OrderItems` | Connects an order to a product and records quantity and price at purchase. |
| `ReturnRequests` | Belongs to a customer and an order item; stores reason, status, approver, and timestamps. |
| `Complaints` | Belongs to a customer and product; may reference an order item and assigned staff member. |
| `ComplaintResponses` | Messages on a complaint, authored by a user. |
| `Refunds` | Refund record for a return; each return can have at most one refund. |
| `AuditLogs` | Records actions and their actor/entity references. |

The main relationship chain is `Users -> Orders -> OrderItems -> Products`. A return refers to an order item and customer. A complaint refers to a customer and product, and can optionally refer to an order item and support staff. Responses refer to both their complaint and author. Refunds refer to returns. Foreign keys enforce these relationships inside MySQL.

### MongoDB Atlas: flexible complaint data

Two collections are used in the `smart_return_system` database:

- `complaint_details` stores a complaint's long description, evidence metadata, product condition, tags, and optional extra fields.
- `activity_logs` stores events such as submission, assignment, status changes, and responses.

The `complaint_id` field in these documents corresponds to MySQL's `Complaints.ComplaintID`. MongoDB cannot enforce a foreign key back to MySQL, so application code uses the MySQL ID when writing/reading complaint documents. No complete relational table is copied into MongoDB.

The current complaint creation flow commits the MySQL complaint before attempting MongoDB writes. Mongo activity writes from later actions are best-effort. This means the two databases can become inconsistent if Atlas is unavailable at the wrong time; there is not yet a persistent retry/outbox recovery screen.

## User Workflows

### Customer

1. Sign in.
2. Browse products and view their own orders.
3. Submit a return request using an order-item ID shown on the order page, with a reason.
4. Submit a complaint by selecting a product from the actual catalog, selecting a category, and describing the issue. Evidence is currently metadata/text only; files are not uploaded.
5. View their own return and complaint statuses.
6. Reply to their own complaints and read the response thread. Replies to Resolved complaints automatically move them back to In Progress.
7. Reopen a Closed complaint with a reason within 7 days. For older closures, submit a new complaint linked as a follow-up.

Customers cannot view other customers' orders, returns, or complaints through the customer queries.

### Support Staff

1. Open **Complaint Queue** to view complaints assigned to their user ID.
2. Read complaint descriptions/evidence metadata when those MongoDB documents exist.
3. Reply to those complaints and update their status.
4. Open **Return Queue** to see all pending return requests.
5. Approve or reject a pending return. Approval updates the return, creates a simulated refund in `Processing` status for the order-item value, and writes an audit record. No payment is sent.

Support staff do not see complaints assigned to someone else. They see pending returns system-wide; return assignment is not currently modeled.

### Administrator

1. Open the admin page to see live MySQL/MongoDB health indicators and current summary counts.
2. Open **Complaint Queue** to see all complaints, assign them to active support staff, reply, or update status.
3. Open **Return Queue** to see all returns and make decisions on pending ones.
4. View the live user list, including name, email, and role.

The admin page is not full CRUD. It does not currently create, edit, deactivate, or delete users/products/orders. Audit rows are recorded for selected workflow actions, but there is no dedicated audit-history page.

## Routes and Pages

| Route | Access | Purpose |
|---|---|---|
| `/login` | Public | Sign in. |
| `/logout` | Signed-in user | Clear the session. |
| `/dashboard` | Signed-in user | Summary cards and recent activity/database health. |
| `/products` | Signed-in user | Browse the catalog. |
| `/orders` | Customer | View own orders and order-item IDs. |
| `/returns` | Signed-in user | Customer submits/views own returns; staff sees pending returns; admin sees all returns. |
| `/complaints` | Signed-in user | Customer submits/views own complaints; staff sees assigned complaints; admin sees all complaints. |
| `/complaints/<id>/responses` | Customer, assigned staff, or admin | Add a complaint response; backend checks ownership/assignment. |
| `/complaints/<id>/reopen` | Customer who owns the complaint | Reopen a complaint closed within the last 7 days; reason is recorded as a response and in the audit log. |
| `/complaints/<id>/status` | Assigned staff or admin | Update complaint status. |
| `/complaints/<id>/assign` | Admin | Assign complaint to active support staff. |
| `/returns/<id>/decision` | Staff or admin | Approve or reject a pending return. |
| `/admin` | Admin | System counts, queue links, user list. |
| `/support` | Support staff | Redirects to the complaint queue. |

Role restrictions are enforced server-side by Flask decorators and workflow checks; hiding a link in the template is not the authorization mechanism.

## Return and Complaint Rules Currently Enforced

- A return item must belong to the signed-in customer.
- A duplicate request is blocked while that order item has a pending/approved/processing/completed return.
- A return decision only applies while the request is pending.
- Approval creates one refund for the order-item quantity times its stored unit price.
- A complaint product must exist in MySQL.
- Support staff may update/reply only to complaints assigned to them; admins may access all; customers may reply only to their own complaints.
- Resolved complaints still accept messages; a customer reply reopens the case as In Progress. Closed complaints reject ordinary messages. Customers can explicitly reopen within 7 days; older cases can be followed up with a new linked complaint.
- Complaint and return actions write audit records in MySQL.

There is no configurable return time limit, warranty rule, real courier flow, or real payment integration yet. The return eligibility policy is therefore much simpler than a retail production system.

## ADBMS Demonstration Files

`schema.sql` includes all ten tables, seed rows, constraints, indexes, two views, a refund calculation function, stored procedures, and status audit triggers. `advanced_queries.sql` demonstrates joins, nested/correlated queries, aggregation, views, function/procedure calls, and transaction examples. `mongodb_init.js` creates indexes and sample MongoDB complaint/activity documents.

## Current Limitations to Know

- No customer registration or profile edit page.
- No administrator CRUD for users, roles, products, or orders; the product page is browse-only.
- No order-placement workflow.
- No dedicated refunds page or manual refund-status management. Refund creation happens on return approval.
- No dedicated reports or audit-history browser, though summary counts and audit records exist.
- No file upload; the complaint form stores evidence as text metadata.
- MongoDB synchronization has no durable retry/outbox mechanism if Atlas is unavailable.
- Some demo accounts are hard-coded in the development login fallback. The initial `schema.sql` seed also uses plaintext demo passwords, despite the `PasswordHash` column name. Replace these for any non-demo use; new customer rows should contain Werkzeug hashes compatible with `check_password_hash`.
- If MySQL is unavailable, selected functions fall back to static demo data. New demo-mode return/complaint writes are not durable. Use a live MySQL database for meaningful demonstrations.
- The current test suite covers route access, order rendering, duplicate return feedback, catalog product selection, queue visibility/actions, and Closed/Resolved reply behavior. It does not exhaustively test every workflow against isolated database instances.

## Live Demo State Verified

At the time of this handoff, the configured MySQL database had five initial products, five initial users, four orders/order items, six initial complaints before additional demo seed data, and three initial return requests. Admin and support queue pages rendered successfully. The configured database was upgraded with `complaint_closure_migration.sql` changes (closure timestamp and self-referencing follow-up ID). The automated test suite passed 16 tests.
