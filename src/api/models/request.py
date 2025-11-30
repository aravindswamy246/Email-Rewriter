from pydantic import BaseModel, Field, field_validator
from .shared import ToneEnum
from typing import Optional
import re
import uuid


class EmailRewriteRequest(BaseModel):
    """
    Request model for email rewriting with validation
    """
    email_text: str = Field(
        ...,  # Required field
        min_length=30,  # Reduced from 100 - allows ~10 words minimum
        max_length=5000,
        description="The email text to be rewritten (minimum 10 words)"
    )

    target_audience: str = Field(
        ...,
        min_length=10,  # Reduced from 25 - allows ~3-4 words minimum
        max_length=2000,
        description="The context or audience for email rewriting (minimum 2 words)"
    )

    tone: ToneEnum = Field(
        default=ToneEnum.PROFESSIONAL,
        description="The tone to use in the rewritten email"
    )

    focus_areas: Optional[list[str]] = Field(
        default=None,
        description="List of areas to emphasize in the rewrite"
    )

    additional_instructions: Optional[str] = Field(
        default=None,
        description="Additional specific instructions for rewriting"
    )

    save_output: bool = Field(
        default=True,
        description="Whether to save the output to a file"
    )

    correlation_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Correlation ID for request tracking"
    )

    @field_validator('email_text')
    @classmethod
    def validate_email_text(cls, v: str) -> str:
        """Validate email text has meaningful content"""
        # Remove control characters
        v = re.sub(r'[\x00-\x1F\x7F]', '', v).strip()

        # Check for minimum word count
        word_count = len(v.split())
        if word_count < 10:
            raise ValueError(
                f"Email text must contain at least 10 words (found {word_count})")

        return v

    @field_validator('target_audience')
    @classmethod
    def validate_target_audience(cls, v: str) -> str:
        """Validate target audience has meaningful content"""
        # Remove control characters
        v = re.sub(r'[\x00-\x1F\x7F]', '', v).strip()

        # Check for minimum word count
        word_count = len(v.split())
        if word_count < 2:
            raise ValueError(
                f"Target audience must contain at least 2 words (found {word_count})")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email_text": "Hi, I wanted to reach out about the project status. Let me know when you have time to discuss the next steps and timeline.",
                    "target_audience": "C-level executives at Fortune 500 company",
                    "tone": "professional",
                    "focus_areas": ["brevity", "confidence"],
                    "additional_instructions": "Include a clear call-to-action",
                    "save_output": True
                },
                {
                    "email_text": "Hello, I am writing to apply for the Senior Python Developer position at your company. I have been coding in Python for 6 years and have experience with FastAPI, Django, and building REST APIs.",
                    "target_audience": "Netflix Engineering Manager",
                    "tone": "professional",
                    "save_output": False
                }
            ]
        }
    }
