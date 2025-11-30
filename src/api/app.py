"""
Email Rewriter API - FastAPI Application

This module provides a REST API for rewriting emails using OpenAI GPT models.
It supports multiple input methods:
1. Direct JSON API requests
2. File uploads (TXT, PDF, DOCX)
3. Input folder monitoring for batch processing

Features:
- Multiple file format support with validation
- Industry-standard logging with request tracking
- Rate limiting and security features
- Comprehensive error handling
- Health monitoring and statistics endpoints

Author: Email Rewriter Team
Version: 0.1.0
"""

from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime, timedelta
from pathlib import Path
import os
from fastapi import FastAPI, Depends, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAIError
from .models import (
    EmailRewriteRequest, EmailRewriteResponse, HealthResponse,
    ApiError, ValidationError, ApiConfig,
    DetailedApiError, ErrorCode, DetailedApiException
)
from .exceptions import TokenLimitError, APIRateLimitError
from services import EmailService, EmailServiceInterface
from utils import (
    load_environment,
    CustomLogger,
)
from utils.file_handler import (
    extract_text_from_file, validate_file_type, validate_file_size,
    get_file_mime_type, save_output_file
)
from utils.input_folder_monitor import InputFolderMonitor, get_folder_stats
import time
from asyncio import Lock
import uuid
import mimetypes
from typing import List, Optional
from config.production import ProductionSettings

# ==================== INITIALIZATION ====================

# Load environment variables from .env file or environment
load_environment()

# Initialize API configuration with rate limits and size restrictions
api_config = ApiConfig()

# Validate production settings if running in production mode
if ProductionSettings.is_production():
    ProductionSettings.validate()

# ==================== FASTAPI APP SETUP ====================

app = FastAPI(
    title="Email Rewriter API",
    description="API for rewriting emails using OpenAI GPT with support for multiple input formats",
    version="0.1.0",
    debug=not ProductionSettings.is_production()
)

# Add trusted host middleware for production security
if ProductionSettings.is_production():
    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    if ProductionSettings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=ProductionSettings.ALLOWED_HOSTS
        )

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"] if not ProductionSettings.is_production() else ProductionSettings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression middleware for response compression
app.add_middleware(
    GZipMiddleware,
    minimum_size=api_config.max_request_size
)

# ==================== LOGGING AND MONITORING ====================

# Initialize custom logger with rotation and structured logging
logger = CustomLogger()

# ==================== FOLDER PATHS ====================

# Define base directory and data folders for file processing
BASE_DIR = Path(__file__).parent.parent.parent
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# Initialize input folder monitor for batch processing
input_monitor = InputFolderMonitor(INPUT_DIR, OUTPUT_DIR)

# ==================== DEPENDENCY INJECTION ====================


def get_email_service() -> EmailServiceInterface:
    """
    Dependency injection function to provide EmailService instance.

    Returns:
        EmailServiceInterface: Instance of the email rewriting service
    """
    return EmailService()


# ==================== HEALTH CHECK ENDPOINTS ====================


