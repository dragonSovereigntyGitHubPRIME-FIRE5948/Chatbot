# firebase
import firebase_admin
from firebase_admin import firestore, credentials

class FirebaseDB:
    def __init__(self):
        # get credential
        self.cred = credentials.Certificate("")
        self.app = firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

# Use the application default credentials.
    # def get_or_create_collection(self, name: str):
    #     doc_ref = self.db.collection(name)
        
    def set_feedback(self, email: str, unanswered: str, feedback: str, rating: int):
        # create empty document
        # id will be auto generated and set as doc name
        doc_ref = self.db.collection("feedbacks").document()
        
        # set data in doc
        doc_ref.set(
            {   
                "id": doc_ref.id,
                "email": email,
                "unanswered": unanswered,
                "feedback": feedback,
                "rating": rating,
            }
        )
        return doc_ref.id