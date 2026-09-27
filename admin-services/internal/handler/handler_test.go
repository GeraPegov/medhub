package handler

import (
	"context"
	"new_prog/internal/domain"
	"time"
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
	commentId int
}

func (a *adminServiceStub) GetUsers(ctx context.Context, userFilter domain.UserFilter) ([]domain.User, error) {
	if userFilter.ID != nil {
		user := domain.User{
			Id: *userFilter.ID,
		}
		a.resultUsers = append(a.resultUsers, user)
	}
	if userFilter.Username != "" {
		user := domain.User{
			UniqueUsername: userFilter.Username,
		}
		a.resultUsers = append(a.resultUsers, user)
	}
	if userFilter.Email != "" {
		user := domain.User{
			Email: userFilter.Email,
		}
		a.resultUsers = append(a.resultUsers, user)
	}
	return a.resultUsers, a.errUsers
}

func (a *adminServiceStub) GetArticles(ctx context.Context, articleFilter domain.ArticleFilter) ([]domain.Article, error) {
	if articleFilter.ID != nil {
		article := domain.Article{
			Id: *articleFilter.ID,
		}
		a.resultArticles = append(a.resultArticles, article)
	}
	if articleFilter.UserID != nil {
		article := domain.Article{
			UserID: *articleFilter.UserID,
		}
		a.resultArticles = append(a.resultArticles, article)
	}
	if articleFilter.Title != "" {
		article := domain.Article{
			Title: articleFilter.Title,
		}
		a.resultArticles = append(a.resultArticles, article)
	}
	if articleFilter.Date != nil {
		article := domain.Article{
			CreatedAt: *articleFilter.Date,
		}
		a.resultArticles = append(a.resultArticles, article)
	}
	return a.resultArticles, a.errArticles
}

func (a *adminServiceStub) GetComments(ctx context.Context, commentFilter domain.CommentFilter) ([]domain.Comment, error) {
	if commentFilter.ArticleID != nil {
		comment := domain.Comment{
			ArticleID: *commentFilter.ArticleID,
		}
		a.resultComments = append(a.resultComments, comment)
	}
	if commentFilter.UserID != nil {
		comment := domain.Comment{
			UserID: *commentFilter.UserID,
		}
		a.resultComments = append(a.resultComments, comment)
	}
	if commentFilter.Date != nil {
		comment := domain.Comment{
			CreatedAt: *commentFilter.Date,
		}
		a.resultComments = append(a.resultComments, comment)
	}
	return a.resultComments, a.errComments
}

func (a *adminServiceStub) DeleteUser(ctx context.Context, userId int) error {
	a.userId = userId
	return a.errUsers
}

func (a *adminServiceStub) DeleteArticle(ctx context.Context, articleId int) error {
	a.articleId = articleId
	return a.errArticles
}

func (a *adminServiceStub) DeleteComment(ctx context.Context, commentId int) error {
	a.commentId = commentId
	return a.errComments
}

func (a *adminServiceStub) QuantityUsers(ctx context.Context, dateFrom time.Time, dateTo time.Time) (int, error) {
	return a.quantityUsers, a.errUsers
}

func (a *adminServiceStub) QuantityArticles(ctx context.Context, dateFrom time.Time, dateTo time.Time) (int, error) {
	return a.quantityArticles, a.errArticles
}

func (a *adminServiceStub) ArticlesByDate(ctx context.Context, date string) ([]domain.Article, error) {
	return a.resultArticles, a.errArticles
}

func (a *adminServiceStub) UsersByDate(ctx context.Context, date string) ([]domain.User, error) {
	return a.resultUsers, a.errArticles
}
