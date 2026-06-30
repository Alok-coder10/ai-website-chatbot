from sentence_transformers import SentenceTransformer

class Embedder:
    _model = None
    def __init__(self):
        if Embedder._model is None:
            Embedder._model = SentenceTransformer("all-MiniLM-L6-v2")
        self.model = Embedder._model

    def encode(self, text):
        return self.model.encode(text).tolist()
