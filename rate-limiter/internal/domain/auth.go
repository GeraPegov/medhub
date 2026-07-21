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
