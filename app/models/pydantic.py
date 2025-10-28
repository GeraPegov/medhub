from pydantic import BaseModel

class ArticleModel(BaseModel):
    author: str
    title: str
    content: str