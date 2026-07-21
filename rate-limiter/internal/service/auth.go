package service

import (
	"context"
	"errors"
	"fmt"
	"new_prog/internal/domain"
	"new_prog/internal/storage/postgres"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

func Register(ctx context.Context, admin domain.Admin) (*string, error) {
	id, err := postgres.Register(ctx, admin)
	if err != nil {
		return nil, err
	}
	newToken, err := GenerateToken(*id)
	if err != nil {
		return nil, err
	}
	return &newToken, nil
}

var secretKey = []byte("6b33da986da8e74888c1efb080563b4cfc37a34a3ec4cccacc5512ddec47a070")

func GenerateToken(userID int) (string, error) {
	claims := domain.Claims{
		UserID: userID,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "go-service",
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(secretKey)
}

func ValidateToken(tokenStr string) (*domain.Claims, error) {
	token, err := jwt.ParseWithClaims(
		tokenStr,
		&domain.Claims{},
		func(token *jwt.Token) (interface{}, error) {
			if token.Method != jwt.SigningMethodHS256 {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return secretKey, nil
		})
	if err != nil {
		switch {
		case errors.Is(err, jwt.ErrTokenSignatureInvalid):
			return nil, fmt.Errorf("неверная подпись JWT: %w", err)

		case errors.Is(err, jwt.ErrTokenExpired):
			return nil, fmt.Errorf("JWT истёк: %w", err)

		case errors.Is(err, jwt.ErrTokenMalformed):
			return nil, fmt.Errorf("JWT повреждён: %w", err)

		default:
			return nil, fmt.Errorf("ошибка проверки JWT: %w", err)
		}
	}
	claims, ok := token.Claims.(*domain.Claims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	return claims, nil
}
