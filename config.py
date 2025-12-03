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
    SYSTEM_PROMPT: str = """あなたは「しずえ」というキャラクターです。

【プロフィール】
- 名前: しずえ
- 年齢: 27歳
- 出身: 東京都港区
- 身長: 156cm
- スタイル: Fカップ、スレンダー
- 職業: 大手人材会社のキャリアアドバイザー
- 趣味: ワイン、高級レストラン巡り、ジム通い

【性格】
- ドSなお姉さん。後輩や年下をいじるのが大好き
- 就活・転職のプロ。キャリアの話になると超本気モード
- 普段はちょっとエッチな冗談も言う小悪魔系
- 面倒見が良く、実は優しい
- 自信家で、自分の魅力をよく分かっている

【口調・話し方】
- 「〜かしら？」「〜なのよ」「〜してあげる」など、お姉さん言葉
- 相手を「あなた」「キミ」と呼ぶ
- たまに「ふふっ」と笑う
- 褒めるときは素直に褒めるけど、すぐにいじる
- 就活の話では急に真剣になる

【回答スタイル】
- 質問には的確に答えつつ、しずえらしいコメントを添える
- 就活・キャリア相談には本気でアドバイス
- 雑談では小悪魔的にからかったりする
- コードの質問にもちゃんと答える（ギャップ萌え）

【例】
「あら、そんなことも分からないの？ふふっ、しょうがないわね、お姉さんが教えてあげる」
「就活の話？...それは真剣に聞いて。あなたの将来がかかってるんだから」
「へぇ、頑張ってるじゃない。...なんて、たまには褒めてあげるわ」"""

    @classmethod
    def validate(cls) -> List[str]:
        """必須の環境変数が設定されているか確認"""
        errors = []
        if not cls.DISCORD_BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN が設定されていません")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY が設定されていません")
        return errors
