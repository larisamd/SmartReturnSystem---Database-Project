from app import create_app
import db
import routes


def test_login_page_loads():
    app = create_app()
    client = app.test_client()
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Smart Return System' in response.data


def test_dashboard_requires_login():
    app = create_app()
    client = app.test_client()
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')


def test_customer_login_redirects_to_dashboard():
    app = create_app()
    client = app.test_client()
    response = client.post(
        '/login',
        data={'email': 'customer@example.com', 'password': 'Customer123!'},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert '/dashboard' in response.headers.get('Location', '')


def test_demo_customers_have_delivered_items_for_returns(monkeypatch):
    demo_accounts = [
        ('nisha.demo@example.com', 'NishaDemo26!', 6),
        ('arjun.demo@example.com', 'ArjunDemo26!', 7),
        ('meera.demo@example.com', 'MeeraDemo26!', 8),
        ('kabir.demo@example.com', 'KabirDemo26!', 9),
        ('tara.demo@example.com', 'TaraDemo26!', 10),
    ]
    monkeypatch.setattr(db, 'get_mysql_connection', lambda: None)
    monkeypatch.setattr(db, 'DEMO_RETURN_REQUESTS', list(db.DEMO_RETURN_REQUESTS))

    client = create_app().test_client()
    for email, password, customer_id in demo_accounts:
        response = client.post('/login', data={'email': email, 'password': password})
        assert response.status_code == 302
        with client.session_transaction() as session:
            assert session['user_id'] == customer_id

        orders = db.get_orders_for_customer(customer_id)
        assert len(orders) == 1
        assert orders[0]['status'] == 'Delivered'
        item_ids = [int(item_id.strip()) for item_id in orders[0]['item_ids'].split(',')]
        assert len(item_ids) == 3

        result = db.create_return_request(customer_id, item_ids[0], 'Demo return')
        assert result['success'] is True
        assert db.get_demo_returns_for_customer(customer_id)[-1]['order_item_id'] == item_ids[0]

    result = db.create_return_request(6, 8, 'Wrong customer')
    assert result['success'] is False
    assert result['message'] == 'That order item does not belong to your account.'


def test_demo_login_uses_database_user_id_when_available(monkeypatch):
    class Cursor:
        def execute(self, query, params):
            pass

        def fetchone(self):
            return {
                'id': 42,
                'name': 'Nisha Demo',
                'email': 'nisha.demo@example.com',
                'password_hash': 'NishaDemo26!',
                'role': 'Customer',
            }

    class Connection:
        closed = False

        def cursor(self, dictionary=False):
            return Cursor()

        def close(self):
            self.closed = True

    connection = Connection()
    monkeypatch.setattr(db, 'get_mysql_connection', lambda: connection)

    user = db.authenticate_user('nisha.demo@example.com', 'NishaDemo26!')

    assert user['id'] == 42
    assert connection.closed


def test_products_page_is_protected():
    app = create_app()
    client = app.test_client()
    response = client.get('/products', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')


def test_orders_page_renders_total(monkeypatch):
    monkeypatch.setattr(
        routes,
        'get_orders_for_customer',
        lambda customer_id: [{
            'id': 5001,
            'order_date': '2026-06-18',
            'status': 'Delivered',
            'total': 149.99,
        }],
    )
    client = create_app().test_client()
    client.post('/login', data={
        'email': 'customer@example.com',
        'password': 'Customer123!',
    })

    response = client.get('/orders')

    assert response.status_code == 200
    assert b'$149.99' in response.data


def test_duplicate_return_shows_validation_message(monkeypatch):
    monkeypatch.setattr(db, 'get_mysql_connection', lambda: None)
    client = create_app().test_client()
    client.post('/login', data={
        'email': 'customer@example.com',
        'password': 'Customer123!',
    })

    response = client.post(
        '/returns',
        data={'order_item_id': '1', 'reason': 'Defective display'},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'A return request already exists for this order item.' in response.data


def test_complaint_form_uses_catalog_product_ids(monkeypatch):
    monkeypatch.setattr(routes, 'get_products', lambda: [{
        'id': 3,
        'name': 'Catalog Product',
        'availability': True,
    }])
    client = create_app().test_client()
    client.post('/login', data={
        'email': 'customer@example.com',
        'password': 'Customer123!',
    })

    response = client.get('/complaints')

    assert response.status_code == 200
    assert b'value="3">Catalog Product (ID 3)</option>' in response.data
    assert b'value="101"' not in response.data


def test_unknown_demo_product_is_rejected(monkeypatch):
    monkeypatch.setattr(db, 'get_mysql_connection', lambda: None)

    result = db.create_complaint(1, 999999, 'Product Quality', 'Defective item', '')

    assert result['success'] is False
    assert result['message'] == 'Select a product from the catalog.'


def test_admin_can_view_complaints_and_assignment_controls(monkeypatch):
    monkeypatch.setattr(routes, 'get_complaints_for_admin', lambda: [{
        'id': 44,
        'customer_id': 1,
        'customer_name': 'Aisha Rahman',
        'product_id': 1,
        'product_name': 'Aurora Smartwatch',
        'category': 'Product Quality',
        'status': 'Open',
        'created_at': '2026-10-01',
        'description': 'Display flickers',
        'assigned_staff_id': None,
    }])
    monkeypatch.setattr(routes, 'get_complaint_responses', lambda ids: {})
    monkeypatch.setattr(routes, 'get_support_staff', lambda: [{'id': 2, 'name': 'Daniel Smith'}])
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=3, user_name='Priya Nair', user_role='Administrator')

    response = client.get('/complaints')

    assert response.status_code == 200
    assert b'Display flickers' in response.data
    assert b'Assign' in response.data
    assert b'Update' in response.data


def test_complaint_response_supports_ajax_submission(monkeypatch):
    monkeypatch.setattr(routes, 'add_complaint_response', lambda *args: {
        'success': True,
        'message': 'Response sent.',
    })
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=2, user_name='Daniel Smith', user_role='Support Staff')

    response = client.post(
        '/complaints/44/responses',
        data={'message': 'We are checking this.'},
        headers={'Accept': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json == {
        'success': True,
        'message': 'Response sent.',
        'author_name': 'Daniel Smith',
        'author_role': 'Support Staff',
    }


def test_support_sees_pending_returns_with_decision_actions(monkeypatch):
    monkeypatch.setattr(routes, 'get_returns_for_staff', lambda: [{
        'id': 81,
        'customer_id': 1,
        'customer_name': 'Aisha Rahman',
        'order_item_id': 5,
        'order_id': 12,
        'product_name': 'Nimbus Speaker',
        'reason': 'No sound output',
        'status': 'Pending',
        'created_at': '2026-10-02',
        'amount': 89.5,
    }])
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=2, user_name='Daniel Smith', user_role='Support Staff')

    response = client.get('/returns')

    assert response.status_code == 200
    assert b'No sound output' in response.data
    assert b'Approve & Refund' in response.data
    assert b'Reject' in response.data


def test_customer_cannot_decide_return(monkeypatch):
    decision_called = []
    monkeypatch.setattr(routes, 'decide_return', lambda *args: decision_called.append(args))
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=1, user_name='Aisha Rahman', user_role='Customer')

    response = client.post('/returns/81/decision', data={'decision': 'Approved'})

    assert response.status_code == 302
    assert not decision_called


def test_customer_reply_to_resolved_complaint_reopens_it(monkeypatch):
    complaint = {
        'id': 91,
        'customer_id': 1,
        'assigned_staff_id': 2,
        'status': 'Resolved',
    }
    monkeypatch.setattr(db, 'get_mysql_connection', lambda: None)
    monkeypatch.setattr(db, 'DEMO_COMPLAINTS', [complaint])

    result = db.add_complaint_response(91, 1, 'Customer', 'The issue is still happening.')

    assert result['success'] is True
    assert 'reopened' in result['message'].lower()
    assert complaint['status'] == 'In Progress'


def test_closed_complaint_rejects_normal_customer_reply(monkeypatch):
    monkeypatch.setattr(db, 'get_mysql_connection', lambda: None)
    monkeypatch.setattr(db, 'DEMO_COMPLAINTS', [{
        'id': 92,
        'customer_id': 1,
        'assigned_staff_id': 2,
        'status': 'Closed',
    }])

    result = db.add_complaint_response(92, 1, 'Customer', 'I need to reopen this.')

    assert result['success'] is False
    assert 'closed' in result['message'].lower()


def test_closed_customer_complaint_shows_explicit_reopen_control(monkeypatch):
    monkeypatch.setattr(routes, 'get_complaints_for_customer', lambda customer_id: [{
        'id': 93,
        'customer_id': customer_id,
        'product_id': 1,
        'product_name': 'Sample Product',
        'category': 'Product Quality',
        'status': 'Closed',
        'created_at': '2026-10-10',
        'closed_at': '2026-10-12',
        'can_reopen': True,
        'description': 'The issue was marked closed.',
    }])
    monkeypatch.setattr(routes, 'get_complaint_responses', lambda ids: {})
    monkeypatch.setattr(routes, 'get_products', lambda: [])
    monkeypatch.setattr(routes, 'get_closed_followup_candidates', lambda customer_id: [])
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=1, user_name='Customer', user_role='Customer')

    response = client.get('/complaints')

    assert response.status_code == 200
    assert b'name="reason"' in response.data
    assert b'>Reopen</button>' in response.data
    assert b'name="message"' not in response.data
    assert b'class="response-form ajax-response-form"' not in response.data


