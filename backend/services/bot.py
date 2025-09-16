from services.Firebase_memory import store_message, get_recent_messages, keyword_search
from services.chroma_memory import ChromaMemory
from services.llm_service import ask_llm

ch = ChromaMemory()

def chat(user_id: str, user_message: str):
    # 1. Save user message
    store_message(user_id, "user", user_message)

    # 2. Try to fetch memory context
    context = ""

    # a. Get recent short-term msgs (for conversation flow)
    recent_msgs = get_recent_messages(user_id)
    for msg in recent_msgs:
        context += f"{msg['role']}: {msg['content']}\n"

    # b. Try keyword search in Firebase
    keyword_context = keyword_search(user_id, user_message)
    if keyword_context:
        context += "\n[Found in Firebase memory]\n"
        for kc in keyword_context:
            context += f"- {kc}\n"
    else:
        # c. If nothing found, fallback to Chroma
        semantic_context = ch.search(query=user_message, user_id=user_id)
        if semantic_context:
            context += "\n[Relevant past memories]\n"
            for sc in semantic_context:
                context += f"- {sc}\n"

    # 3. Ask LLM with the constructed context
    bot_response = ask_llm(context, user_message)

    # 4. Save bot response
    store_message(user_id, "bot", bot_response)

    return bot_response
