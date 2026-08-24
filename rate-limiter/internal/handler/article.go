package handler

import (
	"encoding/json"
	"net/http"
	"new_prog/internal/domain"
	"new_prog/internal/storage/postgres"
	"time"
)

func (h *AdminHandler) GetArticles(w http.ResponseWriter, r *http.Request) {
	articleID, err := optionalInt(r, "article_id")
	if err != nil {
		http.Error(w, "invalid article id", http.StatusBadRequest)
		return
	}
	userID, err := optionalInt(r, "user_id")
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
		return
	}

	articles, err := h.service.GetArticles(r.Context(), domain.ArticleFilter{
		ID:     articleID,
		UserID: userID,
		Title:  r.URL.Query().Get("title"),
	})
	if err != nil {
		http.Error(w, "failed to get articles", http.StatusInternalServerError)
		return
	}
	writeJSON(w, http.StatusOK, articles)
}

func (h *AdminHandler) DeleteArticle(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		http.Error(w, "invalid article id", http.StatusBadRequest)
		return
	}
	if err := h.service.DeleteArticle(r.Context(), id); err != nil {
		http.Error(w, "failed to delete article", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func ArticlesRegDate(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	date := r.URL.Query().Get("date")
	if _, err := time.Parse("2006-01-02", date); err != nil {
		http.Error(w, "invalid date format", http.StatusBadRequest)
		return
	}
	articles, err := postgres.ArticlesByDate(ctx, date)
	if err != nil {
		http.Error(w, "failed to get articles", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(articles); err != nil {
		return
	}
}
