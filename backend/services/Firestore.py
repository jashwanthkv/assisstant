import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

class FirestoreMemory:
    def __init__(self, project_id, collection="conversations", k=20):
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        self.db = firestore.client()
        self.collection = collection
        self.k = k

    def save_message(self, session_id, role, content):
        doc_ref = self.db.collection(self.collection).document(session_id)
        doc = doc_ref.get()

        if doc.exists:
            history = doc.to_dict().get("history", [])
        else:
            history = []

        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep only last K
        history = history[-self.k:]

        doc_ref.set({"history": history})

    def get_history(self, session_id):
        doc_ref = self.db.collection(self.collection).document(session_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("history", [])
        return []
