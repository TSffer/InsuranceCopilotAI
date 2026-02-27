import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from sqlalchemy.orm import selectinload

from ..domain.models import ChatThread, ChatMessage, User
from ..domain.schemas import ThreadCreate, ThreadUpdate, MessageCreate

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_thread(self, user_id: int, title: str) -> ChatThread:
        new_thread = ChatThread(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title
        )
        self.db.add(new_thread)
        await self.db.commit()
        
        result = await self.db.execute(
            select(ChatThread)
            .where(ChatThread.id == new_thread.id)
            .options(selectinload(ChatThread.messages))
        )
        return result.scalars().one()

    async def get_user_threads(self, user_id: int) -> list[ChatThread]:
        result = await self.db.execute(
            select(ChatThread)
            .where(ChatThread.user_id == user_id)
            .order_by(desc(ChatThread.updated_at))
            .options(selectinload(ChatThread.messages))
        )
        return result.scalars().all()

    async def get_thread(self, thread_id: str, user_id: int) -> ChatThread | None:
        result = await self.db.execute(
            select(ChatThread)
            .where(ChatThread.id == thread_id, ChatThread.user_id == user_id)
            .options(selectinload(ChatThread.messages))
        )
        return result.scalars().first()
    
    async def update_thread(self, thread_id: str, user_id: int, thread_update: ThreadUpdate) -> ChatThread | None:
        thread = await self.get_thread(thread_id, user_id)
        if thread:
            thread.title = thread_update.title
            await self.db.commit()

            return await self.get_thread(thread_id, user_id)
        return thread

    async def delete_thread(self, thread_id: str, user_id: int) -> bool:
        thread = await self.get_thread(thread_id, user_id)
        if thread:
            await self.db.delete(thread)
            await self.db.commit()
            return True
        return False

    async def save_message(self, thread_id: str, role: str, content: str, metadata: dict = None) -> ChatMessage:
        new_msg = ChatMessage(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            role=role,
            content=content,
            metadata_json=metadata
        )
        self.db.add(new_msg)
        
        thread_result = await self.db.execute(select(ChatThread).where(ChatThread.id == thread_id))
        thread = thread_result.scalars().first()
        if thread:
             pass 
        
        await self.db.commit()
        await self.db.refresh(new_msg)
        return new_msg

    async def get_thread_messages(self, thread_id: str) -> list[ChatMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at)
        )
        return result.scalars().all()
