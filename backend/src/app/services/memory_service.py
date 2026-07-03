import json
import math
import numpy as np
from sqlalchemy import select
from app.models.memory import Memory

class MemoryService:

    async def save_memory(self, db, conversation_id, content, embedding):
        memories = await self.get_memories(db, conversation_id)
        exists = any(
            m.content.lower() == content.lower()
            for m in memories
        )

        if exists:
            return None
        
        memory = Memory(
            conversation_id = conversation_id,
            content = content,
            embedding = json.dumps(embedding)
        )

        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        return memory


    async def get_memories(self, db, conversation_id):
        result = await db.execute(
            select(Memory).where(
                Memory.conversation_id == conversation_id
            )
        )

        return result.scalars().all()

    
    def cosine_similarity(self, a, b):
        dot = sum(x*y for x, y in zip(a,b))
        norm_a = math.sqrt(
            sum(
                x*x for x in a
            )
        )
        norm_b = math.sqrt(
            sum(
                x*x for x in b
            )
        )

        if norm_a == 0 or norm_b == 0:
            return 0
        
        return dot/(norm_a * norm_b)

# def cosine_similarity(a,b):
#     a=np.array(a)
#     b=np.array(b)

#     return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))
    async def search(
        self, db, conversation_id, query_embedding, top_k=3, threshold=0.70
    ):
        memories = await self.get_memories(db, conversation_id)

        scored = []
        for m in memories:
            emb = json.loads(m.embedding)
            score = self.cosine_similarity(query_embedding, emb)

            if score > threshold:
                scored.append((score, m))

            scored.sort(reverse=True, key= lambda x: x[0])

            return [x[1] for x in scored[:top_k]]
















    # async def save_memory(
    #         self,
    #         db,
    #         conversation_id,
    #         content,
    #         embedding
    # ):
    #     memory = Memory(
    #         conversation_id=conversation_id,
    #         content=content,
    #         embedding=json.dumps(
    #             embedding
    #         )
    #     )

    #     db.add(memory)
    #     await db.commit()
    #     await db.refresh(memory)
    #     return memory

    # async def get_memories(
    #         self,
    #         db,
    #         conversation_id
    # ):
    #     result = await db.execute(
    #         select(Memory).where(
    #             Memory.conversation_id == conversation_id
    #         )
    #     )
    #     return result.scalars().all()

    # def cosine_similarity(self, a, b):
    #     dot = sum(
    #         x*y
    #         for x,y in zip(a,b)
    #     )

    #     norm_a = math.sqrt(
    #         sum(
    #             x*x
    #             for x in a
    #         )
    #     )

    #     norm_b = math.sqrt(
    #         sum(
    #             x*x
    #             for x in b
    #         )
    #     )

    #     if norm_a == 0 or norm_b == 0:
    #         return 0

    #     return dot/(norm_a*norm_b)

    # async def search(
    #         self,
    #         db,
    #         conversation_id,
    #         query_embedding,
    #         top_k=5
    # ):
    #     memories = await self.get_memories(
    #         db,
    #         conversation_id
    #     )

    #     scored = []
    #     for m in memories:
    #         emb = json.loads(m.embedding)
    #         score = self.cosine_similarity(
    #             query_embedding,
    #             emb
    #         )

    #         scored.append(
    #             (
    #                 score, m
    #             )
    #         )

    #     scored.sort(
    #         reverse=True,
    #         key=lambda x:x[0]
    #     )

    #     return [
    #         x[1]
    #         for x in scored[:top_k]
    #     ]

