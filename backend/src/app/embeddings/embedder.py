import random

class Embedder:
    def encode(self, text):
        return [
            random.random()
            for _ in range(
                128
            )
        ]
