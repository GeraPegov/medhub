package postgres

import (
	"context"
	"new_prog/internal/domain"
)

func Register(ctx context.Context, newAdmin domain.Admin) (*int, error) {
	var id int
	err := Pool.QueryRow(ctx, "INSERT INTO admins (login, password) VALUES ($1, $2) RETURNING id", newAdmin.Login, newAdmin.Password).Scan(&id)
	if err != nil {
		return nil, err
	}
	return &id, nil
}
