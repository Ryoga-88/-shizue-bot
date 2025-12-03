import base64
from typing import Optional, List, Dict
import aiohttp
from openai import AsyncOpenAI

from config import Config


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.AI_MODEL

    async def chat(
        self,
        user_message: str,
        history: Optional[List[Dict]] = None,
        image_urls: Optional[List[str]] = None,
    ) -> str:
        """
        AIとチャットする

        Args:
            user_message: ユーザーのメッセージ
            history: 会話履歴 [{"role": "user/assistant", "content": "..."}]
            image_urls: 画像URLのリスト（画像認識用）

        Returns:
            AIの応答テキスト
        """
        messages = [{"role": "system", "content": Config.SYSTEM_PROMPT}]

        # 会話履歴を追加
        if history:
            messages.extend(history)

        # ユーザーメッセージを構築
        if image_urls:
            # 画像付きメッセージ
            content = await self._build_image_content(user_message, image_urls)
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": user_message})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=2000,
        )

        return response.choices[0].message.content or ""

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
