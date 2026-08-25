package postgres

import (
	"context"
	"errors"
	"log/slog"
	"new_prog/internal/domain"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
)

func Register(ctx context.Context, login string, password []byte) error {
	_, err := Pool.Exec(ctx, "INSERT INTO admins (login, password) VALUES ($1, $2)", login, password)
	if err != nil {
		var pgErr *pgconn.PgError

		if errors.As(err, &pgErr) {
			switch pgErr.Code {
			case "23505":
				return domain.ErrAdminAlreadyExists
			}
		}
		slog.ErrorContext(
			ctx,
			"failed to register admin",
			"operation", "Register",
			"error", err,
		)
		return domain.ErrDatabase
	}
	return nil
}

func Login(ctx context.Context, login string) (int, string, error) {
	var id int
	var hash string
	err := Pool.QueryRow(ctx, "SELECT id, password FROM admins WHERE login = $1", login).Scan(&id, &hash)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return 0, "", domain.ErrInvalidCredentials
		}
		slog.ErrorContext(
			ctx,
			"failed to find admin for login",
			"operation", "Login",
			"error", err,
		)
		return 0, "", domain.ErrDatabase
	}
	return id, hash, nil
}
