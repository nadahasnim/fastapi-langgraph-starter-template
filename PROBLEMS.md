# Background

We're just deployed to client's projects as a Fullstack dev. The project is about making custom agent that help assist the user to create somethings, fill forms, generate artifact, answer about data insights, etc.

## Specs

From those problems some things that we want to build are like this. Backend agentic python fastapi with Langgraph/Langchain as a agent framework. What we need now is to scaffold or make a project starter template with all the tech stacks setup, so every team in our company have same standards to built agent.

### Backend server goals

Here are some goals that we wanted in our backend service:

1. OpenAI supported endpoints, request response, with the capability of extending the response so we can add extension for our FE to consume, e.g: adding extra what component and params to render to the UI for rendering the journey map, and service card.
2. Observability, should easy to debug in production and development.
3. Structured pattern: routing, middleware, dependency injection, service, repository, pydantic request response DTO and validation.
4. DB using SQLAlchemy, alembic.
5. Easy to maintain, easy to test (pytest).

### Agent part goals

1. Use Langgraph/Langchain for agent framewrok.
2. Agent should be able to spin another agent (multi agent) so the orchestrator context window is not polluted.
3. Should be able to use tool calls, implement middleware, etc.
4. Should able to implement guardrails in input or output to sanitize/limit agent response to our needs.
5. Able to access knowledge base RAG like Qdrant or pgvector, because we will ingest many company/organizations docs for the agent knowledge.
6. Agent should smart enough to ask/guide the user information if the information is not enough, and able to route itself either deterministic/llm based natural language based to spin sub agents, make tool calls, etc, before making output.
7. Use Langfuse observability
8. Able to connect any LLMs with OpenAI standard.
9. There is the evaluation part that ease the developer and teams to evaluate the agent responses, either deterministic or llm based evaluation.
10. Able to access short term and long term memory, short term maybe like the current session chat context, and longterm maybe like accross different session history context for every users to personalized the user experience.
11. Team might be able to manage the system prompt using file based system prompts (the prompt builder), splitted to some parts.

### Some tech stacks in my mind right now

1. Python
2. uv
3. ruff
4. FastApi
5. Langgraph/Langchain
6. Langfuse
7. httpx
8. SQLAlchemy
9. Alembic
10. PostgreSQL
11. pgvector or Qdrant
12. Openrouter subscription token credits LLM
13. mem0 optional, still need further research
14. Any other package that help read yaml, json, or pdf docs, for ingesting the company/organization docs, rules, policy for knowledge based.
