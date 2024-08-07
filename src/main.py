import os
from typing import List, Union

import fire
from dotenv import load_dotenv
from devtopy import DevTo
from devtopy.model import PublishedArticleList, PublishedArticle, ErrorResponse, Article

from dev_to_digest.db import DataBase
from dev_to_digest.report import DiscordWebhookClient
from dev_to_digest.lang_processor_gpt import LangProcGpt

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
DOT_ENV_PATH = os.path.join(THIS_DIR, ".env")

load_dotenv(dotenv_path=DOT_ENV_PATH)


def fil_articles(
    articles: PublishedArticleList, threshold: int
) -> List[PublishedArticle]:
    return [a for a in articles.articles if a.positive_reactions_count > threshold]


def proc(
    tag_name: str,
    webhook_url: str,
    reaction_threshold: int = 55,
    summary_sentences: int = 5,
    is_silent: bool = True,
):
    # 8% = 20
    # 5% = 22
    # 2% = 53
    db = DataBase(dir_path=THIS_DIR)
    dt = DevTo(api_key=os.getenv("DEVTO_API_KEY"))
    res = dt.articles.get(page=1, per_page=1000, tag=tag_name.lower())
    articles = fil_articles(res, reaction_threshold)
    dw = DiscordWebhookClient(
        webhook_url=webhook_url,
        is_silent=is_silent,
    )
    for article in articles:
        url = str(article.url)
        if db.url_exists(url):
            continue
        article_id = article.id
        detail: Union[ErrorResponse, Article] = dt.articles.get_by_id(article_id)
        if type(detail) is ErrorResponse:
            continue
        title = article.title
        tags = article.tag_list
        contents = detail.body_markdown
        params = {
            "title": title,
            "contents": contents,
            "url": url,
            "img_url": detail.social_image,
            "tag_list": tags,
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
        lp = LangProcGpt(**params)
        data = lp.run(summary_sentences=summary_sentences)
        err_status = dw.report(data)
        if err_status:
            continue
        db.insert_data(
            url=data.url,
            en_title=data.en_title,
            ja_title=data.ja_title,
            translated_text=data.ja_summary,
            tags=data.tags,
        )
        exit()


def main():
    fire.Fire(proc)


if __name__ == "__main__":
    main()
