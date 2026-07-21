package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"new_prog/internal/domain"
	"new_prog/internal/service"
	"time"
)

func Register(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	var NewAdmin domain.Admin
	if err := json.NewDecoder(r.Body).Decode(&NewAdmin); err != nil {
		http.Error(w, "bad news when parse body request", http.StatusBadRequest)
		return
	}
	newToken, err := service.Register(ctx, NewAdmin)
	if err != nil {
		fmt.Println(err)
		http.Error(w, "плохие новости при регистрации админа", http.StatusBadRequest)
		return
	}
	http.SetCookie(w, &http.Cookie{
		Name:     "token",
		Value:    *newToken,
		HttpOnly: true,
		Path:     "/",
		Expires:  time.Now().Add(24 * time.Hour),
	})
	fmt.Fprintln(w, "access")
}

func Login(w http.ResponseWriter, r *http.Request) {

}