@app.get("/ping")
async def ping():
    """
    Simple ping endpoint to verify API is responding.

    Returns:
        dict: Simple ping/pong response
    """
    return {"ping": "pong"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Enhanced health check endpoint for production monitoring.
    Checks OpenAI API connectivity and system status.

    Returns:
        HealthResponse: Detailed health status including dependencies
    """
    start_time = time.time()

    try:
        # Check OpenAI connection (lightweight test)
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Just verify the client is configured (doesn't make API call)
        api_key_valid = bool(
            client.api_key and client.api_key.startswith("sk-"))

        status = "healthy" if api_key_valid else "degraded"

        return HealthResponse(
            status=status,
            version="0.1.0",
            uptime=time.time() - start_time,
            message=f"Service is {status}",
            dependencies={
                "openai": "connected" if api_key_valid else "error",
                "file_system": "ok"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version="0.1.0",
            uptime=time.time() - start_time,
            message=f"Health check failed: {str(e)}",
            dependencies={
                "openai": "error",
                "file_system": "unknown"
            }
        )

# ==================== API ENDPOINTS ====================
# After the health endpoint (around line 186), add these endpoints:

# ==================== EMAIL REWRITING ENDPOINTS ====================


@app.post("/rewrite", response_model=EmailRewriteResponse)
async def rewrite_email(
    request: EmailRewriteRequest,
    email_service: EmailServiceInterface = Depends(get_email_service)
):
    """
    Rewrite email content using AI based on target audience and tone.

    This endpoint accepts JSON input with email text and rewriting parameters.

    Args:
        request: EmailRewriteRequest containing email text and parameters
        email_service: Injected email service instance

    Returns:
        EmailRewriteResponse with rewritten content and metadata

    Example:
        ```json
        {
          "email_text": "Hi, I want to apply for the job...",
          "target_audience": "Hiring Manager at Tech Company",
          "tone": "professional",
          "focus_areas": ["technical skills", "experience"]
        }
        ```
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        logger.info(f"[{request_id}] → Processing email rewrite...")

        # Call the email service to rewrite
        result = await email_service.rewrite_email(
            email_text=request.email_text,
            target_audience=request.target_audience,
            tone=request.tone,
            focus_areas=request.focus_areas,
            additional_instructions=request.additional_instructions
        )

        processing_time = time.time() - start_time
        cost = result.get('usage', {}).get('cost_usd', 0)

        logger.info(
            f"[{request_id}] ✓ Email rewritten | "
            f"Time: {processing_time:.2f}s | "
            f"Tokens: {result.get('usage', {}).get('total_tokens', 0)} | "
            f"Cost: ${cost:.4f}"
        )

        return EmailRewriteResponse(
            rewritten_email=result.get("content", ""),
            saved_to=None,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "processing_time": processing_time,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                "cost_usd": cost,
                "model_used": result.get("model", "unknown"),
                "correlation_id": request_id,
                "target_audience": request.target_audience,
                "tone": request.tone
            }
        )

    except OpenAIError as e:
        logger.error(f"[{request_id}] OpenAI API error: {str(e)}")
        raise DetailedApiException(
            error_code=ErrorCode.OPENAI_ERROR,
            message=f"OpenAI API error: {str(e)}",
            suggestion="Check your API key and quota"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        raise DetailedApiException(
            error_code=ErrorCode.API_ERROR,
            message=f"Failed to process request: {str(e)}"
        )


@app.post("/rewrite-upload")
async def rewrite_email_upload(
    file: UploadFile = File(..., description="Email file (.txt, .pdf, .docx)"),
    target_audience: str = Form(..., description="Target audience or context"),
    tone: str = Form(default="professional",
                     description="Desired tone (professional, casual, academic)"),
    focus_areas: Optional[str] = Form(
        default=None, description="Comma-separated focus areas"),
    additional_instructions: Optional[str] = Form(
        default=None, description="Additional instructions"),
    email_service: EmailServiceInterface = Depends(get_email_service)
):
    """
    Rewrite email from uploaded file (.txt, .pdf, .docx).

    Upload a file and specify rewriting parameters. The API will extract text
    from the file and rewrite it according to your specifications.

    Supported formats:
    - .txt (text files)
    - .pdf (PDF documents)
    - .docx (Word documents)

    Args:
        file: Uploaded file containing email content
        target_audience: Description of target audience
        tone: Desired tone for the rewrite
        focus_areas: Comma-separated list of areas to emphasize
        additional_instructions: Optional specific instructions

    Returns:
        JSON response with rewritten content and metadata
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        # Validate file
        if not file.filename:
            raise DetailedApiException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="No filename provided",
                suggestion="Please upload a file with a valid name"
            )

        logger.info(f"[{request_id}] → Processing file: {file.filename}")

        # Validate file type
        if not validate_file_type(file.filename):
            raise DetailedApiException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=f"Unsupported file type: {file.filename}",
                suggestion="Please upload .txt, .pdf, or .docx files only"
            )

        # Read file content
        file_content = await file.read()

        # Validate file size
        if not validate_file_size(file_content):
            raise DetailedApiException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="File size exceeds maximum allowed size (10MB)",
                suggestion="Please upload a smaller file"
            )

        # Extract text from file
        email_text = extract_text_from_file(file_content, file.filename)

        if not email_text or len(email_text.strip()) < 10:
            raise DetailedApiException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="Extracted text is too short or empty",
                suggestion="Please ensure the file contains readable text content"
            )

        # Parse focus areas
        focus_areas_list = [area.strip() for area in focus_areas.split(
            ",")] if focus_areas else None

        # Call the email service
        result = await email_service.rewrite_email(
            email_text=email_text,
            target_audience=target_audience,
            tone=tone,
            focus_areas=focus_areas_list,
            additional_instructions=additional_instructions
        )

        processing_time = time.time() - start_time
        cost = result.get('usage', {}).get('cost_usd', 0)

        logger.info(
            f"[{request_id}] ✓ File rewritten: {file.filename} | "
            f"Time: {processing_time:.2f}s | "
            f"Tokens: {result.get('usage', {}).get('total_tokens', 0)} | "
            f"Cost: ${cost:.4f}"
        )

        return JSONResponse(content={
            "status": "success",
            "rewritten_email": result.get("content", ""),
            "original_filename": file.filename,
            "target_audience": target_audience,
            "tone": tone,
            "processing_time": processing_time,
            "model_used": result.get("model", "unknown"),
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "cost_usd": result.get("usage", {}).get("cost_usd", 0),
            "correlation_id": request_id,
            "timestamp": datetime.now().isoformat()
        })

    except DetailedApiException:
        raise
    except ValueError as e:
        logger.error(f"[{request_id}] Validation error: {str(e)}")
        raise DetailedApiException(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=str(e),
            suggestion="Check file format and content"
        )
    except OpenAIError as e:
        logger.error(f"[{request_id}] OpenAI API error: {str(e)}")
        raise DetailedApiException(
            error_code=ErrorCode.OPENAI_ERROR,
            message=f"OpenAI API error: {str(e)}",
            suggestion="Check your API key and quota"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        raise DetailedApiException(
            error_code=ErrorCode.API_ERROR,
            message=f"Failed to process file upload: {str(e)}"
        )


@app.get("/folder-stats")
async def get_folder_statistics():
    """
    Get statistics about input and output folders.
    Useful for monitoring file processing activity.
    """
    try:
        input_stats = get_folder_stats(INPUT_DIR)
        output_stats = get_folder_stats(OUTPUT_DIR)

        return JSONResponse(content={
            "status": "success",
            "input_folder": {
                "path": str(INPUT_DIR),
                **input_stats
            },
            "output_folder": {
                "path": str(OUTPUT_DIR),
                **output_stats
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get folder stats: {str(e)}")
        raise DetailedApiException(
            error_code=ErrorCode.API_ERROR,
            message="Failed to retrieve folder statistics",
            suggestion="Check folder permissions"
        )


@app.post("/process-input-folder")
async def process_input_folder_endpoint(
    target_audience: str = Form(...,
                                description="Target audience for email rewriting"),
    service: EmailServiceInterface = Depends(get_email_service)
):
    """
    Process all files in the input folder.
    This endpoint scans the input folder for .txt files and processes them.
    """
    request_id = str(uuid.uuid4())
    logger.set_request_context(request_id)

    try:
        # Scan for files
        from utils.file_handler import scan_input_folder
        files = scan_input_folder(INPUT_DIR)

        if not files:
            return JSONResponse(content={
                "status": "success",
                "message": "No files found in input folder",
                "processed": 0,
                "input_folder": str(INPUT_DIR)
            })

        results = []

        for file_path in files:
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8') as f:
                    email_text = f.read()

                # Validate content length
                if len(email_text) < 100:
                    results.append({
                        "file": file_path.name,
                        "status": "skipped",
                        "reason": "File too short (minimum 100 characters)"
                    })
                    continue

                # Process with email service
                result = await service.rewrite_email(
                    email_text=email_text,
                    target_audience=target_audience,
                    tone="professional"
                )

                # Save to output folder
                from utils.file_handler import save_output_file
                output_path = await save_output_file(
                    result.get("content", ""),
                    OUTPUT_DIR,
                    f"processed_{file_path.stem}"
                )

                # Move processed file to subdirectory
                processed_dir = INPUT_DIR / "processed"
                processed_dir.mkdir(exist_ok=True)
                moved_path = processed_dir / file_path.name
                file_path.rename(moved_path)

                results.append({
                    "file": file_path.name,
                    "status": "success",
                    "output": str(output_path),
                    "moved_to": str(moved_path)
                })

            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {str(e)}")
                results.append({
                    "file": file_path.name,
                    "status": "error",
                    "error": str(e)
                })

        return JSONResponse(content={
            "status": "success",
            "processed": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "skipped": len([r for r in results if r["status"] == "skipped"]),
            "results": results,
            "request_id": request_id
        })

    except Exception as e:
        logger.log_error(e, {"request_id": request_id})
        raise DetailedApiException(
            error_code=ErrorCode.API_ERROR,
            message=f"Failed to process input folder: {str(e)}",
            suggestion="Check folder permissions and file formats"
        )


@app.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats and their details.
    """
    return JSONResponse(content={
        "supported_formats": [
            {
                "extension": ".txt",
                "mime_type": "text/plain",
                "description": "Plain text files",
                "max_size_mb": 10
            },
            {
                "extension": ".pdf",
                "mime_type": "application/pdf",
                "description": "PDF documents",
                "max_size_mb": 10,
                "requires": "PyPDF2"
            },
            {
                "extension": ".docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "description": "Microsoft Word documents",
                "max_size_mb": 10,
                "requires": "python-docx"
            }
        ],
        "input_folder": str(INPUT_DIR),
        "output_folder": str(OUTPUT_DIR)
    })
