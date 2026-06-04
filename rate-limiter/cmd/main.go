package main

import (
	"net/http"
	"new_prog/internal/handler"
	"new_prog/internal/storage"
)

func main() {
	storage.CreateRedis()
	http.HandleFunc("/hello", handler.Hello)
	http.HandleFunc("/get", handler.Get)
	http.ListenAndServe(":8000", nil)
}
