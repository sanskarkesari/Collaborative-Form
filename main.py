from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
from pydantic import BaseModel
from typing import List, Dict, Any, Tuple
import uuid
import json
import os
import asyncio
from dotenv import load_dotenv
import socketio
import logging

# Configure logging for deployment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Add CORS middleware to handle all CORS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment; adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server without its own CORS handling
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=None)
app.mount('/socket.io', socketio.ASGIApp(sio))

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+asyncmy://user:password@localhost:3306/form_db")
database = Database(DATABASE_URL)

# Connection manager for Socket.IO
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Tuple[str, str]]] = {}

    async def connect(self, share_token: str, sid: str, username: str):
        if share_token not in self.active_connections:
            self.active_connections[share_token] = []
        self.active_connections[share_token].append((sid, username))
        logger.info(f"Connected: {share_token} now has {self.active_connections[share_token]}")
        join_message = {"type": "user_joined", "username": username}
        await self.broadcast(share_token, join_message)

    async def disconnect(self, share_token: str, sid: str):
        if share_token in self.active_connections:
            for conn in self.active_connections[share_token]:
                if conn[0] == sid:
                    left_username = conn[1]
                    self.active_connections[share_token].remove(conn)
                    logger.info(f"Disconnected: {share_token} now has {self.active_connections[share_token]}")
                    left_message = {"type": "user_left", "username": left_username}
                    await self.broadcast(share_token, left_message)
                    break
            if not self.active_connections[share_token]:
                del self.active_connections[share_token]

    async def broadcast(self, share_token: str, message: Dict):
        logger.info(f"Broadcasting to {share_token}: {message}")
        if share_token in self.active_connections:
            for sid, _ in self.active_connections[share_token]:
                try:
                    logger.info(f"Sending to sid {sid}")
                    await sio.emit('message', message, room=sid)
                except Exception as e:
                    logger.error(f"Error broadcasting to {sid}: {str(e)}")

manager = ConnectionManager()

# Pydantic models
class FieldCreate(BaseModel):
    type: str
    label: str
    options: List[str] = []
    order: int
    required: bool = False

class FormCreate(BaseModel):
    name: str
    fields: List[FieldCreate]

class FormResponse(BaseModel):
    id: str
    name: str
    fields: List[dict]
    response: dict

# Database operations
async def get_form_id_from_token(share_token: str) -> str:
    query = "SELECT id FROM forms WHERE share_token = :share_token"
    result = await database.fetch_one(query=query, values={"share_token": share_token})
    if not result:
        raise HTTPException(status_code=404, detail="Form not found")
    return result["id"]

async def update_response(form_id: str, field_id: str, value: Any):
    field = await database.fetch_one(
        query="SELECT type, options FROM fields WHERE id = :field_id AND form_id = :form_id",
        values={"field_id": field_id, "form_id": form_id}
    )
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    if field["type"] == "number":
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid number value")
    elif field["type"] == "dropdown":
        options = json.loads(field["options"]) if field["options"] else []
        if value not in options:
            raise HTTPException(status_code=400, detail="Invalid dropdown value")

    query = """
        UPDATE responses 
        SET data = JSON_SET(data, :field_path, :value), last_updated_at = NOW() 
        WHERE form_id = :form_id
    """
    await database.execute(
        query=query,
        values={"field_path": f'$.{field_id}', "value": value, "form_id": form_id}
    )

# API endpoints
@app.on_event("startup")
async def startup():
    try:
        await database.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    logger.info("Database disconnected")

@app.post("/api/forms", response_model=dict)
async def create_form(form: FormCreate):
    try:
        form_id = str(uuid.uuid4())
        share_token = str(uuid.uuid4())
        
        await database.execute(
            query="INSERT INTO forms (id, name, share_token) VALUES (:id, :name, :share_token)",
            values={"id": form_id, "name": form.name, "share_token": share_token}
        )
        
        for field in form.fields:
            field_id = str(uuid.uuid4())
            await database.execute(
                query="INSERT INTO fields (id, form_id, type, label, options, `order`, required) VALUES (:id, :form_id, :type, :label, :options, :order, :required)",
                values={
                    "id": field_id,
                    "form_id": form_id,
                    "type": field.type,
                    "label": field.label,
                    "options": json.dumps(field.options),
                    "order": field.order,
                    "required": field.required
                }
            )
        
        await database.execute(
            query="INSERT INTO responses (id, form_id, data) VALUES (:id, :form_id, :data)",
            values={"id": str(uuid.uuid4()), "form_id": form_id, "data": json.dumps({})}
        )
        
        return {"id": form_id, "share_token": share_token}
    except Exception as e:
        logger.error(f"Error creating form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating form: {str(e)}")

