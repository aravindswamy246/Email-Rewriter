# Email Rewriter API - Render Deployment Configuration

## Environment Variables to Set in Render

Set these environment variables in your Render dashboard under Environment > Environment Variables:

### Required Variables:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Optional Variables (with defaults):
```
# Model Configuration
MODEL_NAME=gpt-4o-mini  # Most cost-effective: $0.00015/$0.0006 per 1K tokens
MAX_TOKENS=2000
TEMPERATURE=0.7

# Available models (in order of cost):
# - gpt-4o-mini: $0.00015/$0.0006 per 1K (recommended)
# - gpt-3.5-turbo: $0.0015/$0.002 per 1K
# - gpt-4o: $0.005/$0.015 per 1K
# - gpt-4-turbo: $0.01/$0.03 per 1K
# - gpt-4: $0.03/$0.06 per 1K

# API Configuration  
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60

# Production Settings
ENV=production
RENDER=true

# Security (optional - configure if needed)
ALLOWED_HOSTS=your-app.onrender.com,your-custom-domain.com

# Application Settings
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

## Project Features

### 1. Multiple Input Methods
- **File Upload via API**: Upload .txt, .pdf, .docx files through Swagger/Render UI
- **Input Folder Monitoring**: Place files in `data/input` folder for automated processing
- **JSON API**: Direct text input via `/rewrite` endpoint

### 2. Supported File Formats
- **TXT** (.txt): Plain text files
- **PDF** (.pdf): PDF documents (requires PyPDF2)
- **DOCX** (.docx): Microsoft Word documents (requires python-docx)

Maximum file size: 10MB per file

### 3. API Endpoints

#### Core Endpoints:
- `POST /rewrite` - Rewrite email via JSON request
- `POST /rewrite-upload` - Rewrite email via file upload (email + context files)
- `POST /process-input-folder` - Process all files in input folder
- `GET /health` - Health check with dependency status
- `GET /ping` - Simple ping endpoint

#### Utility Endpoints:
- `GET /folder-stats` - Get statistics about input/output folders
- `GET /supported-formats` - List supported file formats and requirements

### 4. Edge Cases Handled

#### File Validation:
- Empty files detection
- Minimum content length validation (100 characters for emails, 50 for context)
- File size limits (10MB)
- Unsupported format detection
- Corrupt file handling
- Encoding detection and handling (UTF-8, UTF-16, Latin-1, CP1252)

#### Error Handling:
- Missing API key
- Invalid API key format
- Rate limiting (configurable)
- Token limit exceeded
- File system errors
- Network timeouts
- Invalid request format
- Missing required fields

####  Processing:
- Multiple file processing with individual error tracking
- Automatic file movement after processing (to `processed` subdirectory)
- Failed file movement (to `errors` subdirectory)
- Empty folder handling
- Concurrent request handling

### 5. Industry-Standard Logging

#### Log Features:
- Request ID tracking for all operations
- Structured logging with timestamps
- Performance metrics (processing time, token usage, cost)
- Error tracking with context
- File rotation (10MB per file, 5 backup files)
- Separate log levels (DEBUG, INFO, WARNING, ERROR)
- Production-ready logging format

#### What Gets Logged:
- Every API request with request_id
- File processing attempts and results
- Token usage and estimated costs
- Processing time for each operation
- Errors with full context and stack traces
- Rate limiting events
- Health check status changes

#### Log Format:
```
2025-11-28 10:30:45.123 - request-id-12345 - email_rewriter - INFO - Request received
```

### 6. File Processing Workflow

#### Upload Method:
1. User uploads files via Swagger UI or API
2. Files validated for type, size, content
3. Text extracted from files
4. Email rewritten using AI
5. Result saved to output folder (if requested)
6. Response returned with metadata

#### Input Folder Method:
1. User places .txt files in `data/input` folder
2. Call `/process-input-folder` endpoint
3. All supported files processed automatically
4. Processed files moved to `data/input/processed`
5. Failed files moved to `data/input/errors`
6. Results saved to `data/output`
7. Detailed report returned with status of each file

### 7. Response Format

All responses include:
- Processing status
- Rewritten email content
- Metadata (processing time, tokens used, cost estimate, model used)
- File paths (if saved)
- Request ID for tracking
- Error details (if any)

### 8. Security Features

- API key validation
- Rate limiting per client IP
- CORS configuration (production-safe)
- Trusted host middleware (production)
- Request size limits
- Input sanitization
- File type restrictions
- Size limits enforcement

## Dependencies

Install required packages:
```bash
pip install fastapi uvicorn openai python-multipart aiofiles python-dotenv PyPDF2 python-docx
```

## Folder Structure

```
/Users/aravind246/Projects/AI/p2/
├── data/
│   ├── input/          # Place files here for processing
│   │   ├── processed/  # Successfully processed files moved here
│   │   └── errors/     # Failed files moved here
│   └── output/         # Processed results saved here
├── logs/               # Application logs
├── src/
│   ├── api/
│   │   ├── app.py     # Main FastAPI application
│   │   └── models/    # Request/Response models
│   ├── services/      # Business logic
│   ├── utils/         # Utilities (logging, file handling, monitoring)
│   └── config/        # Configuration
└── requirements.txt
```

## Testing the API

After deployment:
1. Go to `https://your-app.onrender.com/docs` for Swagger UI
2. Test `/ping` endpoint first
3. Check `/health` for API status
4. Try `/supported-formats` to see available formats
5. Upload test files via `/rewrite-upload`
6. Check `/folder-stats` for processing statistics

## Monitoring

Check logs for:
- Request IDs for tracking
- Processing times
- Token usage and costs
- Error patterns
- Rate limiting hits
- File processing success/failure rates

## Common Issues

1. **"Missing OPENAI_API_KEY"**: Set the API key in Render environment variables
2. **"Unsupported file type"**: Only .txt, .pdf, .docx are supported
3. **"File too short"**: Email must be at least 100 characters
4. **"Rate limit exceeded"**: Wait 60 seconds or adjust RATE_LIMIT_REQUESTS
5. **"No text extracted"**: Check if file is corrupt or empty

## Next Steps

1. Set all environment variables in Render
2. Deploy the application
3. Test all endpoints using Swagger UI
4. Monitor logs for any issues
5. Adjust rate limits and other settings as needed
