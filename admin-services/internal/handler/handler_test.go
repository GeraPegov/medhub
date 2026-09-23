package handler

import (
	"context"
	"new_prog/internal/domain"
)

type adminServiceStub struct {
	resultUsers []domain.User
	errUsers    error

	resultArticles []domain.Article
	errArticles    error

	resultComments []domain.Comment
	errComments    error

	quantityUsers    int
	quantityArticles int

	articleId int
	userId    int
	comentId  int
}

func (a *adminServiceStub) GetUsers(ctx context.Context, userFilter domain.UserFilter) ([]domain.User, error) {
	return a.resultUsers, a.errUsers
}

func (a *adminServiceStub) GetArticles(ctx context.Context, articleFilter domain.ArticleFilter) ([]domain.Article, error) {
	return a.resultArticles, a.errArticles
}

func (a *adminServiceStub) GetComments(ctx context.Context, commentFilter domain.CommentFilter) ([]domain.Comment, error) {
	return a.resultComments, a.errComments
}

func (a *adminServiceStub) DeleteUser(ctx context.Context, userId int) error {
	return a.errUsers
}

func (a *adminServiceStub) DeleteArticle(ctx context.Context, articleId int) error {
	a.articleId = articleId
	return a.errArticles
}

func (a *adminServiceStub) DeleteComment(ctx context.Context, commentId int) error {
	return a.errComments
}

func (a *adminServiceStub) QuantityUsers(ctx context.Context) (int, error) {
	return a.quantityUsers, a.errUsers
}

func (a *adminServiceStub) QuantityArticles(ctx context.Context) (int, error) {
	return a.quantityArticles, a.errArticles
}

func (a *adminServiceStub) ArticlesByDate(ctx context.Context, date string) ([]domain.Article, error) {
	return a.resultArticles, a.errArticles
}

func (a *adminServiceStub) UsersByDate(ctx context.Context, date string) ([]domain.User, error) {
	return a.resultUsers, a.errArticles
}
