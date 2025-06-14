Collaborative Form is a backend project that enables multiple users to fill out forms together in real-time, similar to Google Forms but with live updates. Built as a backend-focused project, it showcases my skills in Python, FastAPI, WebSockets, and PostgreSQL, demonstrating my ability to design scalable, real-time systems.

GitHub Repository: https://github.com/sanskarkesari/Collaborative-Form

Key Features

Dynamic Form Creation: Create forms with various field types (text, number, dropdown) via a REST API. 
Real-Time Collaboration: Users can join a form session and see updates instantly using WebSockets. 
Persistent Storage: Form responses are stored efficiently in PostgreSQL using the JSONB data type. 
Input Validation: Ensures data integrity by validating field inputs. 
Scalable Design: Built with FastAPI for production-ready performance.

Tech Stack

Backend: Python, FastAPI 
Real-Time Communication: WebSockets (via socketio) 
Database: PostgreSQL (with JSONB for flexible storage) 
Deployment: Docker Compose (local) 
Other Tools: databases library for async PostgreSQL queries, uvicorn for ASGI server

Set Up Environment:Create a .env file in the backend directory: DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/form_db

Run with Docker Compose: docker-compose up --build

This will start the FastAPI server on http://localhost:8000 and the PostgreSQL database.

Access the API:

Open http://localhost:8000/docs to interact with the API. Use POST /api/forms to create a form and GET /api/forms/{share_token} to retrieve form data.

Test WebSocket Functionality:

Use the provided HTML test client (or create your own) to connect to the WebSocket server using the share_token. Example HTML client setup is available in the repository’s docs folder.

API Documentation

API Documentation:See api_docs.md in the repository for detailed endpoint descriptions.

Example Usage

Create a Ex-form:
POST /api/forms { "name": "Team Survey", "fields": [ {"type": "text", "label": "Team Name", "order": 1, "required": true}, {"type": "number", "label": "Team Size", "order": 2, "required": false} ] }

Ex-Response:{ "id": "f1a2b3c4-d5e6-4f78-9123-456789abcdef", "share_token": "a1b2c3d4-e5f6-4g78-h123-456789abcdef" }

Join a session and update fields using a WebSocket client with the share_token.

Design Decisions and Edge Cases Design Decision: Flexible Data Storage I chose PostgreSQL’s JSONB data type to store form responses, allowing flexibility for dynamic fields without altering the database schema. This design enables the system to handle various field types (text, number, dropdown) and scale for future additions. In the update_response function, I ensured reliability by casting the form_id to UUID, resolving an issue where updates failed due to type mismatches. Edge Case: Input Validation An interesting edge case I handled was invalid user inputs. For example, if a user enters a non-numeric value (e.g., "abc") for a number field like "Team Size," the system validates the input and throws an error (Invalid number value). This ensures data integrity and prevents invalid data from being stored, enhancing the user experience.
