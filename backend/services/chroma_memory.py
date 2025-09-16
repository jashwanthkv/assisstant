import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid


class ChromaMemory:
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "notes"):
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(allow_reset=True)
        )

        # Load embedding model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Create or get collection
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def _embed(self, text: str):
        """Generate embedding for a given text"""
        return self.embedder.encode([text])[0].tolist()

    def _find_by_topic(self, user_id: str, topic: str):
        """Find existing note by topic for a given user"""
        results = self.collection.query(
            query_embeddings=[self._embed(topic)],  # semantic lookup on topic
            n_results=1,
            where={
                "$and": [
                    {"user_id": user_id},
                    {"topic": topic}
                ]
            }
        )

        if results["ids"] and results["ids"][0]:
            return {
                "id": results["ids"][0][0],
                "note": results["documents"][0][0],
                "metadata": results["metadatas"][0][0]
            }
        return None

    def add_note(self, user_id: str, note: str, topic: str, metadata: dict = None):
        """
        Store or update a note grouped by topic.
        - User MUST provide topic.
        - If topic already exists → append (concatenate) new note.
        """
        if not topic:
            raise ValueError("Topic is required to add a note.")

        existing = self._find_by_topic(user_id, topic)

        if existing:
            # Concatenate new note to old
            updated_note = existing["note"] + " " + note
            self.collection.update(
                ids=[existing["id"]],
                embeddings=[self._embed(updated_note)],
                documents=[updated_note],
                metadatas=[existing["metadata"]]  # keep same metadata
            )
            return existing["id"]
        else:
            # Create new entry
            doc_id = str(uuid.uuid4())
            meta = {"user_id": user_id, "topic": topic}
            if metadata:
                meta.update(metadata)

            self.collection.add(
                ids=[doc_id],
                embeddings=[self._embed(note)],
                documents=[note],
                metadatas=[meta]
            )
            return doc_id

    def search_notes(self, query: str, n_results: int = 5, user_id: str = None):
        """
        Semantic search for a given query.
        Returns ONLY the single best note as context, plus metadata.
        {
            "context": str,          # top note only
            "topic": str,            # topic from the top note (or "unknown")
            "matches": [ ... ]       # other hits from the SAME topic; if topic unknown -> just the top hit
        }
        """
        filters = {"user_id": user_id} if user_id else None
        results = self.collection.query(
            query_embeddings=[self._embed(query)],
            n_results=n_results,
            where=filters
        )

        # no hits
        if not results or not results.get("ids") or not results["ids"][0]:
            return None

        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        scores = results.get("distances", [[]])[0]

        matches = []
        for i in range(len(ids)):
            matches.append({
                "id": ids[i],
                "note": docs[i],
                "metadata": metas[i] if i < len(metas) and metas[i] else {},
                "score": scores[i] if i < len(scores) else None,
            })

        # top match only
        top = matches[0]
        top_topic = top["metadata"].get("topic", "unknown")

        # keep other hits ONLY if they share the same topic; if topic unknown -> don't merge others
        if top_topic != "unknown":
            same_topic_matches = [m for m in matches if m["metadata"].get("topic") == top_topic]
        else:
            same_topic_matches = [top]

        return {
            "context": top["note"],  # <= single best note
            "topic": top_topic,
            "matches": same_topic_matches
        }

    def delete(self, doc_id: str):
        """Delete a note by its ID"""
        self.collection.delete(ids=[doc_id])

    def clear(self):
        """Clear all stored notes"""
        self.collection.delete(where={})

    def debug_all_notes(self, user_id: str = None, limit: int = 20):
        """
        Fetch all raw notes stored in Chroma for inspection.
        If user_id is provided → filter by that user.
        """
        filters = {"user_id": user_id} if user_id else None

        results = self.collection.get(
            where=filters,
            include=["documents", "metadatas"],
            limit=limit
        )

        # Make it easier to read
        formatted = []
        for i in range(len(results["ids"])):
            formatted.append({
                "id": results["ids"][i],
                "note": results["documents"][i],
                "metadata": results["metadatas"][i]
            })

        return formatted

