package service

import (
	"context"
	"errors"
	"new_prog/internal/domain"
	"new_prog/internal/storage/postgres"
)

func GetUser(ctx context.Context, uniqueUsername string, id string, email string) (*domain.User, error) {
	if uniqueUsername != "" {
		return postgres.SearchUserUsername(ctx, uniqueUsername)
	}
	if id != "" {
		return postgres.SearchUserId(ctx, id)
	}
	if email != "" {
		return postgres.SearchUserEmail(ctx, email)
	}
	return nil, errors.New("not corrected")
}
