from pydantic import BaseModel


class ProcessedArticleData(BaseModel):
    en_title: str
    ja_title: str
    url: str
    img_url: str
    tags: str
    ja_summary: str
