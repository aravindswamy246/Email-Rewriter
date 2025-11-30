"""
Email Rewriting Service with Jinja2-based Prompt Templates

This module provides the email rewriting service that uses OpenAI GPT models
with structured Jinja2 prompt templates for better prompt engineering.
"""

from .base import EmailServiceInterface
from typing import Optional, Dict, Any, List
import os
from openai import AsyncOpenAI
from utils.prompt_templates import prompt_templates


class EmailService(EmailServiceInterface):
    """
    Email rewriting service using OpenAI with Jinja2 prompt templates.

    Features:
    - Structured prompt templates using Jinja2
    - Support for different tones and contexts
    - Usage tracking and cost estimation
    - Async API calls for better performance
    """

    def __init__(self, client: Optional[AsyncOpenAI] = None):
        """
        Initialize service with optional OpenAI client.

        Args:
            client: Optional AsyncOpenAI client for dependency injection
        """
        self._client = client
        self.model = os.getenv('MODEL_NAME', 'gpt-4')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found in environment variables")
            self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    async def rewrite_email(
        self,
        email_text: str,
        target_audience: str,
        tone: str = "professional",
        focus_areas: Optional[List[str]] = None,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rewrite email using OpenAI with Jinja2-structured prompts.

        Args:
            email_text: Original email content
            target_audience: Description of target audience or context
            tone: Desired tone (professional, casual, academic)
            focus_areas: Optional list of areas to emphasize
            additional_instructions: Optional specific instructions

        Returns:
            Dict containing:
                - content: Rewritten email text
                - usage: Token usage statistics
                - model: Model used
        """
        # Generate structured prompt using Jinja2 templates
        system_prompt = prompt_templates.get_base_system_prompt()
        user_prompt = prompt_templates.get_email_rewrite_prompt(
            email_text=email_text,
            target_audience=target_audience,
            tone=tone,
            focus_areas=focus_areas,
            additional_instructions=additional_instructions
        )

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # Extract response and usage data
        rewritten_content = response.choices[0].message.content
        if not rewritten_content:
            raise ValueError("OpenAI returned empty response")
        rewritten_content = rewritten_content.strip()
        usage_data = response.usage
        if not usage_data:
            raise ValueError("OpenAI returned no usage data")

        # Calculate cost (approximate rates for GPT-4)
        input_cost_per_1k = 0.03  # $0.03 per 1K input tokens
        output_cost_per_1k = 0.06  # $0.06 per 1K output tokens

        input_cost = (usage_data.prompt_tokens / 1000) * input_cost_per_1k
        output_cost = (usage_data.completion_tokens / 1000) * \
            output_cost_per_1k
        total_cost = input_cost + output_cost

        return {
            "content": rewritten_content,
            "usage": {
                "total_tokens": usage_data.total_tokens,
                "input_tokens": usage_data.prompt_tokens,
                "output_tokens": usage_data.completion_tokens,
                "cost_usd": round(total_cost, 4)
            },
            "model": self.model
        }

    async def rewrite_job_application_email(
        self,
        email_text: str,
        job_description: str,
        company_name: Optional[str] = None,
        key_qualifications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Specialized method for job application emails.

        Args:
            email_text: Original email/cover letter
            job_description: Job posting or requirements
            company_name: Company name
            key_qualifications: Key qualifications to highlight

        Returns:
            Dict with rewritten content and usage statistics
        """
        system_prompt = prompt_templates.get_base_system_prompt()
        user_prompt = prompt_templates.get_job_application_email_prompt(
            email_text=email_text,
            job_description=job_description,
            company_name=company_name,
            key_qualifications=key_qualifications
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        rewritten_content = response.choices[0].message.content
        if not rewritten_content:
            raise ValueError("OpenAI returned empty response")
        rewritten_content = rewritten_content.strip()
        usage_data = response.usage
        if not usage_data:
            raise ValueError("OpenAI returned no usage data")

        # Calculate cost
        input_cost = (usage_data.prompt_tokens / 1000) * 0.03
        output_cost = (usage_data.completion_tokens / 1000) * 0.06

        return {
            "content": rewritten_content,
            "usage": {
                "total_tokens": usage_data.total_tokens,
                "input_tokens": usage_data.prompt_tokens,
                "output_tokens": usage_data.completion_tokens,
                "cost_usd": round(input_cost + output_cost, 4)
            },
            "model": self.model
        }
