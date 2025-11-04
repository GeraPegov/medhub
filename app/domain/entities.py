from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass 
class ArticleEntity:
    author: str
    title: str
    article: str 
    date_add: Optional[date] = None
