import firebase_admin
from firebase_admin import credentials, firestore

# Path to the downloaded service account key
cred = credentials.Certificate("./firebase-key.json")

# Initialize Firebase app (singleton check to avoid reinit)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
