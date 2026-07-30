from agents.base import AgentResponse, CodingAgent


class ManualAgent(CodingAgent):
    def __init__(self, model_name: str = "manual"):
        self.model_name = model_name

    def generate(self, prompt: str) -> AgentResponse:
        print(prompt)
        print("\nPaste the model response, then enter EOF.")
        print("macOS/Linux: Ctrl-D | Windows: Ctrl-Z then Enter\n")

        lines = []

        try:
            while True:
                lines.append(input())
        except EOFError:
            pass

        return AgentResponse(
            text="\n".join(lines),
            model=self.model_name,
            condition="one_shot",
        )
