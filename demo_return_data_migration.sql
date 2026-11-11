USE smart_return_system;

START TRANSACTION;

INSERT INTO Users (Name, Email, PasswordHash, RoleID, IsActive)
SELECT demo.name, demo.email, demo.password_hash, customer_role.RoleID, 1
FROM (
    SELECT 'Nisha Demo' AS name, 'nisha.demo@example.com' AS email,
           'scrypt:32768:8:1$RB1xxNX2y7hAO2rW$3ea25c7de8f1ed265668c705b1f13513c31fe1f8d4b5622934104e3f9bcd8d8d05c6d55a73459da4b3d83ea7383ed85a13f29abb0fca655b08716f26583c7ae5' AS password_hash
    UNION ALL SELECT 'Arjun Demo', 'arjun.demo@example.com',
           'scrypt:32768:8:1$DeiHrXxZFpV3OHS1$b44f3e6f1c57559b8fea81b59b22dce49d1a3b03cdb385175d6468c2ff06a9a761d91e70920c87d59bcd6159aefa090f81c39b694e4fa664d10b5738815d1876'
    UNION ALL SELECT 'Meera Demo', 'meera.demo@example.com',
           'scrypt:32768:8:1$EEFCW95hxRTcOP2g$0a62dc15a54b5d2a04ab86842ee22d229fdd0b147db3f424814fc2bc2cd3bb428d1831f1a8186338db615443cb907c5d81f2a18494be302c2714bb590a8d3d09'
    UNION ALL SELECT 'Kabir Demo', 'kabir.demo@example.com',
           'scrypt:32768:8:1$UNRB3jrmnYYDDfgr$46b7b4c4ba75e4c075fc17091bcdec30f48f4ea214af4d6ade12ef471d5c071094774a63a418cb11b74a82ae0e393d423f9333a54dcc4e0a807bf9faedea6810'
    UNION ALL SELECT 'Tara Demo', 'tara.demo@example.com',
           'scrypt:32768:8:1$FfhVMigXCjfgCwoS$58aa243f2e23869fa3d4f1f418507fdb137174701a49a44e481b6be29d9053ff84dc7f83514e0872cd49bd0d52a13ce49e74cc83f1d0f16ce487ab456d812788'
) AS demo
JOIN Roles AS customer_role ON customer_role.RoleName = 'Customer'
WHERE NOT EXISTS (
    SELECT 1 FROM Users AS existing_user WHERE existing_user.Email = demo.email
);

INSERT INTO Orders (CustomerID, OrderDate, OrderStatus, TotalAmount)
SELECT u.UserID, demo.order_date, 'Delivered', 358.49
FROM (
    SELECT 'nisha.demo@example.com' AS email, '2026-10-15 10:00:00' AS order_date
    UNION ALL SELECT 'arjun.demo@example.com', '2026-10-16 10:00:00'
    UNION ALL SELECT 'meera.demo@example.com', '2026-10-17 10:00:00'
    UNION ALL SELECT 'kabir.demo@example.com', '2026-10-18 10:00:00'
    UNION ALL SELECT 'tara.demo@example.com', '2026-10-19 10:00:00'
) AS demo
JOIN Users AS u ON u.Email = demo.email
WHERE NOT EXISTS (
    SELECT 1
    FROM Orders AS existing_order
    WHERE existing_order.CustomerID = u.UserID
      AND existing_order.OrderDate = demo.order_date
);

INSERT INTO OrderItems (OrderID, ProductID, Quantity, UnitPrice)
SELECT o.OrderID, p.ProductID, 1, p.Price
FROM (
    SELECT 'nisha.demo@example.com' AS email, '2026-10-15 10:00:00' AS order_date, 'Aurora Smartwatch' AS product_name
    UNION ALL SELECT 'nisha.demo@example.com', '2026-10-15 10:00:00', 'Nimbus Bluetooth Speaker'
    UNION ALL SELECT 'nisha.demo@example.com', '2026-10-15 10:00:00', 'Quill Mechanical Keyboard'
    UNION ALL SELECT 'arjun.demo@example.com', '2026-10-16 10:00:00', 'Aurora Smartwatch'
    UNION ALL SELECT 'arjun.demo@example.com', '2026-10-16 10:00:00', 'Nimbus Bluetooth Speaker'
    UNION ALL SELECT 'arjun.demo@example.com', '2026-10-16 10:00:00', 'Quill Mechanical Keyboard'
    UNION ALL SELECT 'meera.demo@example.com', '2026-10-17 10:00:00', 'Aurora Smartwatch'
    UNION ALL SELECT 'meera.demo@example.com', '2026-10-17 10:00:00', 'Nimbus Bluetooth Speaker'
    UNION ALL SELECT 'meera.demo@example.com', '2026-10-17 10:00:00', 'Quill Mechanical Keyboard'
    UNION ALL SELECT 'kabir.demo@example.com', '2026-10-18 10:00:00', 'Aurora Smartwatch'
    UNION ALL SELECT 'kabir.demo@example.com', '2026-10-18 10:00:00', 'Nimbus Bluetooth Speaker'
    UNION ALL SELECT 'kabir.demo@example.com', '2026-10-18 10:00:00', 'Quill Mechanical Keyboard'
    UNION ALL SELECT 'tara.demo@example.com', '2026-10-19 10:00:00', 'Aurora Smartwatch'
    UNION ALL SELECT 'tara.demo@example.com', '2026-10-19 10:00:00', 'Nimbus Bluetooth Speaker'
    UNION ALL SELECT 'tara.demo@example.com', '2026-10-19 10:00:00', 'Quill Mechanical Keyboard'
) AS demo
JOIN Users AS u ON u.Email = demo.email
JOIN Orders AS o ON o.CustomerID = u.UserID AND o.OrderDate = demo.order_date
JOIN Products AS p ON p.Name = demo.product_name
WHERE NOT EXISTS (
    SELECT 1
    FROM OrderItems AS existing_item
    WHERE existing_item.OrderID = o.OrderID
      AND existing_item.ProductID = p.ProductID
);

COMMIT;
