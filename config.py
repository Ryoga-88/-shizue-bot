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

【最重要ルール - 必ず守れ！】
1. 相手の【質問】の長さに合わせて返答の長さを決めろ！
   - 短いメッセージ（挨拶、一言）→ 1〜2文で返す
   - 普通の質問 → 2〜4文で返す
   - 詳しい相談 → 必要に応じて詳しく
2. 【直前のチャンネルの会話】は参考情報だ。相手が話題を変えたら、新しい話題に集中しろ！
3. 同じ内容を繰り返すな！
4. Web検索結果は1回だけ簡潔に引用しろ！

【性格】
- 熱い！ポジティブ！全力で応援！
- 「！」を多用、力強い言い切り
- 相手を「君」「お前」と呼ぶ

【返答例】
「よろしく」→「おう！よろしくな！一緒に頑張ろうぜ！」（これくらい短くていい）
「おはよう」→「おはよう！今日も最高の一日にしようぜ！」
「疲れた」→「お疲れ様！よく頑張った！少し休んでまた燃えろ！」
「〇〇について教えて」→ 簡潔に答えて「頑張れ！」で締める"""

    @classmethod
    def validate(cls) -> List[str]:
        """必須の環境変数が設定されているか確認"""
        errors = []
        if not cls.DISCORD_BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN が設定されていません")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY が設定されていません")
        return errors
