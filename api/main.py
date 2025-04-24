from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
import time
import os
import tempfile
from dotenv import load_dotenv

from api.models import PocketClinicRequest, PocketClinicResponse, ErrorResponse
from main import PocketClinicCrew

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PocketClinic API",
    description="API for PocketClinic - A Simple AI healthcare assistant",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP and request details
    client_host = request.client.host if request.client else "unknown"
    method = request.method
    url = request.url.path
    
    logger.info(f"Request started: {method} {url} from {client_host}")
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(f"Request completed: {method} {url} - Status: {response.status_code} - Time: {process_time:.4f}s")
        
        return response
    except Exception as e:
        # Log any unhandled exceptions
        process_time = time.time() - start_time
        logger.error(f"Request failed: {method} {url} - Error: {str(e)} - Time: {process_time:.4f}s")
        
        # Return a JSON error response
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                status="error",
                message="Internal server error",
                details={"error": str(e)}
            ).dict()
        )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to PocketClinic API",
        "docs": "/docs",
        "version": "0.1.0"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# Main PocketClinic endpoint for text input
@app.post("/api/v1/process", response_model=PocketClinicResponse, tags=["PocketClinic"])
async def process_request(request: PocketClinicRequest):
    """
    Process a request with text input
    
    This endpoint accepts a text message and processes it through the PocketClinic workflow:
    1. Collect symptoms from the text
    2. Triage the symptoms
    3. Dispatch a referral via SMS
    
    Returns the result of the entire process.
    """
    try:
        logger.info(f"Processing text request for {request.phone_number}")
        
        # Create PocketClinicCrew instance
        crew = PocketClinicCrew(
            text_message=request.text_message,
            audio_file=None,
            phone_number=request.phone_number
        )
        
        # Run the crew
        result = crew.run()
        
        # Return response
        return PocketClinicResponse(
            status="success",
            message="Request processed successfully",
            details={"result": result}
        )
    except Exception as e:
        logger.error(f"Error processing text request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Main PocketClinic endpoint for audio input
@app.post("/api/v1/process/audio", response_model=PocketClinicResponse, tags=["PocketClinic"])
async def process_audio_request(
    phone_number: str = Form(...),
    audio_file: UploadFile = File(...),
):
    """
    Process a request with audio input
    
    This endpoint accepts an audio file and processes it through the PocketClinic workflow:
    1. Collect symptoms from the audio
    2. Triage the symptoms
    3. Dispatch a referral via SMS
    
    Returns the result of the entire process.
    """
    try:
        logger.info(f"Processing audio request for {phone_number}")
        
        # Save uploaded file to a temporary file
        suffix = ".wav"  # Default suffix
        if audio_file.filename and "." in audio_file.filename:
            suffix = "." + audio_file.filename.split(".")[-1]
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await audio_file.read())
            temp_path = temp_file.name
        
        try:
            # Create PocketClinicCrew instance
            crew = PocketClinicCrew(
                text_message=None,
                audio_file=temp_path,
                phone_number=phone_number
            )
            
            # Run the crew
            result = crew.run()
            
            # Return response
            return PocketClinicResponse(
                status="success",
                message="Request processed successfully",
                details={"result": result}
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        logger.error(f"Error processing audio request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
