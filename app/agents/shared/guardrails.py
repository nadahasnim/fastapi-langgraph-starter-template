MAX_TEXT_LENGTH = 8000

_PROMPT_LEAK_PATTERNS = (
    "ignore previous instructions",
    "reveal system prompt",
    "show system prompt",
    "print system prompt",
)


class GuardrailViolation(ValueError):
    pass


def validate_input_text(text: str) -> str:
    if not text.strip():
        raise GuardrailViolation("Input text must not be blank.")
    if len(text) > MAX_TEXT_LENGTH:
        raise GuardrailViolation("Input text exceeds maximum length.")

    normalized_text = text.lower()
    if any(pattern in normalized_text for pattern in _PROMPT_LEAK_PATTERNS):
        raise GuardrailViolation("Input text contains a blocked prompt-leak attempt.")

    return text


def validate_output_text(text: str) -> str:
    if not text.strip():
        raise GuardrailViolation("Output text must not be blank.")

    return text