@app.get("/api/forms/{share_token}", response_model=FormResponse)
async def get_form(share_token: str):
    try:
        form_id = await get_form_id_from_token(share_token)
        form = await database.fetch_one(
            query="SELECT id, name FROM forms WHERE id = :form_id",
            values={"form_id": form_id}
        )
        fields = await database.fetch_all(
            query="SELECT id, type, label, options, `order`, required FROM fields WHERE form_id = :form_id ORDER BY `order`",
            values={"form_id": form_id}
        )
        response_data = await database.fetch_one(
            query="SELECT data FROM responses WHERE form_id = :form_id",
            values={"form_id": form_id}
        )
        
        return {
            "id": form["id"],
            "name": form["name"],
            "fields": [
                {
                    "id": f["id"],
                    "type": f["type"],
                    "label": f["label"],
                    "options": json.loads(f["options"]) if f["options"] else [],
                    "order": f["order"],
                    "required": f["required"]
                } for f in fields
            ],
            "response": json.loads(response_data["data"])
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving form: {str(e)}")

# Test endpoint to debug CORS headers
@app.get("/test-cors")
async def test_cors(response: Response):
    logger.info("Response headers for /test-cors:", response.headers)
    return {"message": "CORS test"}

# Serve favicon.ico to silence browser error
@app.get("/favicon.ico")
async def favicon():
    return Response(content="", media_type="image/x-icon")

# Debug middleware to log headers for /socket.io/ requests
@app.middleware("http")
async def log_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/socket.io"):
        logger.info(f"Headers for {request.url.path}: {response.headers}")
    return response

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    query = environ.get('QUERY_STRING', '')
    params = dict(q.split('=') for q in query.split('&') if q)
    share_token = params.get('share_token')
    if not share_token or share_token.lower() == "null" or share_token.strip() == "":
        logger.warning(f"Invalid share_token: {share_token}")
        await sio.disconnect(sid)
        return False
    try:
        await get_form_id_from_token(share_token)
        await sio.save_session(sid, {'share_token': share_token})
        logger.info(f"Socket.IO connect - Origin: {environ.get('HTTP_ORIGIN')}, SID: {sid}, Session: {await sio.get_session(sid)}")
        return True
    except HTTPException as e:
        logger.error(f"Socket.IO connect error: {e.status_code}: {e.detail}")
        await sio.disconnect(sid)
        return False

@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    share_token = session.get('share_token')
    if share_token:
        await manager.disconnect(share_token, sid)

@sio.on('message')
async def handle_message(sid, data):
    logger.info(f"Received message from {sid}: {data}")
    try:
        session = await sio.get_session(sid)
        share_token = session['share_token']
        form_id = await get_form_id_from_token(share_token)

        if data["type"] == "join":
            username = data.get("username")
            if not username:
                logger.warning(f"No username provided in join message, disconnecting {sid}")
                await sio.disconnect(sid)
                return
            await manager.connect(share_token, sid, username)
        elif data["type"] == "update":
            field_id = data["field_id"]
            value = data["value"]
            username = next((conn[1] for conn in manager.active_connections[share_token] if conn[0] == sid), None)
            if username is None:
                logger.warning(f"Username not found for sid {sid} in share_token {share_token}, using default")
                username = "Unknown User"
            logger.info(f"Updating field {field_id} with value {value} for form {form_id}")
            await update_response(form_id, field_id, value)
            broadcast_message = {
                "type": "update",
                "field_id": field_id,
                "value": value,
                "updated_by": username
            }
            await manager.broadcast(share_token, broadcast_message)
    except HTTPException as e:
        logger.error(f"Socket.IO message error: {e.status_code}: {e.detail}")
        await sio.disconnect(sid)
    except Exception as e:
        logger.error(f"Socket.IO error: {str(e)}")
        await sio.disconnect(sid)

# Error handler for unexpected exceptions
@app.exception_handler(Exception)
async def custom_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )