import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


class FirebaseMemory:
    def __init__(self, cred_path: str = r"C:\Users\HP\PycharmProjects\MyAssiss\.venv\backend\firebase-key.json"):
        # Initialize Firebase only once
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def add_message(self, user_id: str, topic: str, message: str, role: str = "user"):
        """
        Add a single message (user or bot) under user_id/date/topic.
        Avoids saving duplicates for same role & message within same date/topic.
        """
        if not message:
            return None

        date = datetime.now().strftime("%Y-%m-%d")
        messages_ref = (
            self.db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document(date)
            .collection("topics")
            .document(topic)
            .collection("messages")
        )

        # 🔍 Check if the same message already exists (role + message match)
        existing = (
            messages_ref.where("role", "==", role)
            .where("message", "==", message)
            .limit(1)
            .stream()
        )

        if any(existing):  # If found, skip saving
            print("⚠️ Duplicate message skipped:", message)
            return None

        # ✅ Add new unique message
        return messages_ref.add({
            "role": role,
            "message": message,
            "timestamp": datetime.now()
        })

    def get_conversation(self, user_id: str, date: str, topic: str):
        """
        Fetch all messages for a given user on a date & topic.
        """
        messages_ref = (
            self.db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document(date)
            .collection("topics")
            .document(topic)
            .collection("messages")
        )

        messages = messages_ref.order_by("timestamp").stream()
        return [
            {
                "role": m.get("role"),
                "message": m.get("message"),
                "timestamp": m.get("timestamp").isoformat() if m.get("timestamp") else None
            }
            for m in messages
        ]

    def list_topics(self, user_id: str, date: str):
        """
        List all topics discussed on a given date.
        """
        topics_ref = (
            self.db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document(date)
            .collection("topics")
        )

        topics = topics_ref.stream()
        return [t.id for t in topics]
