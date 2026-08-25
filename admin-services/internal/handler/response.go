package handler

import (
	"encoding/json"
	"net/http"
	"new_prog/internal/domain"
)

func responseError(w http.ResponseWriter, statusCode int, detail string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(domain.AuthResonseErr{
		Detail: detail,
	})
}
