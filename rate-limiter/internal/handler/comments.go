package handler

import (
	"net/http"
	"new_prog/internal/domain"
)

func (h *AdminHandler) GetComments(w http.ResponseWriter, r *http.Request) {
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
	date, err := optionalDate(r, "public_date")
	if err != nil {
		http.Error(w, "invalid public date", http.StatusBadRequest)
		return
	}

	comments, err := h.service.GetComments(r.Context(), domain.CommentFilter{
		ArticleID: articleID,
		UserID:    userID,
		Date:      date,
	})
	if err != nil {
		http.Error(w, "failed to get comments", http.StatusInternalServerError)
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
	if err := h.service.DeleteComment(r.Context(), id); err != nil {
		http.Error(w, "failed to delete comment", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
