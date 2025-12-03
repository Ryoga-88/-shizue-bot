import discord
from discord.ext import commands

from config import Config


def create_bot() -> commands.Bot:
    """Discord Botインスタンスを作成"""
    intents = discord.Intents.default()
    intents.message_content = True  # メッセージ内容を読む権限
    intents.guilds = True
    intents.members = True

    bot = commands.Bot(
        command_prefix="!",  # プレフィックスコマンド用（メインはスラッシュコマンド）
        intents=intents,
        help_command=None,  # デフォルトのhelpコマンドを無効化
    )

    return bot


async def setup_bot(bot: commands.Bot) -> None:
    """Botの初期設定を行う"""
    # コグ（機能モジュール）を読み込む
    from bot.events import MessageHandler
    from bot.commands import SlashCommands

    await bot.add_cog(MessageHandler(bot))
    await bot.add_cog(SlashCommands(bot))

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        print(f"Connected to {len(bot.guilds)} guilds")

        # スラッシュコマンドを同期
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        # ステータスを設定
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="@メンションで質問",
            )
        )
