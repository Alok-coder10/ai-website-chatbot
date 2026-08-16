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


    @abstractmethod
    async def health_check(self) -> bool:
        pass

    @property
    def last_usage(self) -> dict:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }