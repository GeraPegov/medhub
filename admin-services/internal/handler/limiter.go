package handler

import (
	"context"
	"net/http"
)

type LimiterService interface {
	GetIncrementLimiterArticle(context.Context, string) (int64, error)
}

type LimiterHandler struct {
	service LimiterService
}

func NewLimiterHandler(service LimiterService) *LimiterHandler {
	return &LimiterHandler{service: service}
}

func (h *LimiterHandler) LimiterArticlerForUser(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userId := r.PathValue("user_id")
	h.service.GetIncrementLimiterArticle(ctx, userId)
}
