import requests

from .model import ProcessedArticleData


class DiscordWebhookClient:
    def __init__(self, webhook_url: str, is_silent: bool = True):
        self.webhook_url = webhook_url
        self.is_silent = is_silent

    def report(self, proc_data: ProcessedArticleData) -> int:
        embed = {
            "color": 0x00C0CE,
            "title": proc_data.ja_title,
            "url": proc_data.url,
            "fields": [
                {"name": "EnTitle", "value": proc_data.en_title},
                {"name": "Tags", "value": proc_data.tags},
                {"name": "Summary", "value": proc_data.ja_summary},
            ],
            "image": {"url": proc_data.img_url},
        }
        data = {
            "content": "",
            "embeds": [embed],
        }
        if self.is_silent:
            data["flags"] = 4096
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook_url, json=data, headers=headers)
        if response.status_code in (200, 204):
            return 0
        return response.status_code
