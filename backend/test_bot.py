from services.bot import chat
from services.Firebase_memory import get_recent_messages
from services.chroma_memory import ChromaMemory

USER_ID = "test_user"
chroma = ChromaMemory()  # init Chroma client

def run_test():
    # 1. Simulate conversation
    user_message = "what am i learning currrently?"
    print(f"User: {user_message}")

    bot_reply = chat(USER_ID, user_message)
    print(f"Bot: {bot_reply}\n")

    # 2. Show recent messages from Firestore
    print("📌 Firestore (recent messages):")
    recent = get_recent_messages(USER_ID)
    for msg in recent:
        print(f"{msg['role']}: {msg['content']}")

    # 3. Show semantic recall from Chroma
    print("\n📌 Chroma (semantic search):")
    results = chroma.search(query=user_message, n_results=3, user_id=USER_ID)

    if results and "documents" in results:
        docs = results["documents"][0]  # documents come nested in a list
        for d in docs:
            print(f"- {d}")

if __name__ == "__main__":
    run_test()
