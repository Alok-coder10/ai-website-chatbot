from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Generate the complete response
        """
        pass

    
    @abstractmethod
    async def stream_generate(self, prompt:str):
        """
        Async generator.
        Yields small text chunks.
        """
        pass