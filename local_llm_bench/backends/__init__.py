from .base import Backend, BackendResult
from .ollama import OllamaBackend
from .openai_compat import OpenAICompatibleBackend

__all__ = ["Backend", "BackendResult", "OllamaBackend", "OpenAICompatibleBackend"]
