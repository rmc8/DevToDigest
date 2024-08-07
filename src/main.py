import os
import json
from typing import List

import fire
from dotenv import load_dotenv
from devtopy import DevTo
from devtopy.model import PublishedArticleList, PublishedArticle, ErrorResponse

from dev_to_digest.db import DataBase

from dev_to_digest.lang_processor_gpt import LangProcGpt

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
DOT_ENV_PATH = os.path.join(THIS_DIR, ".env")
JSON_PATH = os.path.join(THIS_DIR, "config.json")

load_dotenv(dotenv_path=DOT_ENV_PATH)

with open(JSON_PATH, "r") as f:
    conf = json.load(f)


def fil_articles(
    articles: PublishedArticleList, threshold: int
) -> List[PublishedArticle]:
    return [a for a in articles.articles if a.positive_reactions_count > threshold]


def proc(tag_name: str, webhook_url: str, reaction_threshold: int = 55):
    # 8% = 20
    # 5% = 22
    # 2% = 53
    db = DataBase(dir_path=THIS_DIR)
    dt = DevTo(api_key=os.getenv("DEVTO_API_KEY"))
    res = dt.articles.get(page=1, per_page=1000, tag=tag_name.lower())
    articles = fil_articles(res, reaction_threshold)
    for article in articles:
        url = str(article.url)
        if db.url_exists(url):
            continue
        article_id = article.id
        detail = dt.articles.get_by_id(article_id)
        if type(detail) is ErrorResponse:
            continue
        title = article.title
        tags = article.tag_list
        contents = detail.body_markdown
        params = {
            "title": title,
            "contents": contents,
            "url": url,
            "tag_list": tags,
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
        lp = LangProcGpt(**params)
        data = lp.run()
        print(data)
        break


def main():
    fire.Fire(proc)


if __name__ == "__main__":
    main()