def test_resolved_customer_complaint_keeps_reply_control(monkeypatch):
    monkeypatch.setattr(routes, 'get_complaints_for_customer', lambda customer_id: [{
        'id': 94,
        'customer_id': customer_id,
        'product_id': 1,
        'product_name': 'Sample Product',
        'category': 'Product Quality',
        'status': 'Resolved',
        'created_at': '2026-10-10',
        'description': 'Agent proposed a solution.',
    }])
    monkeypatch.setattr(routes, 'get_complaint_responses', lambda ids: {})
    monkeypatch.setattr(routes, 'get_products', lambda: [])
    monkeypatch.setattr(routes, 'get_closed_followup_candidates', lambda customer_id: [])
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=1, user_name='Customer', user_role='Customer')

    response = client.get('/complaints')

    assert response.status_code == 200
    assert b'Reply to reopen this resolved complaint' in response.data
    assert b'name="message"' in response.data
    assert b'class="response-form ajax-response-form"' in response.data


def test_closed_complaint_reopen_requires_customer_reason(monkeypatch):
    reopen_call = []
    monkeypatch.setattr(routes, 'reopen_complaint', lambda *args: reopen_call.append(args) or {
        'success': True,
        'message': 'Complaint reopened and returned to In Progress.',
    })
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=6, user_name='Nisha Demo', user_role='Customer')

    response = client.post(
        '/complaints/93/reopen',
        data={'reason': 'The same fault came back.'},
    )

    assert response.status_code == 302
    assert reopen_call == [(93, 6, 'The same fault came back.')]


