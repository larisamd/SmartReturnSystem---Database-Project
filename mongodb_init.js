const database = db.getSiblingDB('smart_return_system');

const complaintDetails = database.getCollection('complaint_details');
const activityLogs = database.getCollection('activity_logs');

complaintDetails.createIndex({ complaint_id: 1 }, { unique: true });
complaintDetails.createIndex({ tags: 1 });
complaintDetails.createIndex({ product_condition: 1 });
complaintDetails.createIndex({ created_at: -1 });

activityLogs.createIndex({ complaint_id: 1, timestamp: -1 });
activityLogs.createIndex({ event_type: 1, actor_id: 1 });

complaintDetails.insertMany([
  {
    complaint_id: 1,
    detailed_description: 'The display flickers and turns blue after charging for 30 minutes.',
    evidence_metadata: {
      attachment_type: 'image',
      url: 'https://example.com/evidence/display-flicker.jpg',
      uploaded_at: new Date()
    },
    product_condition: 'Defective',
    tags: ['display', 'defect', 'smartwatch'],
    extra_details: {
      issue_count: 2,
      warranty_status: 'active'
    },
    created_at: new Date()
  },
  {
    complaint_id: 2,
    detailed_description: 'The speaker volume drops during sync after 10 minutes of use.',
    evidence_metadata: {
      attachment_type: 'audio',
      url: 'https://example.com/evidence/speaker-audio.wav',
      uploaded_at: new Date()
    },
    product_condition: 'Damaged',
    tags: ['speaker', 'shipping', 'audio'],
    extra_details: {
      packaging: 'box damaged'
    },
    created_at: new Date()
  }
]);

activityLogs.insertMany([
  {
    complaint_id: 1,
    event_type: 'submitted',
    actor_id: 1,
    event_details: 'Customer submitted a complaint with evidence.',
    timestamp: new Date()
  },
  {
    complaint_id: 1,
    event_type: 'assigned',
    actor_id: 2,
    event_details: 'Complaint assigned to support staff.',
    timestamp: new Date()
  },
  {
    complaint_id: 2,
    event_type: 'status_update',
    actor_id: 2,
    event_details: 'Complaint moved to in progress.',
    timestamp: new Date()
  }
]);

print('MongoDB complaint and activity collections initialized.');
