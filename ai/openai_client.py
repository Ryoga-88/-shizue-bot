import base64
from typing import Optional, List, Dict
import aiohttp
from openai import AsyncOpenAI

from config import Config


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.AI_MODEL
        self.model_search = Config.AI_MODEL_SEARCH
        self.web_search_enabled = Config.WEB_SEARCH_ENABLED

    async def chat(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        image_urls: Optional[List[str]] = None,
        use_web_search: Optional[bool] = None,
    ) -> str:
        """
        AIとチャットする

        Args:
            user_message: ユーザーのメッセージ
            history: 会話履歴 [{"role": "user/assistant", "content": "..."}]
            image_urls: 画像URLのリスト（画像認識用）
            use_web_search: Web検索を使用するか（Noneの場合は自動判定）

        Returns:
            AIの応答テキスト
        """
        # Web検索を使用するかを判定
        should_use_search = self._should_use_web_search(user_message, use_web_search, image_urls)

        messages = [{"role": "system", "content": Config.SYSTEM_PROMPT}]

        # 会話履歴を追加
        if history:
            messages.extend(history)

        # ユーザーメッセージを構築
        if image_urls:
            # 画像付きメッセージ（Web検索は画像と併用不可）
            content = await self._build_image_content(user_message, image_urls)
            messages.append({"role": "user", "content": content})
            should_use_search = False  # 画像があるときはWeb検索を無効化
        else:
            messages.append({"role": "user", "content": user_message})

        if should_use_search:
            # Web検索付きのリクエスト
            response = await self.client.chat.completions.create(
                model=self.model_search,
                messages=messages,
                max_tokens=2000,
                web_search_options={},
            )
        else:
            # 通常のリクエスト
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
            )

        return response.choices[0].message.content or ""

    def _should_use_web_search(
        self,
        message: str,
        explicit_setting: Optional[bool],
        has_images: Optional[List[str]]
    ) -> bool:
        """Web検索を使用するかを判定する"""
        # 明示的に指定されている場合はそれを使用
        if explicit_setting is not None:
            return explicit_setting

        # Web検索が無効化されている場合
        if not self.web_search_enabled:
            return False

        # 画像がある場合は検索を使わない
        if has_images:
            return False

        # 検索が必要そうなキーワードをチェック
        search_keywords = [
            # 時事・ニュース系
            "最新", "今日", "昨日", "今週", "今月", "今年",
            "ニュース", "速報", "現在", "リアルタイム",
            "どうなった", "どうなってる", "何があった",
            "最近", "トレンド", "流行",
            # 検索指示
            "検索", "調べて",
            # 金融・天気
            "株価", "天気", "為替", "レート",
            # イベント
            "イベント", "開催", "発売", "リリース",
            # 就活・キャリア系
            "年収", "給料", "給与", "平均年収", "初任給", "ボーナス", "賞与",
            "就活", "就職", "転職", "採用", "内定", "退職", "離職率",
            "企業", "会社", "業界", "職種", "職業",
            "面接", "ES", "エントリーシート", "履歴書", "職務経歴書",
            "インターン", "説明会", "選考", "SPI", "適性検査",
            "求人", "募集", "倍率", "求人倍率",
            "福利厚生", "残業", "ワークライフバランス", "有給",
            "昇給", "昇進", "キャリアパス", "スキル",
            # 業界名
            "IT業界", "金融業界", "商社", "メーカー", "コンサル",
            "広告", "マスコミ", "不動産", "建設", "医療", "製薬",
            "食品", "アパレル", "小売", "サービス業", "公務員",
            "ベンチャー", "スタートアップ", "外資", "大手",
            # 年齢・世代系
            "20代", "30代", "40代", "50代",
            "新卒", "第二新卒", "中途", "既卒", "未経験",
            "社会人", "フリーター", "ニート",
            "年齢", "世代", "Z世代", "ミレニアル",
            # 恋愛系
            "恋愛", "彼氏", "彼女", "デート", "告白", "片思い",
            "マッチングアプリ", "出会い", "婚活", "結婚",
            "モテ", "脈あり", "脈なし", "好きな人",
            "付き合う", "別れ", "復縁", "浮気",
        ]

        message_lower = message.lower()
        for keyword in search_keywords:
            if keyword in message_lower:
                return True

        return False

    async def _build_image_content(
        self, text: str, image_urls: List[str]
    ) -> List[Dict]:
        """画像付きコンテンツを構築する"""
        content = []

        # テキスト部分
        if text:
            content.append({"type": "text", "text": text})

        # 画像部分
        for url in image_urls:
            image_data = await self._fetch_image_as_base64(url)
            if image_data:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data},
                    }
                )

        return content

    async def _fetch_image_as_base64(self, url: str) -> Optional[str]:
        """画像をダウンロードしてbase64エンコードする"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        return None

                    content_type = resp.headers.get("Content-Type", "image/png")
                    data = await resp.read()
                    b64 = base64.b64encode(data).decode("utf-8")

                    # data URL形式で返す
                    return f"data:{content_type};base64,{b64}"
        except Exception:
            return None
