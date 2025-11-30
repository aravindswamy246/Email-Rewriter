# Jinja2 Prompt Templates Guide

This guide explains how the Jinja2-based prompt template system works in this email rewriting API.

## Overview

The project uses **Jinja2** templating for all OpenAI prompts, providing:
- **Structured prompts** with consistent formatting
- **Dynamic variable injection** for context-specific rewriting
- **Conditional logic** for optional parameters
- **Maintainability** - all prompts in one centralized file
- **Testability** - easy to test prompt generation without API calls

## Architecture

```
src/utils/prompt_templates.py       # Central template repository
src/services/email_service.py       # Consumer of templates
```

## Template Structure

All templates follow this pattern:

```python
prompt = prompt_templates.get_<template_name>(
    required_param="value",
    optional_param="value"  # Can be None
)
```

The template engine:
1. Loads the Jinja2 template string
2. Injects variables with `.render()`
3. Returns formatted prompt string
4. Handles None values gracefully with conditionals

## Available Templates

### 1. Base System Prompt

```python
system_prompt = prompt_templates.get_base_system_prompt()
```

**Purpose**: Standard system message for all email rewriting tasks  
**Variables**: None  
**Output**: Professional email rewriting assistant instructions

---

### 2. Email Rewrite Prompt

```python
user_prompt = prompt_templates.get_email_rewrite_prompt(
    email_text="Original email content...",
    target_audience="hiring managers at tech companies",
    tone="professional",  # Optional
    focus_areas=["clarity", "conciseness"],  # Optional
    additional_instructions="Emphasize leadership skills"  # Optional
)
```

**Purpose**: General-purpose email rewriting  
**Required**:
- `email_text`: The email to rewrite
- `target_audience`: Who will read this email

**Optional**:
- `tone`: professional (default), casual, academic, friendly
- `focus_areas`: List of aspects to emphasize
- `additional_instructions`: Specific requirements

**Example Output**:
```
You are tasked with rewriting the following email to better suit the target audience and context.

Target Audience: hiring managers at tech companies

Desired Tone: professional

Focus Areas:
- clarity
- conciseness

Additional Instructions:
Emphasize leadership skills

Original Email:
Original email content...

Please rewrite this email maintaining the core message while improving clarity, tone, and professionalism.
```

---

### 3. Job Application Email Prompt

```python
user_prompt = prompt_templates.get_job_application_email_prompt(
    email_text="Dear Hiring Manager, I am applying...",
    job_description="Senior Python Developer position...",
    company_name="TechCorp Inc.",  # Optional
    key_qualifications=["5 years Python", "FastAPI expert"]  # Optional
)
```

**Purpose**: Specialized for job applications  
**Required**:
- `email_text`: Cover letter or application email
- `job_description`: Job posting details

**Optional**:
- `company_name`: Company name to personalize
- `key_qualifications`: Skills to highlight

**Use Case**: When user specifies it's a job application email

---

### 4. Follow-Up Email Prompt

```python
user_prompt = prompt_templates.get_follow_up_email_prompt(
    email_text="Following up on my previous email...",
    context="Initial outreach sent 2 weeks ago",
    relationship="potential client",  # Optional
    days_since_last_contact=14  # Optional
)
```

**Purpose**: Follow-up and reminder emails  
**Required**:
- `email_text`: Follow-up message
- `context`: Previous interaction context

**Optional**:
- `relationship`: Type of relationship (client, colleague, etc.)
- `days_since_last_contact`: Time elapsed

---

### 5. Email Summary Prompt

```python
summary = prompt_templates.get_email_summary_prompt(
    email_text="Long email with multiple points...",
    max_sentences=3  # Optional
)
```

**Purpose**: Generate concise email summaries  
**Required**:
- `email_text`: Email to summarize

**Optional**:
- `max_sentences`: Maximum sentences in summary (default: 3)

**Use Case**: Quick overview of lengthy emails

