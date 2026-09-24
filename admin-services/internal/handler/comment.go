package handler

import (
	"errors"
	"net/http"
	"new_prog/internal/domain"
)

func (h *AdminHandler) GetComments(w http.ResponseWriter, r *http.Request) {
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
	date, err := optionalDate(r, "public_date")
	if err != nil {
		responseError(w, http.StatusBadRequest, "invalid date")
		return
	}
	comments, err := h.service.GetComments(r.Context(), domain.CommentFilter{
		ArticleID: articleID,
		UserID:    userID,
		Date:      date,
	})
	if err != nil {
		responseError(w, http.StatusInternalServerError, "internal server error")
		return
	}
	writeJSON(w, http.StatusOK, comments)
}

func (h *AdminHandler) DeleteComment(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		http.Error(w, "invalid comment id", http.StatusBadRequest)
		return
	}
	err = h.service.DeleteComment(r.Context(), id)
	if err != nil {
		switch {
		case errors.Is(err, domain.ErrRowsNotFound):
			responseError(w, http.StatusNotFound, "Comments not found")
		default:
			responseError(w, http.StatusInternalServerError, "failed to delete comment")
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
