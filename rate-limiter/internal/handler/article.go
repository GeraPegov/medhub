package handler

import (
	"errors"
	"net/http"
	"new_prog/internal/domain"
)

func (h *AdminHandler) GetArticles(w http.ResponseWriter, r *http.Request) {
	articleID, err := optionalInt(r, "article_id")
	if err != nil {
		responseError(w, http.StatusBadRequest, "invalid article id")
		return
	}
	userID, err := optionalInt(r, "user_id")
	if err != nil {
		responseError(w, http.StatusBadRequest, "invalid user id")
		return
	}
	articles, err := h.service.GetArticles(r.Context(), domain.ArticleFilter{
		ID:     articleID,
		UserID: userID,
		Title:  r.URL.Query().Get("title"),
	})
	if err != nil {
		responseError(w, http.StatusInternalServerError, "failed to get articles")
		return
	}
	writeJSON(w, http.StatusOK, articles)
}

func (h *AdminHandler) DeleteArticle(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		responseError(w, http.StatusBadRequest, "invalid article id")
		return
	}
	if err := h.service.DeleteArticle(r.Context(), id); err != nil {
		switch {
		case errors.Is(err, domain.ErrRowsNotFound):
			responseError(w, http.StatusNotFound, "article not found")
		default:
			responseError(w, http.StatusInternalServerError, "internal server error")
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
