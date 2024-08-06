import os
from typing import List
import fire
from dotenv import load_dotenv
from devtopy import DevTo
from devtopy.model import PublishedArticleList, PublishedArticle

from dev_to_digest.db import DataBase


THIS_DIR = os.path.abspath(os.path.dirname(__file__))
DOT_ENV_PATH = os.path.join(THIS_DIR, ".env")
load_dotenv(dotenv_path=DOT_ENV_PATH)


def fil_articles(
    articles: PublishedArticleList, threshold: int
) -> List[PublishedArticle]:
    return [a for a in articles if a.positive_reactions_count > threshold]


def proc(tag_name: str, webhook_url: str, reaction_threshold: int = 20):
    db = DataBase(dir_path=THIS_DIR)
    dt = DevTo(api_key=os.getenv("DEVTO_API_KEY"))
    res = dt.articles.get(page=1, per_page=1000, tag=tag_name.lower())
    articles = fil_articles(res, reaction_threshold)
    for article in articles:
        if db.url_exists(article.url):
            continue
        


def main():
    fire.Fire(proc)


if __name__ == "__main__":
    main()
