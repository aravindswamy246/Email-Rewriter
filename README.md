# Email Rewriter API

A production-ready FastAPI application that rewrites emails using OpenAI GPT models with support for multiple input formats and comprehensive error handling.

## 🌟 Features

### Multiple Input Methods
- **Direct API**: Send email text directly via JSON API
- **File Upload**: Upload TXT, PDF, or DOCX files through Swagger UI
- **Batch Processing**: Place files in input folder for automated processing

### File Format Support
- **TXT**: Plain text files with multi-encoding support (UTF-8, UTF-16, Latin-1, CP1252)
- **PDF**: PDF documents with page-by-page text extraction
- **DOCX**: Microsoft Word documents with paragraph extraction
- **Size Limit**: 10MB per file

### Advanced Features
- ✅ **Jinja2 Prompt Templates**: Structured, maintainable prompt engineering
- ✅ **Cost Tracking**: Real-time token usage and cost calculation
- ✅ **Dynamic Pricing**: Centralized pricing config for all OpenAI models
- ✅ **GPT-4o-mini Default**: Most cost-effective model (97% cheaper than GPT-4)
- ✅ **Optimized Logging**: Clean output with cost/time metrics
- ✅ **Industry-standard logging** with request ID tracking
- ✅ **Rate limiting** per client IP (configurable)
- ✅ **Comprehensive error handling** with detailed messages
- ✅ **Health monitoring** and statistics endpoints
- ✅ **CORS configuration** for web applications
- ✅ **GZip compression** for faster responses
- ✅ **Security middleware** for production
- ✅ **File validation** and sanitization

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd p2

# Create virtual environment
python -m venv env_p2
source env_p2/bin/activate  # On Windows: env_p2\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (with defaults)
MODEL_NAME=gpt-4o-mini  # Most cost-effective: $0.00015/$0.0006 per 1K tokens
MAX_TOKENS=2000
TEMPERATURE=0.7
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60
```

### 3. Run the Application

```bash
# Development mode
uvicorn src.main:app --reload

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 API Endpoints

### Core Endpoints

#### POST `/rewrite`
Rewrite email from JSON request with Jinja2-powered prompts
```json
{
  "email_text": "Your email content here (min 100 chars)",
  "target_audience": "Description of target audience (min 50 chars)",
  "tone": "professional",
  "focus_areas": ["clarity", "technical accuracy"],
  "additional_instructions": "Emphasize leadership experience",
  "save_output": true
}
```

**Response includes cost tracking:**
```json
{
  "rewritten_email": "...",
  "metadata": {
    "processing_time": 3.45,
    "tokens_used": 428,
    "cost_usd": 0.0257,
    "model_used": "gpt-4"
  }
}
```

#### POST `/rewrite-upload`
Upload files for email rewriting
- **Files**: Email file + Context file (both required)
- **Formats**: .txt, .pdf, .docx
- **Parameters**: tone (professional/casual/academic), save (true/false)

#### POST `/process-input-folder`
Process all files in the input folder
- **Parameter**: target_audience (required)
- **Action**: Processes all supported files in `data/input`
- **Result**: Files moved to `processed` subfolder after success

### Utility Endpoints

#### GET `/health`
Health check with dependency status

#### GET `/ping`
Simple connectivity test

#### GET `/folder-stats`
Statistics about input/output folders

#### GET `/supported-formats`
List of supported file formats and requirements

## 📁 Project Structure

```
p2/
├── src/
│   ├── api/
│   │   ├── app.py              # Main FastAPI application
│   │   ├── models/             # Pydantic models
│   │   └── exceptions.py       # Custom exceptions
│   ├── services/               # Business logic
│   │   ├── base.py            # Service interfaces
│   │   └── email_service.py   # Email rewriting service
│   ├── utils/                  # Utilities
│   │   ├── logger.py          # Custom logging
│   │   ├── file_handler.py    # File processing
│   │   ├── input_folder_monitor.py  # Batch processing
│   │   └── env_loader.py      # Environment management
│   ├── config/                 # Configuration
│   │   └── production.py      # Production settings
│   └── main.py                # Application entry point
├── data/
│   ├── input/                 # Place files here for processing
│   │   ├── processed/        # Successfully processed files
│   │   └── errors/           # Failed files
│   └── output/               # Processed results
├── logs/                      # Application logs
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔒 Security

- API key validation
- Rate limiting (configurable per IP)
- File type restrictions
- File size limits (10MB)
- Input sanitization
- CORS configuration
- Trusted host middleware (production)

## 📊 Logging

All requests are logged with:
- Unique request ID
- Processing time
- Token usage and costs
- Error details with stack traces
- Client IP and user agent

Log format:
```
2025-11-28 10:30:45.123 - request-id-12345 - email_rewriter - INFO - Request received
```

Logs are rotated:
- Max file size: 10MB
- Backup count: 5 files
- Location: `logs/` directory

## 🐛 Error Handling

All errors include:
- Error code
- Detailed message
- Suggested action
- Request correlation ID
- Timestamp

Common error scenarios:
- Missing/invalid API key
- Unsupported file format
- File too large/small
- Rate limit exceeded
- Token limit exceeded
- File processing errors
- Network errors

## 🧪 Testing

Access the Swagger UI at `/docs` to test all endpoints interactively.

### Example: Test File Upload

1. Go to `/docs`
2. Navigate to `/rewrite-upload`
3. Click "Try it out"
4. Upload your email file (.txt, .pdf, or .docx)
5. Upload context file (e.g., job description)
6. Select tone and save options
7. Click "Execute"

### Example: Batch Processing

1. Place .txt files in `data/input/`
2. Call `/process-input-folder` with target_audience
3. Check results in `data/output/`
4. Processed files moved to `data/input/processed/`

## 🚀 Deployment

### Render Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy!

See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for detailed instructions.

### Docker Deployment

**Using Docker Compose (Recommended):**
```bash
# Start container (builds automatically if needed)
docker compose up -d

# View logs in real-time
docker compose logs -f

# Stop container
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

**Why Docker Compose?**
- ✅ Manages everything from `docker-compose.yml`
- ✅ Handles networking, volumes, environment automatically
- ✅ One command does it all
- ✅ Auto-reload on code changes (no rebuild needed for `.py` files)

**Access your API:**
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for troubleshooting and advanced options.

## 📝 Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `MODEL_NAME`: GPT model to use (default: gpt-4o-mini - most cost-effective)
- `MAX_TOKENS`: Maximum tokens per request (default: 2000)
- `TEMPERATURE`: Response creativity (default: 0.7)
- `LOG_LEVEL`: Logging level (default: INFO)
- `RATE_LIMIT_REQUESTS`: Max requests per period (default: 10)
- `RATE_LIMIT_PERIOD`: Rate limit period in seconds (default: 60)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[MIT License](LICENSE)

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `/docs`
- Review logs in `logs/` directory

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 🎯 Roadmap

- [ ] Support for more file formats (HTML, RTF)
- [ ] Email template library
- [ ] Multi-language support
- [ ] Advanced tone customization
- [ ] Email analytics dashboard
- [ ] Webhook notifications
- [ ] Bulk API operations
- [ ] Custom model fine-tuning

## ⚡ Performance

- File processing: < 5 seconds for most files
- API response time: Typically 2-10 seconds depending on email length
- Concurrent requests: Supports multiple simultaneous requests
- Rate limiting: Configurable per client

## 🔍 Monitoring

Monitor your application:
- `/health` endpoint for service status
- `/folder-stats` for processing statistics
- Log files for detailed operation history
- Token usage tracking for cost management

---

**Made with ❤️ for better email communication**
