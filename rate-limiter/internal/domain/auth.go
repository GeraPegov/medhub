package domain

import "github.com/golang-jwt/jwt/v5"

type Admin struct {
	Login    string `json:"login"`
	Password string `json:"password"`
}

type Claims struct {
	UserID int
	jwt.RegisteredClaims
}

type AuthResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
}

type AuthResonseErr struct {
	Detail string `json:"detail_error"`
}

type Info struct {
	Method      string `json:"method"`
	Path        string `json:"path"`
	Description string `json:"description"`
}

type ResponseLogin struct {
	Id   int
	Hash []byte
}
