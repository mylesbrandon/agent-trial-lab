from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentResponse:
    text: str
    model: str
    condition: str


class CodingAgent(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> AgentResponse:
        """Generate a candidate solution from a benchmark prompt."""
        raise NotImplementedError
