package service

import (
	"context"
	"new_prog/internal/domain"
)

type AdminRepository interface {
	SearchUsers(context.Context, domain.UserFilter) ([]domain.User, error)
	SearchArticles(context.Context, domain.ArticleFilter) ([]domain.Article, error)
	SearchComments(context.Context, domain.CommentFilter) ([]domain.Comment, error)
	DeleteUser(context.Context, int) error
	DeleteArticle(context.Context, int) error
	DeleteComment(context.Context, int) error
	QuantityUsers(context.Context) (int, error)
	QuantityArticles(context.Context) (int, error)
	ArticlesByDate(context.Context, string) ([]domain.Article, error)
	UsersByDate(context.Context, string) ([]domain.User, error)
	Login(context.Context, string) (int, string, error)
	Register(context.Context, string, []byte) error
}

type AdminService struct {
	repository AdminRepository
}

func NewAdminService(repository AdminRepository) *AdminService {
	return &AdminService{repository: repository}
}

func (s *AdminService) GetUsers(ctx context.Context, filter domain.UserFilter) ([]domain.User, error) {
	return s.repository.SearchUsers(ctx, filter)
}

func (s *AdminService) GetArticles(ctx context.Context, filter domain.ArticleFilter) ([]domain.Article, error) {
	return s.repository.SearchArticles(ctx, filter)
}

func (s *AdminService) GetComments(ctx context.Context, filter domain.CommentFilter) ([]domain.Comment, error) {
	return s.repository.SearchComments(ctx, filter)
}

func (s *AdminService) DeleteUser(ctx context.Context, id int) error {
	return s.repository.DeleteUser(ctx, id)
}

func (s *AdminService) DeleteArticle(ctx context.Context, id int) error {
	return s.repository.DeleteArticle(ctx, id)
}

func (s *AdminService) DeleteComment(ctx context.Context, id int) error {
	return s.repository.DeleteComment(ctx, id)
}

func (s *AdminService) QuantityUsers(ctx context.Context) (int, error) {
	return s.repository.QuantityUsers(ctx)
}

func (s *AdminService) QuantityArticles(ctx context.Context) (int, error) {
	return s.repository.QuantityArticles(ctx)
}

func (s *AdminService) ArticlesByDate(ctx context.Context, date string) ([]domain.Article, error) {
	return s.repository.ArticlesByDate(ctx, date)
}

func (s *AdminService) UsersByDate(ctx context.Context, date string) ([]domain.User, error) {
	return s.repository.UsersByDate(ctx, date)
}
