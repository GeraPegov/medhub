class UserAlreadyExistsError(Exception):
    pass


class UsernameAlreadyExistsError(Exception):
    pass


class NotValidCsrfTokenError(Exception):
    pass


class NotFoundUserError(Exception):
    pass


class NotValidPasswordError(Exception):
    pass


class ArticleNotFoundError(Exception):
    pass


class ReactionAlreadyExistsError(Exception):
    pass


class CommentsNotFoundError(Exception):
    pass
