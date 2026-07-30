from pathlib import Path

from agents.base import AgentResponse, CodingAgent


class MockAgent(CodingAgent):
    def __init__(self, solution_directory: Path):
        self.solution_directory = solution_directory

    def generate(self, prompt: str) -> AgentResponse:
        raise RuntimeError(
            "MockAgent requires a task-specific generate_for_task method."
        )

    def generate_for_task(self, task_id: str) -> AgentResponse:
        solution_path = self.solution_directory / f"{task_id}.py"

        if not solution_path.exists():
            raise FileNotFoundError(
                f"No mock solution found for {task_id}"
            )

        return AgentResponse(
            text=solution_path.read_text(encoding="utf-8"),
            model="mock-agent",
            condition="one_shot",
        )
