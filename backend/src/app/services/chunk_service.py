class ChunkService:
    CHUNK_SIZE = 700
    OVERLAP = 150

    def split(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            chunk = text[start:end]
            chunks.append(chunk)
            start += (self.CHUNK_SIZE - self.OVERLAP)
        
        return chunks
