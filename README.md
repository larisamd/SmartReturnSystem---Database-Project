# Smart Product Return & Complaint Management System

This project is a full-stack Flask application for product returns, support complaints, refunds, and dashboard reporting. It uses MySQL for transactional records and MongoDB for complaint-related documents and activity logs.

## Technology stack

- Frontend: HTML, CSS, Bootstrap, JavaScript
- Backend: Python Flask
- Database: MySQL Server + MongoDB
- Connectors: mysql-connector-python, pymongo

## Project structure

- `app.py` – Flask app entry point
- `routes.py` – route logic and role-based access controls
- `db.py` – database helpers and demo fallback logic
- `config.py` – environment configuration
- `schema.sql` – MySQL schema, seed data, and advanced database objects
- `demo_return_data_migration.sql` – additive demo customer accounts and delivered orders
- `advanced_queries.sql` – example ADBMS queries and SQL demonstrations
- `mongodb_init.js` – MongoDB schema and indexes
- `templates/` – dashboard HTML templates
- `static/` – CSS and JavaScript assets
- `tests/` – regression tests for route behavior

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   . .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate  # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment file and configure your database credentials:

   ```bash
   copy .env.example .env
   ```

4. Update `.env` with your MySQL and MongoDB settings.

## Database initialization

### MySQL

```bash
mysql -u root -p < schema.sql
```

`schema.sql` drops and recreates the database. If you already have data, do not run it again. For an existing database, apply the complaint messaging lifecycle change once instead:

```bash
mysql -u root -p < complaint_closure_migration.sql
```

Fresh databases created from the current `schema.sql` already contain these columns, so they do not need this migration.

To add the demo customer accounts and delivered products used for return-request demonstrations, apply the additive seed migration after creating the schema:

```bash
mysql -u root -p smart_return_system < demo_return_data_migration.sql
```

This migration is safe to rerun and does not drop existing data. For an existing database, run this migration directly; do not rerun `schema.sql`.

### MongoDB

For MongoDB Atlas, set `MONGO_URI` in `.env` to the connection string from Atlas under **Connect > Shell**. Replace the username, password, and cluster host with your Atlas values. If the password contains reserved URI characters, URL-encode it.

In Atlas, add your current public IP under **Network Access** and create a database user under **Database Access**. Do not use your Atlas website login as the database username.

Run the initialization script against that Atlas cluster (replace the URI with your actual connection string):

```bash
mongosh "mongodb+srv://<db-user>:<url-encoded-password>@<cluster-host>/?retryWrites=true&w=majority&appName=smart-return-system" --file mongodb_init.js
```

The script selects the `smart_return_system` database. The same URI must be configured as `MONGO_URI` in `.env` for the Flask app. `mongosh < mongodb_init.js` without a URI connects to `localhost:27017`, not Atlas.

## Run the app

```bash
python app.py
```

Then open http://localhost:5000/login.

## Demo accounts

- Customer: `customer@example.com` / `Customer123!`
- Support Staff: `support@example.com` / `Support123!`
- Administrator: `admin@example.com` / `Admin123!`

These demo accounts are seeded for local development and can be replaced with database-backed users once MySQL is running.

## Modules implemented

- User & Access Management
- Product & Order Management
- Return Management
- Complaint Management
- Refund Management
- Reports & Audit

## ADBMS features included

- MySQL schema with tables, constraints, indexes, and sample data
- Views for pending complaints and return summaries
- Stored procedures and user-defined functions
- Triggers for audit logging and status changes
- Transaction patterns for return approval and refund creation
- MySQL examples in `advanced_queries.sql`
- MongoDB complaint document storage and analytics index setup

Complaint messaging lifecycle: `Resolved` remains replyable; a customer reply moves it back to `In Progress`. `Closed` blocks ordinary replies. Customers can reopen a complaint with a reason within 7 days. After that, the customer can create a new complaint linked to the old one as a follow-up.

## Troubleshooting

- If MySQL credentials fail, confirm the service is running and the database exists.
- If MongoDB Atlas fails, verify the Atlas database user, IP access list, and `MONGO_URI`. `ECONNREFUSED 127.0.0.1:27017` means the command targeted a local MongoDB server; pass the Atlas URI to `mongosh` as shown above.
- If the app starts in demo mode, it means the database is unavailable; the application still exposes the screen flow and protects routes, but production-grade data access requires the live services.


logins:

Customer: customer@example.com / Customer123!
Support: support@example.com / Support123!
Admin: admin@example.com / Admin123!
Email	Password
nisha.demo@example.com	NishaDemo26!
arjun.demo@example.com	ArjunDemo26!
meera.demo@example.com	MeeraDemo26!
kabir.demo@example.com	KabirDemo26!
tara.demo@example.com	TaraDemo26!