---

### 6. Batch Processing Prompt

```python
batch_prompt = prompt_templates.get_batch_processing_prompt(
    batch_instructions="Rewrite all emails with professional tone",
    file_count=15,
    tone="professional"  # Optional
)
```

**Purpose**: Instructions for batch file processing  
**Required**:
- `batch_instructions`: What to do with all files
- `file_count`: Number of files being processed

**Optional**:
- `tone`: Apply consistent tone across batch

**Use Case**: Input folder batch operations

---

## Integration with EmailService

### Standard Email Rewriting

```python
# In src/services/email_service.py
async def rewrite_email(
    self,
    email_text: str,
    target_audience: str,
    tone: str = "professional",
    focus_areas: Optional[List[str]] = None,
    additional_instructions: Optional[str] = None
) -> Dict[str, Any]:
    # Generate prompts using templates
    system_prompt = prompt_templates.get_base_system_prompt()
    user_prompt = prompt_templates.get_email_rewrite_prompt(
        email_text=email_text,
        target_audience=target_audience,
        tone=tone,
        focus_areas=focus_areas,
        additional_instructions=additional_instructions
    )
    
    # Call OpenAI with structured prompts
    response = await self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=self.temperature,
        max_tokens=self.max_tokens
    )
    
    # Return rewritten content + usage stats
    return {
        "content": response.choices[0].message.content,
        "usage": {...}
    }
```

### Job Application Specialization

```python
async def rewrite_job_application_email(
    self,
    email_text: str,
    job_description: str,
    company_name: Optional[str] = None,
    key_qualifications: Optional[List[str]] = None
) -> Dict[str, Any]:
    system_prompt = prompt_templates.get_base_system_prompt()
    user_prompt = prompt_templates.get_job_application_email_prompt(
        email_text=email_text,
        job_description=job_description,
        company_name=company_name,
        key_qualifications=key_qualifications
    )
    
    # Same API call pattern as above
```

---

## API Request Examples

### 1. Standard Email Rewrite (POST /rewrite)

```json
{
  "email_text": "Hi, I wanted to check in about the project status. Let me know when you have time.",
  "target_audience": "C-level executives at Fortune 500 company",
  "tone": "professional",
  "focus_areas": ["brevity", "confidence"],
  "additional_instructions": "Include a clear call-to-action"
}
```

**Behind the scenes**:
- System prompt from `get_base_system_prompt()`
- User prompt from `get_email_rewrite_prompt()` with all parameters
- OpenAI processes structured prompt
- Returns rewritten email + token usage

---

### 2. File Upload (POST /rewrite-upload)

```bash
curl -X POST "http://localhost:8000/rewrite-upload" \
  -F "file=@cover_letter.docx" \
  -F "target_audience=hiring managers in tech" \
  -F "tone=professional"
```

**Behind the scenes**:
- Extracts text from DOCX
- Generates prompt using `get_email_rewrite_prompt()`
- Same OpenAI processing
- Returns rewritten content

---

### 3. Input Folder Batch (POST /process-input-folder)

```json
{
  "batch_size": 10,
  "tone": "professional"
}
```

**Behind the scenes**:
- Scans input folder for .txt files
- For each file: generates prompt using `get_email_rewrite_prompt()`
- Optional: uses `get_batch_processing_prompt()` for batch-level instructions
- Processes files in batches
- Saves outputs to output folder

---

## Template Customization

### Adding a New Template

1. **Define template in `prompt_templates.py`**:

```python
def get_apology_email_prompt(
    self,
    email_text: str,
    incident_description: str,
    severity: str = "medium"
) -> str:
    """Generate prompt for apology emails."""
    template = Template("""
You are rewriting an apology email for a {{ severity }} severity incident.

Incident: {{ incident_description }}

Original Email:
{{ email_text }}

Requirements:
- Acknowledge the issue sincerely
- Take responsibility
- Provide solution or next steps
- Maintain professional tone
    """)
    
    return template.render(
        email_text=email_text,
        incident_description=incident_description,
        severity=severity
    ).strip()
```

