package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"new_prog/internal/domain"
	"new_prog/internal/service"
	"strings"
)

// func Info(w http.ResponseWriter, r *http.Request) {
// 	manyInfo := []domain.Info{
// 		{
// 			Method:      "get",
// 			Path:        "/admin/articles",
// 			Description: "You can use Id and Title for search article. Example: /admin/articles?id=1; /admin/articles?title=skelleton",
// 		},
// 		{
// 			Method:      "delete",
// 			Path:        "/admin/articles/",
// 			Description: "You wanna use Id for delete article. Example: /admin/articles/1",
// 		},
// 		{
// 			Method:      "get",
// 			Path:        "/admin/users/{}",
// 			Description: "You wanna use Id for search user. Example: /admin/users/1",
// 		},
// 		{
// 			Method:      "delete",
// 			Path:        "admin/users/{}",
// 			Description: "You wanna use Id for delete user. Example: /admin/users/1",
// 		},
// 	}
// 	w.Header().Set("Content-Type", "application/json")
// 	json.NewEncoder(w).Encode(manyInfo)
// }

func AuthCheck(w http.ResponseWriter, r *http.Request) {
	authHeader := r.Header.Get("Authorization")

	parts := strings.SplitN(authHeader, " ", 2)
	if len(parts) != 2 || parts[0] != "Bearer" {
		http.Error(w, "invalid Authorization header", http.StatusUnauthorized)
		return
	}
	_, err := service.ValidateToken(parts[1])
	if err != nil {
		http.Error(w, "invalid or expired token", http.StatusUnauthorized)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func Register(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	var NewAdmin domain.Admin
	if err := json.NewDecoder(r.Body).Decode(&NewAdmin); err != nil {
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}
	err := service.Register(ctx, NewAdmin)
	if err != nil {
		switch {
		case errors.Is(err, domain.ErrAdminAlreadyExists):
			http.Error(w, err.Error(), http.StatusConflict)
		default:
			http.Error(w, "internal server error", http.StatusInternalServerError)
		}
		return
	}
	w.WriteHeader(http.StatusCreated)
}

func Login(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	var admin domain.Admin
	if err := json.NewDecoder(r.Body).Decode(&admin); err != nil {
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}
	newToken, err := service.Login(ctx, admin)
	if err != nil {
		switch {
		case errors.Is(err, domain.ErrInvalidCredentials):
			http.Error(w, err.Error(), http.StatusUnauthorized)
		default:
			http.Error(w, "internal server error", http.StatusInternalServerError)
		}
		return
	}
	response := domain.AuthResponse{
		AccessToken: newToken,
		TokenType:   "Bearer",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
