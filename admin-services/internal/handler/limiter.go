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

func writeLimiterResponse(w http.ResponseWriter, err error, number int) {
	if err != nil {
		responseError(w, http.StatusInternalServerError, "Ошибка базы данных")
		return
	}

	switch number {
	case 0:
		w.WriteHeader(http.StatusTooManyRequests)
	case 1:
		w.WriteHeader(http.StatusNoContent)
	default:
		responseError(w, http.StatusInternalServerError, "Некорректный ответ сервиса")
	}
}

func (h *LimiterHandler) LimiterArticle(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userID := r.PathValue("user_id")
	number, err := h.service.GetIncrementLimiterArticle(ctx, userID)
	writeLimiterResponse(w, err, number)
}

func (h *LimiterHandler) LimiterComment(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userID := r.PathValue("user_id")
	articleID := r.PathValue("article_id")

	number, err := h.service.GetIncrementLimiterComment(ctx, userID, articleID)
	writeLimiterResponse(w, err, number)
}
