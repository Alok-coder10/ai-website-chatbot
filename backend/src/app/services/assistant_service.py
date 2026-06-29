from app.llm.factory import get_llm_provider
from app.services.conversation_service import ConversationService


conversation_service = ConversationService()

class AssistantService:

    def __init__(self):
        self.provider = get_llm_provider()
        self.conversation_service = ConversationService()

    async def chat(self, db, message, conversation_id=None):
        if conversation_id is None:
            conversation = (
                await self.conversation_service.create_conversation(
                    db, "New Chat"
                )
            )
            conversation_id = conversation.id
        
        await self.conversation_service.save_message(
            db, conversation_id, "user", message
        )
        messages = await conversation_service.get_messages(db, conversation_id)
        context = ""
        for m in messages:
            context += f"{m.role}: {m.content}\n"

        context += f"user: {message}" 
        response = await self.provider.generate(
            prompt = f"""Previous conversation:{context}
                        Current message:{message}
                        Answer using the previous conversation.
                        """
        )

        await self.conversation_service.save_message(
            db, conversation_id, "assistant", response
        )

        return {
            "conversation_id": conversation_id,
            "response": response
        }