from pydantic import BaseModel, Field


class ArticleCreateDTO(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10, max_length=10000)
