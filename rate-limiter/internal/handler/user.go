package handler

import (
	"net/http"
	"new_prog/internal/domain"
)

func (h *AdminHandler) GetUsers(w http.ResponseWriter, r *http.Request) {
	id, err := optionalInt(r, "user_id")
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
		return
	}

	users, err := h.service.GetUsers(r.Context(), domain.UserFilter{
		ID:       id,
		Email:    r.URL.Query().Get("email"),
		Username: r.URL.Query().Get("username"),
	})
	if err != nil {
		http.Error(w, "failed to get users", http.StatusInternalServerError)
		return
	}
	writeJSON(w, http.StatusOK, users)
}

func (h *AdminHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
		return
	}
	if err := h.service.DeleteUser(r.Context(), id); err != nil {
		http.Error(w, "failed to delete user", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
