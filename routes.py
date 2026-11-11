import csv
import io
import json

from flask import (
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from auth import login_required, role_required
from db import (
    add_complaint_response,
    assign_complaint,
    authenticate_user,
    create_complaint,
    create_return_request,
    decide_return,
    get_complaint_responses,
    get_complaints_for_admin,
    get_complaints_for_customer,
    get_complaints_for_staff,
    get_closed_followup_candidates,
    get_dashboard_summary,
    get_db_health,
    get_orders_for_customer,
    get_products,
    get_returns_for_admin,
    get_returns_for_customer,
    get_returns_for_staff,
    get_support_staff,
    get_users_for_admin,
    reopen_complaint,
    update_complaint_status,
)


def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user.get('id')
            session['user_name'] = user.get('name') or user.get('Name')
            session['user_email'] = user.get('email') or user.get('Email')
            session['user_role'] = user.get('role') or user.get('RoleName')
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@login_required
def dashboard():
    user_id = session['user_id']
    role = session['user_role']
    data = {
        'user_name': session.get('user_name', 'User'),
        'role': role,
        'summary': get_dashboard_summary(),
        'db_status': get_db_health(),
        'recent_returns': get_returns_for_customer(user_id)[:3] if role == 'Customer' else [],
        'recent_complaints': get_complaints_for_customer(user_id)[:3] if role == 'Customer' else get_complaints_for_staff(user_id)[:3] if role == 'Support Staff' else [],
    }
    return render_template('dashboard.html', **data)


@login_required
def products():
    items = get_products()
    return render_template('products.html', products=items)


@login_required
@role_required('Customer')
def orders():
    items = get_orders_for_customer(session['user_id'])
    return render_template('orders.html', orders=items)


@login_required
def returns():
    user_id = session['user_id']
    role = session['user_role']
    if request.method == 'POST':
        if role != 'Customer':
            flash('Only customers can submit return requests.', 'danger')
            return redirect(url_for('returns'))
        try:
            order_item_id = int(request.form.get('order_item_id', ''))
        except ValueError:
            flash('Enter a valid order item ID.', 'danger')
            return redirect(url_for('returns'))
        reason = request.form.get('reason', '').strip()
        result = create_return_request(user_id, order_item_id, reason)
        flash(result['message'], 'success' if result['success'] else 'danger')
        return redirect(url_for('returns'))

    if role == 'Customer':
        requests = get_returns_for_customer(user_id)
    elif role == 'Support Staff':
        requests = get_returns_for_staff()
    else:
        requests = get_returns_for_admin()
    return render_template('returns.html', returns=requests)


@login_required
def complaints():
    user_id = session['user_id']
    role = session['user_role']
    if request.method == 'POST':
        if role != 'Customer':
            flash('Only customers can file complaints.', 'danger')
            return redirect(url_for('complaints'))
        try:
            product_id = int(request.form.get('product_id', ''))
        except ValueError:
            flash('Select a valid product.', 'danger')
            return redirect(url_for('complaints'))
        category = request.form.get('category', 'General').strip()
        description = request.form.get('description', '').strip()
        evidence = request.form.get('evidence', '').strip()
        parent_value = request.form.get('parent_complaint_id', '').strip()
        try:
            parent_complaint_id = int(parent_value) if parent_value else None
        except ValueError:
            flash('Select a valid complaint to follow up.', 'danger')
            return redirect(url_for('complaints'))
        result = create_complaint(user_id, product_id, category, description, evidence, parent_complaint_id)
        flash(result['message'], 'success' if result['success'] else 'danger')
        return redirect(url_for('complaints'))

    if role == 'Customer':
        items = get_complaints_for_customer(user_id)
    elif role == 'Support Staff':
        items = get_complaints_for_staff(user_id)
    elif role == 'Administrator':
        items = get_complaints_for_admin()
    else:
        items = []
    products = get_products() if role == 'Customer' else []
    followup_candidates = get_closed_followup_candidates(user_id) if role == 'Customer' else []
    responses = get_complaint_responses([item['id'] for item in items])
    staff = get_support_staff() if role == 'Administrator' else []
    return render_template(
        'complaints.html', complaints=items, role=role, products=products,
        responses=responses, support_staff=staff, followup_candidates=followup_candidates,
    )


@login_required
@role_required('Support Staff', 'Administrator')
def complaint_status(complaint_id):
    status = request.form.get('status', '').strip()
    result = update_complaint_status(complaint_id, status, session['user_id'], session['user_role'])
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('complaints'))


@login_required
@role_required('Customer', 'Support Staff', 'Administrator')
def complaint_response(complaint_id):
    result = add_complaint_response(
        complaint_id, session['user_id'], session['user_role'],
        request.form.get('message', ''),
    )
    if request.accept_mimetypes.best == 'application/json':
        return jsonify(
            success=result['success'],
            message=result['message'],
            author_name=session['user_name'],
            author_role=session['user_role'],
        ), 200 if result['success'] else 400
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('complaints'))


@login_required
@role_required('Customer')
def complaint_reopen(complaint_id):
    result = reopen_complaint(
        complaint_id, session['user_id'], request.form.get('reason', ''),
    )
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('complaints'))


