from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

from ai.openai_client import OpenAIClient
from storage.firestore_history import ConversationHistory


class SlashCommands(commands.Cog):
    """スラッシュコマンドを処理するCog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai_client = OpenAIClient()
        self.history = ConversationHistory()

    @app_commands.command(name="ask", description="AIに質問します")
    @app_commands.describe(
        question="質問内容",
        image="画像を添付（任意）",
    )
    async def ask(
        self,
        interaction: discord.Interaction,
        question: str,
        image: Optional[discord.Attachment] = None,
    ):
        """AIに質問するスラッシュコマンド"""
        await interaction.response.defer(thinking=True)

        try:
            # 画像URLを取得
            image_urls = []
            if image and image.content_type and image.content_type.startswith("image/"):
                image_urls.append(image.url)

            # 会話履歴を取得
            history = await self.history.get_history(
                interaction.channel_id, interaction.user.id
            )

            # AIに問い合わせ
            response = await self.ai_client.chat(
                user_message=question,
                history=history,
                image_urls=image_urls if image_urls else None,
            )

            # 会話履歴に追加
            await self.history.add_conversation(
                channel_id=interaction.channel_id,
                user_id=interaction.user.id,
                user_message=question,
                assistant_message=response,
            )

            # 応答を送信
            await self._send_response(interaction, response)

        except Exception as e:
            await interaction.followup.send(f"エラーが発生しました: {type(e).__name__}")
            print(f"Error in /ask command: {e}")

    @app_commands.command(name="clear", description="会話履歴をクリアします")
    async def clear(self, interaction: discord.Interaction):
        """会話履歴をクリアするコマンド"""
        await interaction.response.defer(ephemeral=True)

        try:
            cleared = await self.history.clear_history(
                interaction.channel_id, interaction.user.id
            )

            if cleared:
                await interaction.followup.send(
                    "会話履歴をクリアしました！", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "クリアする履歴がありませんでした。", ephemeral=True
                )

        except Exception as e:
            await interaction.followup.send(
                f"エラーが発生しました: {type(e).__name__}", ephemeral=True
            )
            print(f"Error in /clear command: {e}")

    @app_commands.command(name="help", description="Botの使い方を表示します")
    async def help(self, interaction: discord.Interaction):
        """ヘルプコマンド"""
        embed = discord.Embed(
            title="AI Bot ヘルプ",
            description="AIに質問できるBotです！",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="メンションで質問",
            value="@Bot 質問内容\n画像を添付することもできます",
            inline=False,
        )

        embed.add_field(
            name="/ask",
            value="AIに質問します\n`/ask question:質問内容`",
            inline=False,
        )

        embed.add_field(
            name="/clear",
            value="会話履歴をクリアします\n新しい話題を始めたいときに使ってください",
            inline=False,
        )

        embed.add_field(
            name="/help",
            value="このヘルプを表示します",
            inline=False,
        )

        embed.set_footer(text="会話履歴はチャンネル×ユーザーごとに保存されます")

        await interaction.response.send_message(embed=embed)

    async def _send_response(self, interaction: discord.Interaction, response: str):
        """応答を送信（長い場合は分割）"""
        max_length = 2000

        if len(response) <= max_length:
            await interaction.followup.send(response)
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

        for chunk in chunks:
            await interaction.followup.send(chunk)
