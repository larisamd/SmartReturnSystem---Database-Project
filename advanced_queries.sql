-- Advanced ADBMS demonstration queries for the Smart Return System
-- Run after importing schema.sql into MySQL.

-- 1) INNER JOIN: customer orders with order item details
SELECT o.OrderID, u.Name AS customer_name, p.Name AS product_name, oi.Quantity, oi.UnitPrice
FROM Orders o
INNER JOIN Users u ON u.UserID = o.CustomerID
INNER JOIN OrderItems oi ON oi.OrderID = o.OrderID
INNER JOIN Products p ON p.ProductID = oi.ProductID
WHERE o.OrderStatus IN ('Delivered', 'Shipped');

-- 2) LEFT JOIN: all returns, including those without refund records
SELECT rr.ReturnID, rr.CustomerID, u.Name, rr.Status, rf.Amount AS refund_amount
FROM ReturnRequests rr
LEFT JOIN Users u ON u.UserID = rr.CustomerID
LEFT JOIN Refunds rf ON rf.ReturnID = rr.ReturnID;

-- 3) RIGHT JOIN: all users and their assigned complaint records
SELECT u.UserID, u.Name, c.ComplaintID, c.Category
FROM Complaints c
RIGHT JOIN Users u ON u.UserID = c.AssignedStaffID;

-- 4) Correlated subquery: complaints with product value above customer average spend
SELECT c.ComplaintID, c.CustomerID, c.ProductID,
       (SELECT AVG(oi.UnitPrice * oi.Quantity)
        FROM OrderItems oi
        JOIN Orders o ON o.OrderID = oi.OrderID
        WHERE o.CustomerID = c.CustomerID) AS customer_avg_order_value
FROM Complaints c
WHERE c.ProductID IN (
    SELECT ProductID
    FROM Products
    WHERE Price > 100
);

-- 5) Nested subquery: complaints for customers with more than one return
SELECT *
FROM Complaints c
WHERE c.CustomerID IN (
    SELECT CustomerID
    FROM ReturnRequests rr
    GROUP BY CustomerID
    HAVING COUNT(*) > 1
);

-- 6) Aggregate queries with GROUP BY and HAVING
SELECT p.Category,
       COUNT(*) AS product_count,
       ROUND(AVG(p.Price), 2) AS avg_product_price,
       MAX(p.Price) AS max_price
FROM Products p
GROUP BY p.Category
HAVING AVG(p.Price) > 75;

SELECT rr.Status, COUNT(*) AS return_count
FROM ReturnRequests rr
GROUP BY rr.Status
HAVING COUNT(*) >= 1;

-- 7) View example
SELECT * FROM pending_complaints_vw;
SELECT * FROM return_summary_vw;

-- 8) Function example
SELECT calculate_refund_amount(150.00, 25) AS refund_amount;

-- 9) Procedure example
CALL create_return_request_proc(1, 1, 'Battery drains quickly', @new_return_id);
SELECT @new_return_id AS new_return_id;

CALL assign_complaint_to_staff(2, 2);

-- 10) Transaction pattern example
START TRANSACTION;
UPDATE ReturnRequests
SET Status = 'Approved', UpdatedAt = NOW()
WHERE ReturnID = 1;

INSERT INTO Refunds (ReturnID, Amount, Status)
VALUES (1, 50.00, 'Processing');

COMMIT;

-- 11) Sample rollback block
START TRANSACTION;
UPDATE Complaints
SET Status = 'Escalated'
WHERE ComplaintID = 2;

-- Use ROLLBACK if the process should be cancelled:
-- ROLLBACK;

-- 12) Query for pending customer support queue
SELECT c.ComplaintID, c.Category, c.Status, u.Name AS customer_name
FROM Complaints c
JOIN Users u ON u.UserID = c.CustomerID
WHERE c.Status IN ('Open', 'In Progress')
ORDER BY c.CreatedAt DESC;
