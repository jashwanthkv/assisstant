from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from flask import Flask, request, jsonify
from services.Firebase_memory import FirebaseMemory
from services.chroma_memory import ChromaMemory
from services.llm_service import ask_llm, forRag
from datetime import datetime
from flask_cors import CORS

CHROMA_DB_DIR = "./chromas_db"
db = Chroma(persist_directory=CHROMA_DB_DIR)
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
persist_directory = r"C:\Users\HP\PycharmProjects\MyAssiss\.venv\backend\routes\chromas_db"

db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_function
)

app = Flask(__name__)
CORS(app)
ch = ChromaMemory()
f = FirebaseMemory()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("message")
    date = data.get("date") or datetime.now().strftime("%Y-%m-%d")

    # ✅ If user explicitly asks for past convo (date+topic)
    if data.get("date") and data.get("topic"):
        conversation = f.get_conversation(user_id, data["date"], data["topic"])
        return jsonify({
            "source": "firebase",
            "conversation": conversation
        })

    # ✅ Otherwise: semantic search in Chroma
    semantic_results = ch.search_notes(query=user_message, user_id=user_id)

    if not semantic_results:
        return jsonify({"error": "No related notes found"}), 404

    # semantic_results contains context + topic from Chroma
    semantic_context = semantic_results["context"]
    detected_topic = semantic_results["topic"]   # 👈 topic comes from Chroma, not user

    # LLM generates response
    llm_response = ask_llm(semantic_context, user_message)

    # ✅ Store in Firebase under detected topic
    f.add_message(user_id, detected_topic, f"USER: {user_message}")
    f.add_message(user_id, detected_topic, f"BOT: {llm_response}")

    return jsonify({
        "source": "chroma",
        "detected_topic": detected_topic,
        "retrieved_notes": semantic_context,
        "llm_response": llm_response
    })


@app.route("/add_note", methods=["POST"])
def add_note():
    data = request.get_json()
    user_id = data.get("user_id")
    note = data.get("note")
    topic = data.get("topic")

    if not note:
        return jsonify({"error": "Note cannot be empty"}), 400
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    # ✅ Only stored in Chroma
    ch.add_note(user_id=user_id, note=note, topic=topic)

    return jsonify({"message": f"Note added under topic '{topic}' successfully"})

@app.route("/debug/notes", methods=["GET"])
def debug_notes():
    user_id = request.args.get("user_id")  # optional filter
    all_notes = ch.debug_all_notes(user_id=user_id)
    return jsonify(all_notes)

    return jsonify(results)




@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        answer = forRag(question, db)  # ✅ call your RAG function
        return jsonify({"question": question, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/rag", methods=["POST"])
def rag_endpoint():
    try:
        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "Missing 'question' in request"}), 400

        # call your forRag function
        response = forRag(question, db)

        return jsonify({"answer": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)
