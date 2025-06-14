Collaborative Form: Real-Time Form-Filling Backend
Overview
Collaborative Form is a web application that enables multiple users to fill out forms together in real-time, similar to Google Forms but with live updates. Built as a backend-focused project, it showcases my skills in Python, FastAPI, WebSockets, and PostgreSQL, demonstrating my ability to design scalable, real-time systems. This project was developed to solve the problem of inefficient form collaboration, allowing seamless teamwork for surveys, feedback forms, and more.

Live Demo: https://collaborative-form.up.railway.app/docs
GitHub Repository: https://github.com/sanskarkesari/Collaborative-Form

Key Features

Dynamic Form Creation: Create forms with various field types (text, number, dropdown) via a REST API.
Real-Time Collaboration: Users can join a form session and see updates instantly using WebSockets.
Persistent Storage: Form responses are stored efficiently in PostgreSQL using the JSONB data type.
Input Validation: Ensures data integrity by validating field inputs (e.g., numbers must be numeric).
Scalable Design: Built with FastAPI and deployed on Railway for production-ready performance.

Tech Stack

Backend: Python, FastAPI
Real-Time Communication: WebSockets (via socketio)
Database: PostgreSQL (with JSONB for flexible storage)
Deployment: Docker Compose (local), Railway (production)
Other Tools: databases library for async PostgreSQL queries, uvicorn for ASGI server

Setup Instructions
Prerequisites

Python 3.9+
Docker and Docker Compose
PostgreSQL (if running without Docker)

Steps

Clone the Repository:
git clone https://github.com/sanskarkesari/Collaborative-Form.git
cd Collaborative-Form/backend


Set Up Environment:Create a .env file in the backend directory:
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/form_db


Run with Docker Compose:
docker-compose up --build

This will start the FastAPI server on http://localhost:8000 and the PostgreSQL database.

Access the API:

Open http://localhost:8000/docs to interact with the API.
Use POST /api/forms to create a form and GET /api/forms/{share_token} to retrieve form data.


Test WebSocket Functionality:

Use the provided HTML test client (or create your own) to connect to the WebSocket server using the share_token.
Example HTML client setup is available in the repository’s docs folder.



Demo and API Documentation

Live Demo: Test the application at https://collaborative-form.up.railway.app/docs. Create a form, join a session, and collaborate in real-time.
API Documentation: The live demo URL includes interactive API docs. Alternatively, see api_docs.md in the repository for detailed endpoint descriptions.

Example Usage

Create a form:POST /api/forms
{
    "name": "Team Survey",
    "fields": [
        {"type": "text", "label": "Team Name", "order": 1, "required": true},
        {"type": "number", "label": "Team Size", "order": 2, "required": false}
    ]
}

Response:{
    "id": "f1a2b3c4-d5e6-4f78-9123-456789abcdef",
    "share_token": "a1b2c3d4-e5f6-4g78-h123-456789abcdef"
}


Join a session and update fields using a WebSocket client with the share_token.

Design Decisions and Edge Cases
Design Decision: Flexible Data Storage
I chose PostgreSQL’s JSONB data type to store form responses, allowing flexibility for dynamic fields without altering the database schema. This design enables the system to handle various field types (text, number, dropdown) and scale for future additions. In the update_response function, I ensured reliability by casting the form_id to UUID, resolving an issue where updates failed due to type mismatches.
Edge Case: Input Validation
An interesting edge case I handled was invalid user inputs. For example, if a user enters a non-numeric value (e.g., "abc") for a number field like "Team Size," the system validates the input and throws an error (Invalid number value). This ensures data integrity and prevents invalid data from being stored, enhancing the user experience.
Contributing
Contributions are welcome! Feel free to open issues or submit pull requests. For major changes, please discuss them in an issue first.
Contact
For questions or collaboration opportunities, reach out to me at [your-email@example.com] or connect on [LinkedIn profile URL]. I’m excited to discuss how my backend engineering skills can contribute to your team!
