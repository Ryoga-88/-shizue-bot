import discord
from discord.ext import commands

from ai.openai_client import OpenAIClient
from storage.firestore_history import ConversationHistory


class MessageHandler(commands.Cog):
    """メッセージイベントを処理するCog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai_client = OpenAIClient()
        self.history = ConversationHistory()

    def _is_bot_mentioned(self, message: discord.Message) -> bool:
        """Botがメンションされているか確認（ユーザーメンション or ロールメンション）"""
        # ユーザーとして直接メンションされている
        if self.bot.user and self.bot.user in message.mentions:
            return True

        # Botが持っているロールがメンションされている
        if message.guild:
            bot_member = message.guild.get_member(self.bot.user.id)
            if bot_member:
                for role in message.role_mentions:
                    if role in bot_member.roles:
                        return True

        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """メッセージ受信時の処理"""
        print(f"[DEBUG] Message received: {message.content[:50]}...")

        # Bot自身のメッセージは無視
        if message.author.bot:
            print("[DEBUG] Ignored: bot message")
            return

        # Botがメンションされているか確認（ユーザー or ロール）
        if not self._is_bot_mentioned(message):
            print(f"[DEBUG] Ignored: not mentioned")
            return

        print(f"[DEBUG] Bot was mentioned! Processing...")

        # メンションを除去してメッセージを取得
        content = message.content
        # ユーザーメンションを除去
        for mention in message.mentions:
            content = content.replace(f"<@{mention.id}>", "")
            content = content.replace(f"<@!{mention.id}>", "")
        # ロールメンションを除去
        for role in message.role_mentions:
            content = content.replace(f"<@&{role.id}>", "")
        content = content.strip()

        # メッセージが空の場合
        if not content and not message.attachments:
            await message.reply("何か質問してください！")
            return

        # 処理中であることを示す
        async with message.channel.typing():
            try:
                # 画像URLを収集
                image_urls = []
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith("image/"):
                        image_urls.append(attachment.url)

                # 会話履歴を取得
                history = await self.history.get_history(
                    message.channel.id, message.author.id
                )

                # AIに問い合わせ
                response = await self.ai_client.chat(
                    user_message=content or "この画像について説明してください",
                    history=history,
                    image_urls=image_urls if image_urls else None,
                )

                # 会話履歴に追加
                await self.history.add_conversation(
                    channel_id=message.channel.id,
                    user_id=message.author.id,
                    user_message=content or "[画像]",
                    assistant_message=response,
                )

                # 応答を送信（2000文字制限対応）
                await self._send_response(message, response)

            except Exception as e:
                await message.reply(f"エラーが発生しました: {type(e).__name__}")
                import traceback
                print(f"Error processing message: {e}")
                traceback.print_exc()

    async def _send_response(self, message: discord.Message, response: str):
        """応答を送信（長い場合は分割）"""
        max_length = 2000

        if len(response) <= max_length:
            await message.reply(response)
            return

        # 長い応答は分割して送信
        chunks = []
        current_chunk = ""

        for line in response.split("\n"):
            if len(current_chunk) + len(line) + 1 > max_length:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += "\n" + line if current_chunk else line

        if current_chunk:
            chunks.append(current_chunk)

        # 最初のチャンクはリプライ、残りは通常メッセージ
        for i, chunk in enumerate(chunks):
            if i == 0:
                await message.reply(chunk)
            else:
                await message.channel.send(chunk)
