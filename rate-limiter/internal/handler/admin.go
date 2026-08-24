package handler

import (
	"context"
	"encoding/json"
	"net/http"
	"new_prog/internal/domain"
	"strconv"
	"time"
)

type AdminService interface {
	GetUsers(context.Context, domain.UserFilter) ([]domain.User, error)
	GetArticles(context.Context, domain.ArticleFilter) ([]domain.Article, error)
	GetComments(context.Context, domain.CommentFilter) ([]domain.Comment, error)
	DeleteUser(context.Context, int) error
	DeleteArticle(context.Context, int) error
	DeleteComment(context.Context, int) error
}

type AdminHandler struct {
	service AdminService
}

func NewAdminHandler(service AdminService) *AdminHandler {
	return &AdminHandler{service: service}
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(value); err != nil {
		return
	}
}

func optionalInt(r *http.Request, name string) (*int, error) {
	value := r.URL.Query().Get(name)
	if value == "" {
		return nil, nil
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return nil, err
	}
	return &parsed, nil
}

func pathID(r *http.Request) (int, error) {
	return strconv.Atoi(r.PathValue("id"))
}

func optionalDate(r *http.Request, name string) (*time.Time, error) {
	value := r.URL.Query().Get(name)
	if value == "" {
		return nil, nil
	}
	parsed, err := time.Parse("2006-01-02", value)
	if err != nil {
		return nil, err
	}
	return &parsed, nil
}
