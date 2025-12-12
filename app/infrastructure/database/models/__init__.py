
# Импортируем все модели
from app.infrastructure.database.models.article import Article
from app.infrastructure.database.models.comment import Comments
from app.infrastructure.database.models.user import User

# Экспортируем для удобства
__all__ = ['User', 'Article', 'Comments']
