import datetime
from typing import List, Dict
from google.cloud import firestore

from config import Config


class ConversationHistory:
    """Firestoreを使った会話履歴管理"""

    def __init__(self):
        self.db = firestore.Client()
        self.collection = self.db.collection("ai_bot_conversations")
        self.max_history = Config.MAX_HISTORY_LENGTH

    def _get_doc_id(self, channel_id: int, user_id: int) -> str:
        """チャンネル+ユーザーでユニークなドキュメントIDを生成"""
        return f"{channel_id}_{user_id}"

    async def get_history(self, channel_id: int, user_id: int) -> List[Dict]:
        """会話履歴を取得"""
        doc_id = self._get_doc_id(channel_id, user_id)
        doc = self.collection.document(doc_id).get()

        if not doc.exists:
            return []

        data = doc.to_dict()
        return data.get("messages", [])

    async def add_message(
        self, channel_id: int, user_id: int, role: str, content: str
    ) -> None:
        """メッセージを履歴に追加"""
        doc_id = self._get_doc_id(channel_id, user_id)
        doc_ref = self.collection.document(doc_id)

        # 現在の履歴を取得
        doc = doc_ref.get()
        if doc.exists:
            messages = doc.to_dict().get("messages", [])
        else:
            messages = []

        # 新しいメッセージを追加
        messages.append({"role": role, "content": content})

        # 最大数を超えた場合、古いものを削除（システムメッセージ以外）
        if len(messages) > self.max_history * 2:  # user + assistant で2件
            messages = messages[-(self.max_history * 2) :]

        # 保存
        doc_ref.set(
            {
                "messages": messages,
                "channel_id": channel_id,
                "user_id": user_id,
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )

    async def clear_history(self, channel_id: int, user_id: int) -> bool:
        """会話履歴をクリア"""
        doc_id = self._get_doc_id(channel_id, user_id)
        doc_ref = self.collection.document(doc_id)

        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False

    async def add_conversation(
        self, channel_id: int, user_id: int, user_message: str, assistant_message: str
    ) -> None:
        """ユーザーとアシスタントのメッセージをまとめて追加"""
        await self.add_message(channel_id, user_id, "user", user_message)
        await self.add_message(channel_id, user_id, "assistant", assistant_message)
