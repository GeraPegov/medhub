package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"new_prog/internal/domain"
	"new_prog/internal/service"
	"strings"
)

func AuthCheck(w http.ResponseWriter, r *http.Request) {
	authHeader := r.Header.Get("Authorization")

	parts := strings.SplitN(authHeader, " ", 2)
	if len(parts) != 2 || parts[0] != "Bearer" {
		responseError(w, http.StatusUnauthorized, "invalid Authorization header")
		return
	}
	_, err := service.ValidateToken(parts[1])
	if err != nil {
		responseError(w, http.StatusUnauthorized, "invalid or expired token")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func Register(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	var NewAdmin domain.Admin
	if err := json.NewDecoder(r.Body).Decode(&NewAdmin); err != nil {
		responseError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	err := service.Register(ctx, NewAdmin)
	if err != nil {
		switch {
		case errors.Is(err, domain.ErrAdminAlreadyExists):
			responseError(w, http.StatusConflict, err.Error())
		default:
			responseError(w, http.StatusInternalServerError, "internal server error")
		}
		return
	}
	writeJSON(w, http.StatusCreated, map[string]string{
		"message": "admin created"})
}

func Login(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	var admin domain.Admin

	if err := json.NewDecoder(r.Body).Decode(&admin); err != nil {
		responseError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	newToken, err := service.Login(ctx, admin)
	if err != nil {
		switch {
		case errors.Is(err, domain.ErrInvalidCredentials):
			responseError(w, http.StatusUnauthorized, err.Error())
		default:
			responseError(w, http.StatusInternalServerError, "internal server error")
		}
		return
	}
	response := domain.AuthResponse{
		AccessToken: newToken,
		TokenType:   "Bearer",
	}

	writeJSON(w, http.StatusOK, response)
}
