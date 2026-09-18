package handler

import (
	"context"
	"net/http"
)

type LimiterService interface {
	GetIncrementLimiterArticle(context.Context, string) (int, error)
	GetIncrementLimiterComment(context.Context, string, string) (int, error)
}

type LimiterHandler struct {
	service LimiterService
}

func NewLimiterHandler(service LimiterService) *LimiterHandler {
	return &LimiterHandler{service: service}
}

func conditionResponse(w http.ResponseWriter, err error, number int) {
	if err != nil {
		responseError(w, 500, "Ошибка базы данных")
		return
	}
	if number == 0 {
		w.WriteHeader(422)
		return
	}
	if number == 1 {
		w.WriteHeader(204)
		return
	}
}

func (h *LimiterHandler) LimiterArticler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userId := r.PathValue("user_id")
	number, err := h.service.GetIncrementLimiterArticle(ctx, userId)
	conditionResponse(w, err, number)
}

func (h *LimiterHandler) LimiterComment(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userId := r.PathValue("user_id")
	articleId := r.PathValue("article_id")

	number, err := h.service.GetIncrementLimiterComment(ctx, userId, articleId)
	conditionResponse(w, err, number)
}
