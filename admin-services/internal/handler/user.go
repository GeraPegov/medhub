package handler

import (
	"errors"
	"net/http"
	"new_prog/internal/domain"
)

func (h *AdminHandler) GetUsers(w http.ResponseWriter, r *http.Request) {
	id, err := optionalInt(r, "user_id")
	if err != nil {
		responseError(w, http.StatusBadRequest, "invalid user id")
		return
	}

	users, err := h.service.GetUsers(r.Context(), domain.UserFilter{
		ID:       id,
		Email:    r.URL.Query().Get("email"),
		Username: r.URL.Query().Get("username"),
	})
	if err != nil {
		responseError(w, http.StatusInternalServerError, "failed to get users")
		return
	}
	writeJSON(w, http.StatusOK, users)
}

func (h *AdminHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r)
	if err != nil {
		responseError(w, http.StatusBadRequest, "ivalid user id")
		return
	}
	if err := h.service.DeleteUser(r.Context(), id); err != nil {
		switch {
		case errors.Is(err, domain.ErrRowsNotFound):
			responseError(w, http.StatusNotFound, "user not found")
		default:
			responseError(w, http.StatusInternalServerError, "failed to delete user")
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