2. **Add method to EmailService**:

```python
async def rewrite_apology_email(
    self,
    email_text: str,
    incident_description: str,
    severity: str = "medium"
) -> Dict[str, Any]:
    system_prompt = prompt_templates.get_base_system_prompt()
    user_prompt = prompt_templates.get_apology_email_prompt(
        email_text=email_text,
        incident_description=incident_description,
        severity=severity
    )
    
    # Standard OpenAI call pattern
```

3. **Create API endpoint in `app.py`**:

```python
@app.post("/rewrite-apology")
async def rewrite_apology(request: ApologyEmailRequest):
    result = await email_service.rewrite_apology_email(
        email_text=request.email_text,
        incident_description=request.incident_description,
        severity=request.severity
    )
    return result
```

---

## Benefits of Jinja2 Templating

### 1. Consistency
All prompts follow same structure and formatting rules.

### 2. Maintainability
Change prompt structure once, affects all API calls.

### 3. Version Control
Easy to track prompt changes in git history.

### 4. Testing
Test prompt generation without OpenAI API calls:

```python
def test_email_rewrite_prompt():
    prompt = prompt_templates.get_email_rewrite_prompt(
        email_text="Test email",
        target_audience="test audience",
        tone="professional"
    )
    
    assert "Test email" in prompt
    assert "test audience" in prompt
    assert "professional" in prompt
```

### 5. A/B Testing
Easy to create template variations for experimentation:

```python
# Template V1
template_v1 = "Rewrite the following email..."

# Template V2
template_v2 = "Transform this email to be more engaging..."
```

### 6. Conditional Logic
Handle optional parameters cleanly:

```jinja2
{% if focus_areas %}
Focus Areas:
{% for area in focus_areas %}
- {{ area }}
{% endfor %}
{% endif %}
```

---

## Best Practices

### 1. Always Use Templates
❌ **Don't**:
```python
prompt = f"Rewrite this email: {email_text} for {audience}"
```

✅ **Do**:
```python
prompt = prompt_templates.get_email_rewrite_prompt(
    email_text=email_text,
    target_audience=audience
)
```

### 2. Validate Inputs Before Template Rendering
```python
if not email_text or not email_text.strip():
    raise ValueError("email_text cannot be empty")
```

### 3. Log Generated Prompts (Development Only)
```python
logger.debug(f"Generated prompt: {user_prompt[:200]}...")
```

### 4. Handle None Values Gracefully
All templates use Jinja2 conditionals to skip None parameters.

### 5. Keep Templates Focused
Each template should have a single, clear purpose.

---

## Environment Configuration

Templates respect these environment variables:

```bash
# OpenAI Settings
MODEL_NAME=gpt-4                # Which model to use
MAX_TOKENS=2000                 # Maximum response length
TEMPERATURE=0.7                 # Creativity level (0.0-1.0)
OPENAI_API_KEY=sk-...           # Your API key
```

---

## Troubleshooting

### Issue: Prompt too long
**Solution**: Reduce `email_text` length or adjust `MAX_TOKENS`

### Issue: Template rendering error
**Solution**: Check that all required parameters are provided

### Issue: Unexpected output
**Solution**: Review generated prompt with `logger.debug()` to see what OpenAI received

---

## Future Enhancements

Potential additions to the template system:

1. **Multi-language support**: Templates in different languages
2. **Industry-specific templates**: Legal, medical, technical writing
3. **Style guides**: Templates for different company style guides
4. **Sentiment adjustment**: Templates for changing email sentiment
5. **Formality levels**: More granular tone control

---

## Related Documentation

- [README.md](README.md) - Main project documentation
- [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) - Deployment instructions
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Official Jinja2 docs

---

**Last Updated**: 2025-01-11  
**Version**: 1.0.0
