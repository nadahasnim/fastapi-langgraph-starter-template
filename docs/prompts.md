# Prompts

## Prompt Organization

Prompts are stored in agent-specific `prompts/` directories:

```
app/agents/
  orchestrator/
    prompts/
      system.md
      router.md
  rag_agent/
    prompts/
      system.md
  tool_agent/
    prompts/
      system.md
```

## Loading Prompts

Use `PromptLoader` to load and render prompts:

```python
from pathlib import Path
from app.agents.shared.prompt_loader import PromptLoader

loader = PromptLoader(Path(__file__).parent / "prompts")
system_prompt = loader.render("system.md", {})
```

## Prompt Templates

Prompts support Jinja2 templating:

```markdown
# System Prompt

You are a helpful assistant for {{company_name}}.

## Context

{{context}}

## Instructions

{{instructions}}
```

Render with variables:

```python
prompt = loader.render("system.md", {
    "company_name": "Acme Corp",
    "context": "Customer support",
    "instructions": "Be concise"
})
```

## Best Practices

1. **Use markdown** - Clear structure and formatting
2. **Separate concerns** - System, user, and router prompts
3. **Version control** - Track prompt changes in git
4. **Test prompts** - Evaluate prompt effectiveness
5. **Document variables** - List required template variables
6. **Keep focused** - One purpose per prompt
7. **Use examples** - Include few-shot examples when helpful

## Example Prompts

### System Prompt

```markdown
# Generic Card Assistant

You are an AI assistant that helps users create generic cards.

## Guidelines

- Be concise and clear
- Focus on the user's request
- Provide structured output
- Validate input before processing

## Output Format

Return responses in this format:
- Title: [card title]
- Content: [card content]
- Metadata: [relevant metadata]
```

### Router Prompt

```markdown
# Request Router

Analyze the user's request and determine the appropriate agent.

## Available Agents

- **rag**: Questions about documents or knowledge base
- **tool**: Requests to use tools or perform actions
- **generic_card**: Requests to create generic cards
- **direct**: General questions or conversation

## Instructions

Return only the agent name, nothing else.
```

### Few-Shot Prompt

```markdown
# Generic Artifact Generator

Generate generic artifacts based on user requests.

## Examples

User: Create a generic artifact for project planning
Assistant: [artifact with project planning structure]

User: Generate a generic artifact for data analysis
Assistant: [artifact with data analysis structure]

## Your Task

{{user_request}}
```

## Prompt Engineering Tips

1. **Be specific** - Clear instructions yield better results
2. **Use structure** - Headers, lists, and formatting help
3. **Provide context** - Background information improves accuracy
4. **Set constraints** - Define boundaries and limitations
5. **Include examples** - Show desired output format
6. **Test variations** - Iterate on prompt wording
7. **Measure performance** - Use evals to track quality
