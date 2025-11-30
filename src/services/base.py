from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class EmailServiceInterface(ABC):
    @abstractmethod
    async def rewrite_email(
        self,
        email_text: str,
        target_audience: str,
        tone: str = "professional",
        focus_areas: Optional[List[str]] = None,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Abstract method for email rewriting"""
        pass
