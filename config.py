import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Discord
    DISCORD_BOT_TOKEN: str = os.environ.get("DISCORD_BOT_TOKEN", "")

    # OpenAI
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    AI_MODEL: str = os.environ.get("AI_MODEL", "gpt-4o")

    # 会話履歴設定（直近10メッセージまで保持）
    MAX_HISTORY_LENGTH: int = int(os.environ.get("MAX_HISTORY_LENGTH", "20"))

    # システムプロンプト
    SYSTEM_PROMPT: str = """あなたは親切で知識豊富なAIアシスタントです。
Discordサーバーでユーザーの質問に答えます。
- 簡潔で分かりやすい回答を心がけてください
- 日本語で回答してください
- コードを含む場合はマークダウン形式で整形してください
- 分からないことは正直に伝えてください"""

    @classmethod
    def validate(cls) -> List[str]:
        """必須の環境変数が設定されているか確認"""
        errors = []
        if not cls.DISCORD_BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN が設定されていません")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY が設定されていません")
        return errors
