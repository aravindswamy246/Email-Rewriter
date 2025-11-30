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
        min_length=100,
        max_length=5000,
        description="The email text to be rewritten"
    )

    target_audience: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        description="The context or audience for email rewriting"
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

    @field_validator('email_text', 'target_audience')
    def validate_text_content(cls, v):
        """Validate text doesn't contain harmful content"""
        # Remove any control characters
        v = re.sub(r'[\x00-\x1F\x7F]', '', v)

        # Check for minimum word count
        if len(v.split()) < 10:
            raise ValueError("Text must contain at least 10 words")

        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email_text": "Enter your email content here, ensuring it has at least 10 words to pass validation.",
                "target_audience": "Enter your job description here, ensuring it has at least 10 words to pass validation.",
                "tone": "professional",
                "save_output": True
            }
        }
    }
