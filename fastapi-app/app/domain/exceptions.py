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

class NotFoundArticleError(Exception):
    pass

class ReactionAlreadyExistsError(Exception):
    pass

class NotFoundCommentsError(Exception):
    pass

class NotValidCredentialsError(Exception):
    pass

class NotFoundCommentError(Exception):
    pass

class NotFoundRecordsError(Exception):
    pass

class AdminApiUnavailableError(Exception):
    pass


class BadGatewayError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"Admin API returned status {status_code}")
