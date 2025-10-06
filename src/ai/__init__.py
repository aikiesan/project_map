"""
CP2B Maps - AI Integration Module
Bagacinho AI Assistant with RAG and Gemini
"""

from src.ai.bagacinho_rag import BagacinhoRAG
from src.ai.gemini_integration import (
    GeminiAssistant,
    query_gemini,
    check_gemini_connection,
    HAS_GEMINI
)

__all__ = [
    'BagacinhoRAG',
    'GeminiAssistant',
    'query_gemini',
    'check_gemini_connection',
    'HAS_GEMINI'
]
