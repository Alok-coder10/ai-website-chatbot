from app.embeddings.model_loader import get_model

class Embedder:
    def __init__(self):
        self.model = get_model()

    def encode(self, text):
        return self.model.encode(text).tolist()