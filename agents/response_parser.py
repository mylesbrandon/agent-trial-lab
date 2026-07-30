import re


_CODE_FENCE_PATTERN = re.compile(
    r"```(?:python)?\s*(.*?)```",
    flags=re.DOTALL | re.IGNORECASE,
)


def extract_python_source(response: str) -> str:
    """Extract exactly one syntactically valid Python candidate."""
    text = response.strip()

    fenced_blocks = _CODE_FENCE_PATTERN.findall(text)

    if fenced_blocks:
        if len(fenced_blocks) > 1:
            raise ValueError(
                "Response contained multiple code blocks; "
                "cannot determine the intended solution."
            )

        text = fenced_blocks[0].strip()

    if not text:
        raise ValueError("Model response did not contain code.")

    try:
        compile(text, "<candidate>", "exec")
    except SyntaxError as exc:
        raise ValueError(
            f"Extracted candidate is not valid Python: {exc}"
        ) from exc

    return text + "\n"