@login_required
@role_required('Administrator')
def complaint_assignment(complaint_id):
    try:
        staff_id = int(request.form.get('staff_id', ''))
    except ValueError:
        flash('Select a support staff member.', 'danger')
        return redirect(url_for('complaints'))
    result = assign_complaint(complaint_id, staff_id, session['user_id'])
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('complaints'))


@login_required
@role_required('Support Staff', 'Administrator')
def return_decision(return_id):
    decision = request.form.get('decision', '').strip()
    result = decide_return(return_id, decision, session['user_id'])
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('returns'))


@login_required
@role_required('Administrator')
def admin():
    users = get_users_for_admin()
    return render_template('admin.html', users=users, db_status=get_db_health(), summary=get_dashboard_summary())


@login_required
@role_required('Support Staff')
def support():
    return redirect(url_for('complaints'))


def _csv_response(filename, columns, rows):
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        safe_row = []
        for value in row:
            if value is None:
                safe_row.append('')
            elif isinstance(value, (int, float)):
                safe_row.append(value)
            else:
                text = str(value)
                if text.lstrip(' \t\r\n').startswith(('=', '+', '-', '@')):
                    text = "'" + text
                safe_row.append(text)
        writer.writerow(safe_row)

    return Response(
        '\ufeff' + output.getvalue(),
        content_type='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-store',
        },
    )


@login_required
@role_required('Support Staff', 'Administrator')
def export_complaints_csv():
    role = session['user_role']
    complaints = (
        get_complaints_for_admin()
        if role == 'Administrator'
        else get_complaints_for_staff(session['user_id'])
    )
    responses = get_complaint_responses([item['id'] for item in complaints])
    rows = []
    for item in complaints:
        messages = ' | '.join(reply['message'] for reply in responses.get(item['id'], []))
        evidence = item.get('evidence', {})
        rows.append((
            item.get('id'),
            item.get('customer_name'),
            item.get('customer_id'),
            item.get('product_name'),
            item.get('category'),
            item.get('status'),
            item.get('assigned_staff_name') or item.get('assigned_staff_id'),
            item.get('created_at'),
            item.get('closed_at'),
            item.get('parent_complaint_id'),
            item.get('description'),
            json.dumps(evidence, ensure_ascii=False, default=str) if evidence else '',
            messages,
        ))
    return _csv_response(
        'complaint-queue.csv',
        ('Complaint ID', 'Customer', 'Customer ID', 'Product', 'Category', 'Status',
         'Assigned Staff', 'Created At', 'Closed At', 'Follow-up To', 'Description',
         'Evidence Metadata', 'Responses'),
        rows,
    )


@login_required
@role_required('Support Staff', 'Administrator')
def export_returns_csv():
    role = session['user_role']
    returns = get_returns_for_admin() if role == 'Administrator' else get_returns_for_staff()
    rows = [(
        item.get('id'),
        item.get('customer_name'),
        item.get('customer_id'),
        item.get('order_id'),
        item.get('order_item_id'),
        item.get('product_name'),
        item.get('reason'),
        item.get('status'),
        item.get('amount'),
        item.get('refund_status'),
        item.get('created_at'),
    ) for item in returns]
    return _csv_response(
        'return-queue.csv',
        ('Return ID', 'Customer', 'Customer ID', 'Order ID', 'Order Item ID',
         'Product', 'Reason', 'Status', 'Refund Amount', 'Refund Status', 'Created At'),
        rows,
    )


def register_routes(app):
    app.add_url_rule('/', view_func=index, endpoint='index')
    app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'], endpoint='login')
    app.add_url_rule('/logout', view_func=logout, endpoint='logout')
    app.add_url_rule('/dashboard', view_func=dashboard, endpoint='dashboard')
    app.add_url_rule('/products', view_func=products, endpoint='products')
    app.add_url_rule('/orders', view_func=orders, endpoint='orders')
    app.add_url_rule('/returns', view_func=returns, methods=['GET', 'POST'], endpoint='returns')
    app.add_url_rule('/complaints', view_func=complaints, methods=['GET', 'POST'], endpoint='complaints')
    app.add_url_rule('/complaints/<int:complaint_id>/status', view_func=complaint_status, methods=['POST'], endpoint='complaint_status')
    app.add_url_rule('/complaints/<int:complaint_id>/responses', view_func=complaint_response, methods=['POST'], endpoint='complaint_response')
    app.add_url_rule('/complaints/<int:complaint_id>/reopen', view_func=complaint_reopen, methods=['POST'], endpoint='complaint_reopen')
    app.add_url_rule('/complaints/<int:complaint_id>/assign', view_func=complaint_assignment, methods=['POST'], endpoint='complaint_assignment')
    app.add_url_rule('/returns/<int:return_id>/decision', view_func=return_decision, methods=['POST'], endpoint='return_decision')
    app.add_url_rule('/exports/complaints.csv', view_func=export_complaints_csv, endpoint='export_complaints_csv')
    app.add_url_rule('/exports/returns.csv', view_func=export_returns_csv, endpoint='export_returns_csv')
    app.add_url_rule('/admin', view_func=admin, endpoint='admin')
    app.add_url_rule('/support', view_func=support, endpoint='support')
    app.jinja_env.globals['current_user_role'] = lambda: session.get('user_role', '')
    app.jinja_env.globals['current_user_name'] = lambda: session.get('user_name', '')
