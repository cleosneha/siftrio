from langchain_core.messages import HumanMessage

from src.agents.prompts import ANSWER_PROMPT
from src.agents.services.llm import LLMService
from src.agents.state import ChatState
from src.agents.utils.citations import extract_citations


def _message_content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


async def generate_response(
    state: ChatState,
    llm: LLMService,
) -> dict[str, object]:
    question = state["question"]
    context = state["context"] or ""
    prompt = ANSWER_PROMPT.format(context=context, question=question)

    response = await llm.invoke([HumanMessage(content=prompt)])
    answer = _message_content_to_text(response.content)
    citations = extract_citations(
        answer,
        state["retrieved_chunks"],
        state["meeting_analysis"],
        state["knowledge_entities"],
    )

    return {
        "answer": answer,
        "citations": citations,
    }