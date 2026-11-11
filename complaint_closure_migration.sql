USE smart_return_system;

-- Run this once on an existing database; do not rerun schema.sql to apply it.
ALTER TABLE Complaints
    ADD COLUMN ClosedAt DATETIME DEFAULT NULL AFTER UpdatedAt,
    ADD COLUMN ParentComplaintID INT DEFAULT NULL AFTER ClosedAt,
    ADD CONSTRAINT fk_complaint_parent
        FOREIGN KEY (ParentComplaintID) REFERENCES Complaints(ComplaintID),
    ADD INDEX idx_complaint_parent (ParentComplaintID);

-- Preserve a useful closure timestamp for complaints closed before this migration.
UPDATE Complaints
SET ClosedAt = UpdatedAt
WHERE Status = 'Closed' AND ClosedAt IS NULL;
