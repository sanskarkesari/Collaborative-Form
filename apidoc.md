Collaborative Form API Documentation
Introduction
The Collaborative Form API provides a backend for creating and managing forms, with real-time collaboration capabilities. The API is built with FastAPI and includes REST endpoints for form management and WebSocket support for real-time updates. This documentation covers all available endpoints and WebSocket events, enabling developers to integrate with the system.

Base URL: https://collaborative-form.up.railway.app (or http://localhost:8000 for local development)
Interactive Docs: Available at /docs (e.g., https://collaborative-form.up.railway.app/docs)

REST API Endpoints
1. Create a Form
Create a new form with specified fields.

Method: POST
Path: /api/forms
Request Body:{
  "name": "string",
  "fields": [
    {
      "type": "string", // "text", "number", or "dropdown"
      "label": "string",
      "options": ["string"], // Required for "dropdown" type, otherwise optional
      "order": integer,
      "required": boolean // Optional, defaults to false
    }
  ]
}


Response (200 OK):{
  "id": "uuid",
  "share_token": "uuid"
}


Example:curl -X POST https://collaborative-form.up.railway.app/api/forms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Team Survey",
    "fields": [
      {"type": "text", "label": "Team Name", "order": 1, "required": true},
      {"type": "number", "label": "Team Size", "order": 2, "required": false}
    ]
  }'

Response:{
  "id": "f1a2b3c4-d5e6-4f78-9123-456789abcdef",
  "share_token": "a1b2c3d4-e5f6-4g78-h123-456789abcdef"
}



2. Get Form Details
Retrieve a form’s details and current responses using its share_token.

Method: GET
Path: /api/forms/{share_token}
Parameters:
share_token (path): The unique share token of the form (UUID).


Response (200 OK):{
  "id": "uuid",
  "name": "string",
  "fields": [
    {
      "id": "uuid",
      "type": "string",
      "label": "string",
      "options": ["string"],
      "order": integer,
      "required": boolean
    }
  ],
  "response": {
    "field_id": "value" // Dynamic key-value pairs
  }
}


Example:curl https://collaborative-form.up.railway.app/api/forms/a1b2c3d4-e5f6-4g78-h123-456789abcdef

Response:{
  "id": "f1a2b3c4-d5e6-4f78-9123-456789abcdef",
  "name": "Team Survey",
  "fields": [
    {
      "id": "b2c3d4e5-f6g7-4h89-i123-567890abcdef",
      "type": "text",
      "label": "Team Name",
      "options": [],
      "order": 1,
      "required": true
    },
    {
      "id": "c3d4e5f6-g7h8-4i90-j123-678901abcdef",
      "type": "number",
      "label": "Team Size",
      "options": [],
      "order": 2,
      "required": false
    }
  ],
  "response": {
    "b2c3d4e5-f6g7-4h89-i123-567890abcdef": "Team Alpha"
  }
}



WebSocket Events
The application uses WebSockets for real-time collaboration. Connect to the WebSocket server at /socket.io with the share_token as a query parameter.

Connection URL: wss://collaborative-form.up.railway.app/socket.io?share_token=<share_token> (or ws://localhost:8000/socket.io locally)
Transport: WebSocket (falls back to polling if needed)

1. Join a Session
Join a form session to collaborate with other users.

Event: message
Payload:{
  "type": "join",
  "username": "string"
}


Response Event: message
Response Payload:{
  "type": "user_joined",
  "username": "string"
}


Example:
Send:{
  "type": "join",
  "username": "User1"
}


Receive (in all connected clients):{
  "type": "user_joined",
  "username": "User1"
}





2. Update a Field
Update a form field, broadcasting the change to all connected users.

Event: message
Payload:{
  "type": "update",
  "field_id": "uuid",
  "value": "any"
}


Response Event: message
Response Payload:{
  "type": "update",
  "field_id": "uuid",
  "value": "any",
  "updated_by": "string"
}


Example:
Send:{
  "type": "update",
  "field_id": "b2c3d4e5-f6g7-4h89-i123-567890abcdef",
  "value": "Team Alpha"
}


Receive (in all connected clients):{
  "type": "update",
  "field_id": "b2c3d4e5-f6g7-4h89-i123-567890abcdef",
  "value": "Team Alpha",
  "updated_by": "User1"
}





3. User Disconnect
Notified when a user leaves the session.

Event: message
Payload:{
  "type": "user_left",
  "username": "string"
}


Example:
Receive:{
  "type": "user_left",
  "username": "User1"
}





Authentication and Security

Authentication: Currently, the API does not require authentication. Access is controlled via unique share_tokens, which act as a basic access control mechanism.
Security Considerations:
The share_token should be kept confidential to prevent unauthorized access.
Input validation is enforced (e.g., numbers must be numeric), but additional sanitization may be needed for production use.
In a production environment, consider adding authentication (e.g., JWT) and rate limiting.



Example Workflow

Create a Form:Use POST /api/forms to create a form. Note the share_token from the response.
Retrieve Form Details:Use GET /api/forms/{share_token} to get the form’s fields and current responses. Note the field_ids.
Connect via WebSocket:Connect to the WebSocket server with the share_token (e.g., wss://collaborative-form.up.railway.app/socket.io?share_token=<share_token>).
Join the Session:Send a join message with a username.
Collaborate in Real-Time:Send update messages to modify fields, and receive updates from other users in real-time.
Verify Data:Use GET /api/forms/{share_token} to confirm that updates are persisted in the database.

This workflow demonstrates the full cycle of form creation, collaboration, and data persistence.

