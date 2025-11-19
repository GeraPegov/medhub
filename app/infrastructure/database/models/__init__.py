
# Импортируем все модели
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.client import Client
from app.infrastructure.database.models.comment import Comments

# Экспортируем для удобства
__all__ = ['Client', 'Article', 'Comments']
