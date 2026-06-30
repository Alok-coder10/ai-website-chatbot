from app.llm.factory import get_llm_provider
from app.services.conversation_service import ConversationService
from app.services.summary_service import SummaryService
from app.services.memory_service import MemoryService
from app.embeddings.embedder import Embedder

class AssistantService:
    MAX_HISTORY = 10
    SUMMARY_TRIGGER = 20

    def __init__(self):
        self.provider = get_llm_provider()
        self.conversation_service = ConversationService()
        self.summary_service = SummaryService()
        self.memory_service = MemoryService()
        self.embedder = Embedder()

    async def chat(self, db, message, conversation_id=None):
        if conversation_id is None:
            conversation = (
                await self.conversation_service.create_conversation(
                    db,
                    "New Chat"
                )
            )
            conversation_id = conversation.id

        await self.conversation_service.save_message(
            db, conversation_id, "user", message
        )

        embedding = self.embedder.encode(message)
        await self.memory_service.save_memory(
            db, conversation_id, message, embedding
        )

        messages = await self.conversation_service.get_messages(
            db, conversation_id
        )

        summary = await self.summary_service.get_summary(
            db, conversation_id
        )

        memories = await self.memory_service.get_memories(db, conversation_id)

        memory_text = ""
        for m in memories[-5:]:
            memory_text += (m.content + "\n")

        if summary:
            summary_text = summary.content
        else:
            summary_text = ""

        if len(messages) >= self.SUMMARY_TRIGGER:
            old_messages = messages[:-self.MAX_HISTORY]

            history = ""
            for m in old_messages:
                history += (
                    f"{m.role}: {m.content}\n"
                )

            summary_prompt = f"""
            Summarize this conversation.
            Keep important facts only.
            Names
            preferences
            personal details
            tasks
            projects
            context
            Conversation:
            {history}
            """

            compressed = await self.provider.generate(
                prompt=summary_prompt
            )

            if summary:
                summary.content = compressed
                await db.commit()
            else:
                await self.summary_service.save_summary(
                    db,
                    conversation_id,
                    compressed

                )

            summary_text = compressed

        recent = messages[-self.MAX_HISTORY:]
        context = ""
        for m in recent:
            context += (
                f"{m.role}: {m.content}\n"
            )

        prompt = f"""
        Summary:
        {summary_text}

        Relevent memories:
        {memory_text}

        Recent conversation:
        {context}

        Current message:
        {message}


        Answer naturally.
        Use summary as long-term memory.
        Use memories for personal facts.
        Use recent conversation for context.
        Do not day "according to summary".
        Respond conversationally.
        """

        response = await self.provider.generate(
            prompt=prompt
        )

        await self.conversation_service.save_message(
            db,
            conversation_id,
            "assistant",
            response
        )

        return {
            "conversation_id": conversation_id,
            "response": response
        }

