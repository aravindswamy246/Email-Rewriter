"""
Email Rewriter Prompt Templates using Jinja2

This module provides structured, maintainable prompt templates for email rewriting
using Jinja2 templating engine. This approach offers:
- Better prompt organization and reusability
- Dynamic content insertion
- Conditional logic based on context
- Easier testing and maintenance
"""

from jinja2 import Environment, Template
from typing import Optional, List, Dict


class PromptTemplates:
    """
    Centralized prompt template management using Jinja2.

    Provides structured templates for different email rewriting scenarios
    with support for variables, conditions, and formatting.
    """

    def __init__(self):
        """Initialize Jinja2 environment with custom settings."""
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

    @staticmethod
    def get_base_system_prompt() -> str:
        """
        Get the base system prompt that defines the AI's role and capabilities.

        Returns:
            str: System prompt defining the AI assistant's role
        """
        template = Template("""
You are an expert professional email writer and communication specialist with deep expertise in:
- Corporate communication best practices
- Tone and style adaptation for different audiences
- Clear, concise, and effective writing
- Professional email etiquette and formatting

Your role is to rewrite emails to make them more effective, professional, and tailored to the target audience while maintaining the original intent and key information.
""")
        return template.render().strip()

    def get_email_rewrite_prompt(
        self,
        email_text: str,
        target_audience: str,
        tone: str = "professional",
        additional_instructions: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        constraints: Optional[Dict[str, any]] = None
    ) -> str:
        """
        Generate a comprehensive email rewriting prompt using Jinja2 template.

        Args:
            email_text: Original email content to be rewritten
            target_audience: Description of the target audience or context
            tone: Desired tone (professional, casual, academic, etc.)
            additional_instructions: Optional specific instructions
            focus_areas: List of areas to emphasize (e.g., ["achievements", "technical skills"])
            constraints: Dictionary of constraints (e.g., max_length, must_include)

        Returns:
            str: Formatted prompt ready for the AI model
        """
        template = Template("""
## Task: Rewrite Professional Email

### Original Email:
```
{{ email_text }}
```

### Target Audience/Context:
{{ target_audience }}

### Tone Requirement:
{{ tone|capitalize }} tone - {% if tone == "professional" %}formal, respectful, and business-appropriate
{% elif tone == "casual" %}friendly, approachable, and conversational
{% elif tone == "academic" %}scholarly, precise, and well-structured
{% else %}balanced and appropriate for the context
{% endif %}

{% if focus_areas %}
### Key Focus Areas:
{% for area in focus_areas %}
- Emphasize {{ area }}
{% endfor %}
{% endif %}

{% if constraints %}
### Constraints:
{% if constraints.max_length %}
- Maximum length: {{ constraints.max_length }} words
{% endif %}
{% if constraints.must_include %}
- Must include: {{ constraints.must_include|join(', ') }}
{% endif %}
{% if constraints.avoid %}
- Avoid: {{ constraints.avoid|join(', ') }}
{% endif %}
{% endif %}

{% if additional_instructions %}
### Additional Instructions:
{{ additional_instructions }}
{% endif %}

### Guidelines:
1. Maintain the core message and intent of the original email
2. Improve clarity, conciseness, and readability
3. Ensure appropriate greeting and closing
4. Use proper email structure with clear paragraphs
5. Adapt language and terminology for the target audience
6. Remove redundancy and filler words
7. Ensure professional formatting and grammar

### Output Format:
Provide only the rewritten email content without any explanations, comments, or metadata. The output should be ready to send as-is.
""")

        return template.render(
            email_text=email_text,
            target_audience=target_audience,
            tone=tone,
            additional_instructions=additional_instructions,
            focus_areas=focus_areas or [],
            constraints=constraints or {}
        ).strip()

    def get_job_application_email_prompt(
        self,
        email_text: str,
        job_description: str,
        company_name: Optional[str] = None,
        key_qualifications: Optional[List[str]] = None
    ) -> str:
        """
        Specialized prompt for job application emails.

        Args:
            email_text: Original email/cover letter content
            job_description: Full job description or key requirements
            company_name: Name of the company (if known)
            key_qualifications: List of key qualifications to highlight

        Returns:
            str: Formatted prompt for job application email rewriting
        """
        template = Template("""
## Task: Craft Professional Job Application Email

### Original Content:
```
{{ email_text }}
```

### Job Description/Requirements:
```
{{ job_description }}
```

{% if company_name %}
### Company: {{ company_name }}
{% endif %}

{% if key_qualifications %}
### Key Qualifications to Highlight:
{% for qual in key_qualifications %}
- {{ qual }}
{% endfor %}
{% endif %}

### Rewriting Guidelines:
1. **Opening**: Create a compelling opening that grabs attention
2. **Relevance**: Directly address how your skills match the job requirements
3. **Achievements**: Highlight specific, quantifiable achievements
4. **Value Proposition**: Clearly articulate what you bring to the role
5. **Call to Action**: End with a clear next step
6. **Professional Tone**: Maintain confident but respectful language
7. **Conciseness**: Keep it focused and concise (ideally 200-300 words)

### Structure:
- Professional greeting
- Strong opening statement
- 2-3 paragraphs highlighting relevant experience and skills
- Closing with call to action
- Professional sign-off

### Output:
Provide the complete, polished job application email ready to send.
""")

        return template.render(
            email_text=email_text,
            job_description=job_description,
            company_name=company_name,
            key_qualifications=key_qualifications or []
        ).strip()

    def get_follow_up_email_prompt(
        self,
        email_text: str,
        context: str,
        tone: str = "professional"
    ) -> str:
        """
        Generate prompt for follow-up emails.

        Args:
            email_text: Original follow-up email draft
            context: Context about previous communication
            tone: Desired tone

        Returns:
            str: Formatted prompt for follow-up email
        """
        template = Template("""
## Task: Craft Effective Follow-Up Email

### Original Draft:
```
{{ email_text }}
```

### Context/Previous Communication:
{{ context }}

### Tone: {{ tone|capitalize }}

### Follow-Up Best Practices:
1. **Reference Previous Communication**: Clearly reference the original conversation/email
2. **State Purpose**: Be clear about why you're following up
3. **Add Value**: Provide additional information or clarification if relevant
4. **Be Concise**: Respect the recipient's time
5. **Clear Ask**: Make any requests or next steps explicit
6. **Professional Persistence**: Be persistent but not pushy
7. **Timing Acknowledgment**: Acknowledge appropriate timing

### Output:
Provide the complete, polished follow-up email.
""")

        return template.render(
            email_text=email_text,
            context=context,
            tone=tone
        ).strip()

    def get_email_summary_prompt(self, email_text: str) -> str:
        """
        Generate prompt for email summarization.

        Args:
            email_text: Email content to summarize

        Returns:
            str: Formatted prompt for summarization
        """
        template = Template("""
## Task: Summarize Email Content

### Email to Summarize:
```
{{ email_text }}
```

### Summarization Requirements:
1. Extract key points and main message
2. Identify action items if any
3. Note important dates or deadlines
4. Highlight any requests or questions
5. Keep summary concise (2-3 sentences for short emails, 1 paragraph for long ones)

### Output Format:
**Summary:** [Main message]
**Action Items:** [List if applicable, or "None"]
**Key Dates:** [List if applicable, or "None"]
""")

        return template.render(email_text=email_text).strip()

    def get_batch_processing_prompt(
        self,
        email_texts: List[str],
        common_context: str,
        tone: str = "professional"
    ) -> str:
        """
        Generate prompt for batch email processing.

        Args:
            email_texts: List of email contents to process
            common_context: Common context for all emails
            tone: Desired tone

        Returns:
            str: Formatted prompt for batch processing
        """
        template = Template("""
## Task: Batch Process Multiple Emails

### Common Context/Audience:
{{ common_context }}

### Tone: {{ tone|capitalize }}

### Emails to Process:

{% for email in email_texts %}
#### Email {{ loop.index }}:
```
{{ email }}
```

{% endfor %}

### Instructions:
1. Rewrite each email according to the common context and tone
2. Maintain consistency across all emails
3. Number each rewritten email clearly
4. Ensure each email is complete and ready to send

### Output Format:
For each email, provide:

**Rewritten Email {{ loop.index }}:**
[Complete rewritten content]

---
""")

        return template.render(
            email_texts=email_texts,
            common_context=common_context,
            tone=tone
        ).strip()


# Singleton instance for easy import
prompt_templates = PromptTemplates()
