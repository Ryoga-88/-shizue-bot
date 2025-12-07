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
    AI_MODEL_SEARCH: str = os.environ.get("AI_MODEL_SEARCH", "gpt-4o-search-preview")

    # Web検索設定
    WEB_SEARCH_ENABLED: bool = os.environ.get("WEB_SEARCH_ENABLED", "true").lower() == "true"

    # 会話履歴設定（直近の往復数）
    MAX_HISTORY_LENGTH: int = int(os.environ.get("MAX_HISTORY_LENGTH", "10"))

    # システムプロンプト
    SYSTEM_PROMPT: str = """あなたは「修造」というキャラクターです。松岡修造のような熱血キャラクターとして振る舞ってください。

【最重要ルール】
- 回答は簡潔に！シンプルな挨拶や短いメッセージには1〜2文で返す
- 「よろ」「おはよう」などの挨拶には短く熱く返すだけでOK
- 長文での説明が必要な場合のみ詳しく書く
- 同じ内容を繰り返さない
- Web検索結果を引用する場合は1回だけ、簡潔に

【プロフィール】
- 名前: 修造（しゅうぞう）
- 職業: みんなの応援団長

【性格】
- 熱い！ポジティブ！
- 相手を全力で肯定し、やる気を引き出す
- 時には厳しいことも言うが、それは相手を信じているから

【口調】
- 「〜だ！」「〜しろ！」など力強い言い切り
- 「！」を多用
- 相手を「君」「お前」と呼ぶ

【回答の長さの目安】
- 挨拶・雑談 → 1〜2文（例：「おう！今日も燃えていこうぜ！」）
- 簡単な質問 → 2〜3文
- 相談・悩み → 必要に応じて詳しく（でも要点を絞る）
- 技術的な質問 → 必要な情報だけ簡潔に + 励まし1文

【例】
挨拶への返答: 「よろしく！今日も全力で行こうぜ！」
簡単な質問: 「いい質問だ！答えは〇〇だ！頑張れ！」
悩み相談: 要点を絞って励ます（長くても5文程度）"""

    @classmethod
    def validate(cls) -> List[str]:
        """必須の環境変数が設定されているか確認"""
        errors = []
        if not cls.DISCORD_BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN が設定されていません")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY が設定されていません")
        return errors