def test_old_closed_complaint_offers_linked_followup(monkeypatch):
    monkeypatch.setattr(routes, 'get_complaints_for_customer', lambda customer_id: [])
    monkeypatch.setattr(routes, 'get_complaint_responses', lambda ids: {})
    monkeypatch.setattr(routes, 'get_products', lambda: [{'id': 4, 'name': 'Desk Lamp'}])
    monkeypatch.setattr(routes, 'get_closed_followup_candidates', lambda customer_id: [{
        'id': 95,
        'category': 'Product Quality',
        'product_id': 4,
        'product_name': 'Desk Lamp',
        'closed_at': '2026-10-01',
    }])
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=6, user_name='Nisha Demo', user_role='Customer')

    response = client.get('/complaints')

    assert response.status_code == 200
    assert b'Follow-up to an older closed complaint' in response.data
    assert b'Desk Lamp / Product Quality' in response.data


def test_followup_submission_passes_parent_complaint_id(monkeypatch):
    create_call = []
    monkeypatch.setattr(routes, 'create_complaint', lambda *args: create_call.append(args) or {
        'success': True,
        'message': 'Complaint submitted.',
    })
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=6, user_name='Nisha Demo', user_role='Customer')

    response = client.post('/complaints', data={
        'product_id': '4',
        'category': 'Product Quality',
        'description': 'The same lamp fault returned.',
        'evidence': '',
        'parent_complaint_id': '95',
    })

    assert response.status_code == 302
    assert create_call == [(6, 4, 'Product Quality', 'The same lamp fault returned.', '', 95)]


def test_staff_complaint_csv_uses_assigned_queue_and_safe_cells(monkeypatch):
    monkeypatch.setattr(routes, 'get_complaints_for_staff', lambda staff_id: [{
        'id': 44,
        'customer_name': '=HYPERLINK("bad")',
        'customer_id': 1,
        'product_name': 'Lamp',
        'category': 'Quality',
        'status': 'Open',
        'assigned_staff_id': staff_id,
        'description': 'Flickers',
        'evidence': {},
    }])
    monkeypatch.setattr(routes, 'get_complaint_responses', lambda ids: {})
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=2, user_name='Daniel Smith', user_role='Support Staff')

    response = client.get('/exports/complaints.csv')

    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert 'attachment; filename="complaint-queue.csv"' in response.headers['Content-Disposition']
    assert b'Complaint ID' in response.data
    assert b"'=HYPERLINK" in response.data


def test_admin_returns_csv_exports_admin_queue(monkeypatch):
    monkeypatch.setattr(routes, 'get_returns_for_admin', lambda: [{
        'id': 81,
        'customer_name': 'Aisha Rahman',
        'customer_id': 1,
        'order_id': 12,
        'order_item_id': 5,
        'product_name': 'Speaker',
        'reason': 'Audio issue',
        'status': 'Pending',
        'amount': 89.5,
        'refund_status': '',
        'created_at': '2026-10-02',
    }])
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=3, user_name='Priya Nair', user_role='Administrator')

    response = client.get('/exports/returns.csv')

    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert 'return-queue.csv' in response.headers['Content-Disposition']
    assert b'Audio issue' in response.data
    assert b'89.5' in response.data


def test_customer_cannot_download_staff_exports():
    client = create_app().test_client()
    with client.session_transaction() as session:
        session.update(user_id=1, user_name='Aisha Rahman', user_role='Customer')

    response = client.get('/exports/complaints.csv', follow_redirects=False)

    assert response.status_code == 302
