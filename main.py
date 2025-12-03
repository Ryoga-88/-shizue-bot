import asyncio
import sys
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from config import Config
from bot.client import create_bot, setup_bot


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Renderのヘルスチェック用（スリープ防止）"""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # ログを抑制


def start_health_server():
    """ヘルスチェック用HTTPサーバーを起動"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Health check server running on port {port}")


async def main():
    # 環境変数の検証
    errors = Config.validate()
    if errors:
        print("設定エラー:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # ヘルスチェックサーバー起動（Render用）
    if os.environ.get("RENDER"):
        start_health_server()

    # Botを作成
    bot = create_bot()

    # 初期設定
    await setup_bot(bot)

    # Bot起動（自動再接続付き）
    print("Starting bot...")
    while True:
        try:
            await bot.start(Config.DISCORD_BOT_TOKEN)
        except Exception as e:
            print(f"Bot disconnected: {e}")
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
