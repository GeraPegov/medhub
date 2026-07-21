package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"new_prog/internal/service"
	"new_prog/internal/storage/postgres"
)

func SearchUsers(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("access_token")
	if err != nil {
		http.Error(w, "not token", http.StatusBadRequest)
		return
	}
	_, err = service.ValidateToken(cookie.Value)
	if err != nil {
		fmt.Printf("not validate token: %s", err)
		http.Error(w, "not valide token", http.StatusUnauthorized)
		return
	}
	ctx := r.Context()
	uniqueUsername := r.URL.Query().Get("uniqueUsername")
	id := r.URL.Query().Get("id")
	email := r.URL.Query().Get("email")
	if uniqueUsername == "" && id == "" && email == "" {
		users, err := postgres.GetAllUsers(ctx)
		if err != nil {
			http.Error(w, "warning for search all users", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(users)
		return
	}
	user, err := service.GetUser(ctx, uniqueUsername, id, email)
	if err != nil {
		http.Error(w, "warning for search user", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

func UserDelete(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	userId := r.URL.Query().Get("id")
	err := postgres.DeleteUser(ctx, userId)
	if err != nil {
		http.Error(w, "warning for delete user", http.StatusInternalServerError)
	}
}

func DeletedUsers(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	users, err := postgres.GetDeletedUsers(ctx)
	if err != nil {
		http.Error(w, "warning for search deleted users", http.StatusInternalServerError)
		return
	}
	json.NewEncoder(w).Encode(users)
}
