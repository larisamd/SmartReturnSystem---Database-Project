DROP DATABASE IF EXISTS smart_return_system;
CREATE DATABASE smart_return_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_return_system;

CREATE TABLE Roles (
    RoleID INT NOT NULL AUTO_INCREMENT,
    RoleName VARCHAR(50) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (RoleID),
    UNIQUE KEY uq_roles_name (RoleName)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Users (
    UserID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(120) NOT NULL,
    Email VARCHAR(150) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    RoleID INT NOT NULL,
    Phone VARCHAR(30) DEFAULT NULL,
    City VARCHAR(80) DEFAULT NULL,
    Country VARCHAR(80) DEFAULT NULL,
    IsActive TINYINT(1) NOT NULL DEFAULT 1,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID),
    CONSTRAINT chk_users_email CHECK (Email LIKE '%@%'),
    CONSTRAINT fk_users_role FOREIGN KEY (RoleID) REFERENCES Roles(RoleID),
    UNIQUE KEY uq_users_email (Email),
    INDEX idx_users_role (RoleID),
    INDEX idx_users_active (IsActive)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Products (
    ProductID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(150) NOT NULL,
    Description TEXT NOT NULL,
    Category VARCHAR(80) NOT NULL,
    Price DECIMAL(10,2) NOT NULL CHECK (Price >= 0),
    Availability TINYINT(1) NOT NULL DEFAULT 1,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ProductID),
    INDEX idx_products_category (Category),
    INDEX idx_products_availability (Availability)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Orders (
    OrderID INT NOT NULL AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    OrderDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    OrderStatus VARCHAR(30) NOT NULL DEFAULT 'Pending',
    TotalAmount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (OrderID),
    CONSTRAINT chk_orders_status CHECK (OrderStatus IN ('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled')),
    CONSTRAINT fk_orders_customer FOREIGN KEY (CustomerID) REFERENCES Users(UserID),
    INDEX idx_orders_customer (CustomerID),
    INDEX idx_orders_status (OrderStatus)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE OrderItems (
    OrderItemID INT NOT NULL AUTO_INCREMENT,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    UnitPrice DECIMAL(10,2) NOT NULL CHECK (UnitPrice >= 0),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (OrderItemID),
    CONSTRAINT fk_orderitems_order FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    CONSTRAINT fk_orderitems_product FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    UNIQUE KEY uq_orderitems_order_product (OrderID, ProductID),
    INDEX idx_orderitems_order (OrderID),
    INDEX idx_orderitems_product (ProductID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ReturnRequests (
    ReturnID INT NOT NULL AUTO_INCREMENT,
    OrderItemID INT NOT NULL,
    CustomerID INT NOT NULL,
    Reason TEXT NOT NULL,
    Status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    ApprovedBy INT DEFAULT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ReturnID),
    CONSTRAINT chk_return_status CHECK (Status IN ('Pending', 'Approved', 'Rejected', 'Processing', 'Completed')),
    CONSTRAINT fk_return_orderitem FOREIGN KEY (OrderItemID) REFERENCES OrderItems(OrderItemID),
    CONSTRAINT fk_return_customer FOREIGN KEY (CustomerID) REFERENCES Users(UserID),
    CONSTRAINT fk_return_approver FOREIGN KEY (ApprovedBy) REFERENCES Users(UserID),
    UNIQUE KEY uq_active_return_order_item (OrderItemID, Status),
    INDEX idx_return_customer (CustomerID),
    INDEX idx_return_status (Status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Complaints (
    ComplaintID INT NOT NULL AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    ProductID INT NOT NULL,
    OrderItemID INT DEFAULT NULL,
    AssignedStaffID INT DEFAULT NULL,
    Category VARCHAR(80) NOT NULL,
    Status VARCHAR(30) NOT NULL DEFAULT 'Open',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ClosedAt DATETIME DEFAULT NULL,
    ParentComplaintID INT DEFAULT NULL,
    PRIMARY KEY (ComplaintID),
    CONSTRAINT chk_complaint_status CHECK (Status IN ('Open', 'In Progress', 'Resolved', 'Closed', 'Escalated')),
    CONSTRAINT fk_complaint_customer FOREIGN KEY (CustomerID) REFERENCES Users(UserID),
    CONSTRAINT fk_complaint_product FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    CONSTRAINT fk_complaint_orderitem FOREIGN KEY (OrderItemID) REFERENCES OrderItems(OrderItemID),
    CONSTRAINT fk_complaint_staff FOREIGN KEY (AssignedStaffID) REFERENCES Users(UserID),
    CONSTRAINT fk_complaint_parent FOREIGN KEY (ParentComplaintID) REFERENCES Complaints(ComplaintID),
    INDEX idx_complaint_customer (CustomerID),
    INDEX idx_complaint_product (ProductID),
    INDEX idx_complaint_status (Status),
    INDEX idx_complaint_staff (AssignedStaffID),
    INDEX idx_complaint_parent (ParentComplaintID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ComplaintResponses (
    ResponseID INT NOT NULL AUTO_INCREMENT,
    ComplaintID INT NOT NULL,
    AuthorUserID INT NOT NULL,
    Message TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ResponseID),
    CONSTRAINT fk_response_complaint FOREIGN KEY (ComplaintID) REFERENCES Complaints(ComplaintID),
    CONSTRAINT fk_response_author FOREIGN KEY (AuthorUserID) REFERENCES Users(UserID),
    INDEX idx_response_complaint (ComplaintID),
    INDEX idx_response_author (AuthorUserID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Refunds (
    RefundID INT NOT NULL AUTO_INCREMENT,
    ReturnID INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL CHECK (Amount >= 0),
    Status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (RefundID),
    CONSTRAINT chk_refund_status CHECK (Status IN ('Pending', 'Processing', 'Processed', 'Failed', 'Rejected')),
    CONSTRAINT fk_refund_return FOREIGN KEY (ReturnID) REFERENCES ReturnRequests(ReturnID),
    UNIQUE KEY uq_refunds_return (ReturnID),
    INDEX idx_refund_status (Status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE AuditLogs (
    LogID INT NOT NULL AUTO_INCREMENT,
    ActorUserID INT DEFAULT NULL,
    Action VARCHAR(80) NOT NULL,
    EntityType VARCHAR(60) NOT NULL,
    EntityID INT NOT NULL,
    Details TEXT DEFAULT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (LogID),
    CONSTRAINT fk_audit_actor FOREIGN KEY (ActorUserID) REFERENCES Users(UserID),
    INDEX idx_audit_entity (EntityType, EntityID),
    INDEX idx_audit_actor (ActorUserID),
    INDEX idx_audit_time (CreatedAt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO Roles (RoleName) VALUES
('Customer'),
('Support Staff'),
('Administrator');

INSERT INTO Users (Name, Email, PasswordHash, RoleID, Phone, City, Country, IsActive) VALUES
('Aisha Rahman', 'customer@example.com', 'Customer123!', 1, '9876543210', 'Bengaluru', 'India', 1),
('Daniel Smith', 'support@example.com', 'Support123!', 2, '9123456789', 'Hyderabad', 'India', 1),
('Priya Nair', 'admin@example.com', 'Admin123!', 3, '9765432109', 'Chennai', 'India', 1),
('Rahul Verma', 'rahul.customer@example.com', 'Customer123!', 1, '9988776655', 'Pune', 'India', 1),
('Sara Khan', 'sara.staff@example.com', 'Support123!', 2, '9123987654', 'Mumbai', 'India', 1);

INSERT INTO Products (Name, Description, Category, Price, Availability) VALUES
('Aurora Smartwatch', 'Connected wearable with advanced fitness analytics.', 'Electronics', 149.99, 1),
('Nimbus Bluetooth Speaker', 'Portable speaker with deep bass and 18-hour battery life.', 'Audio', 89.50, 1),
('Terra Yoga Mat', 'Eco-friendly non-slip mat for daily workouts.', 'Fitness', 34.00, 0),
('Quill Mechanical Keyboard', 'Silent mechanical keyboard designed for productivity.', 'Accessories', 119.00, 1),
('Horizon Noise Cancelling Headphones', 'Travel-friendly headphones with premium audio tuning.', 'Audio', 249.99, 1);

INSERT INTO Orders (CustomerID, OrderDate, OrderStatus, TotalAmount) VALUES
(1, '2026-06-18 10:00:00', 'Delivered', 149.99),
(1, '2026-08-20 13:15:00', 'Shipped', 89.50),
(4, '2026-09-01 15:30:00', 'Delivered', 249.99),
(4, '2026-09-10 11:00:00', 'Confirmed', 119.00);

INSERT INTO OrderItems (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 1, 149.99),
(2, 2, 1, 89.50),
(3, 5, 1, 249.99),
(4, 4, 1, 119.00);

INSERT INTO ReturnRequests (OrderItemID, CustomerID, Reason, Status, ApprovedBy) VALUES
(1, 1, 'Defective display', 'Pending', NULL),
(2, 1, 'Audio issue', 'Approved', 2),
(3, 4, 'Packaging damage', 'Rejected', 2);

INSERT INTO Complaints (CustomerID, ProductID, OrderItemID, AssignedStaffID, Category, Status) VALUES
(1, 1, 1, 2, 'Product Quality', 'Open'),
(1, 2, 2, 2, 'Shipping Delay', 'In Progress'),
(4, 5, 3, 5, 'Delivery Issue', 'Resolved');

INSERT INTO ComplaintResponses (ComplaintID, AuthorUserID, Message) VALUES
(1, 2, 'We are reviewing the smartwatch display issue and will confirm a replacement option.'),
(2, 1, 'The product arrived late and the delivery status is still unclear.'),
(3, 5, 'The replacement was processed and the complaint has been resolved.');

INSERT INTO Refunds (ReturnID, Amount, Status) VALUES
(2, 89.50, 'Processed');

INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details) VALUES
(1, 'Created Return Request', 'ReturnRequests', 1, 'Customer filed a defect complaint for order item 1.'),
(2, 'Approved Return', 'ReturnRequests', 2, 'Support staff approved the return and created a refund request.'),
(5, 'Resolved Complaint', 'Complaints', 3, 'Complaint closed after customer confirmation.');

CREATE VIEW pending_complaints_vw AS
SELECT c.ComplaintID, c.CustomerID, u.Name AS CustomerName, c.Category, c.Status, c.CreatedAt
FROM Complaints c
JOIN Users u ON u.UserID = c.CustomerID
WHERE c.Status IN ('Open', 'In Progress')
ORDER BY c.CreatedAt DESC;

CREATE VIEW return_summary_vw AS
SELECT rr.ReturnID,
       rr.CustomerID,
       u.Name AS CustomerName,
       rr.OrderItemID,
       rr.Status,
       rr.CreatedAt,
       COALESCE(rf.Amount, 0) AS RefundAmount
FROM ReturnRequests rr
LEFT JOIN Users u ON u.UserID = rr.CustomerID
LEFT JOIN Refunds rf ON rf.ReturnID = rr.ReturnID;

DELIMITER //
CREATE FUNCTION calculate_refund_amount(p_amount DECIMAL(10,2), p_percent DECIMAL(5,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    RETURN ROUND(p_amount * (p_percent / 100), 2);
END //

CREATE PROCEDURE create_return_request_proc(
    IN p_order_item_id INT,
    IN p_customer_id INT,
    IN p_reason TEXT,
    OUT p_return_id INT
)
BEGIN
    INSERT INTO ReturnRequests (OrderItemID, CustomerID, Reason, Status, CreatedAt, UpdatedAt)
    VALUES (p_order_item_id, p_customer_id, p_reason, 'Pending', NOW(), NOW());
    SET p_return_id = LAST_INSERT_ID();
END //

CREATE PROCEDURE approve_return_and_create_refund(
    IN p_return_id INT,
    IN p_staff_id INT,
    IN p_amount DECIMAL(10,2)
)
BEGIN
    DECLARE v_status VARCHAR(30);
    START TRANSACTION;
    SELECT Status INTO v_status FROM ReturnRequests WHERE ReturnID = p_return_id FOR UPDATE;
    IF v_status IS NULL THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Return request not found';
    ELSEIF v_status IN ('Approved', 'Completed') THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Return already processed';
    END IF;

    UPDATE ReturnRequests
    SET Status = 'Approved', ApprovedBy = p_staff_id, UpdatedAt = NOW()
    WHERE ReturnID = p_return_id;

    INSERT INTO Refunds (ReturnID, Amount, Status, CreatedAt, UpdatedAt)
    VALUES (p_return_id, p_amount, 'Processing', NOW(), NOW());

    INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details)
    VALUES (p_staff_id, 'Approved and Refunded', 'ReturnRequests', p_return_id, CONCAT('Refund created for return ID ', p_return_id));

    COMMIT;
END //

CREATE PROCEDURE assign_complaint_to_staff(
    IN p_complaint_id INT,
    IN p_staff_id INT
)
BEGIN
    UPDATE Complaints
    SET AssignedStaffID = p_staff_id,
        Status = 'In Progress',
        UpdatedAt = NOW()
    WHERE ComplaintID = p_complaint_id;

    INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details)
    VALUES (p_staff_id, 'Assigned complaint', 'Complaints', p_complaint_id, CONCAT('Complaint assigned to staff ID ', p_staff_id));
END //

CREATE TRIGGER trg_return_audit AFTER UPDATE ON ReturnRequests
FOR EACH ROW
BEGIN
    IF OLD.Status <> NEW.Status THEN
        INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details)
        VALUES (NEW.ApprovedBy, CONCAT('Return status changed to ', NEW.Status), 'ReturnRequests', NEW.ReturnID, CONCAT('Status updated from ', OLD.Status, ' to ', NEW.Status));
    END IF;
END //

CREATE TRIGGER trg_refund_audit AFTER UPDATE ON Refunds
FOR EACH ROW
BEGIN
    IF OLD.Status <> NEW.Status THEN
        INSERT INTO AuditLogs (ActorUserID, Action, EntityType, EntityID, Details)
        VALUES (NULL, CONCAT('Refund status changed to ', NEW.Status), 'Refunds', NEW.RefundID, CONCAT('Refund status updated from ', OLD.Status, ' to ', NEW.Status));
    END IF;
END //
DELIMITER ;

CREATE INDEX idx_returnrequest_reason ON ReturnRequests (Reason(64));
CREATE INDEX idx_complaint_category_status ON Complaints (Category, Status);
CREATE INDEX idx_orders_customer_date ON Orders (CustomerID, OrderDate);
CREATE INDEX idx_products_category_price ON Products (Category, Price);
CREATE INDEX idx_users_email_role ON Users (Email, RoleID);

SELECT 'Smart Return System schema initialized successfully.' AS Status;
