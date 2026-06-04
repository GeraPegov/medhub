package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"new_prog/internal/domain"
	"new_prog/internal/storage"
)

var count int = 0

func Hello(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	count += 1
	var NewUser domain.User
	json.NewDecoder(r.Body).Decode(&NewUser)
	NewUser.Id = count
	defer r.Body.Close()
	storage.Save(ctx, NewUser)
}

func Get(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	id := r.URL.Query().Get("id")
	result := storage.Get(ctx, id)
	fmt.Println(result)
}
