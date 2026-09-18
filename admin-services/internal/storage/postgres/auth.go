package postgres

import (
	"context"
	"errors"
	"log/slog"
	"new_prog/internal/domain"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
)

func (r *Repository) Register(ctx context.Context, login string, password []byte) error {
	admins := r.pool.QueryRow(ctx, "SELECT COUNT(id) FROM admins")
	var check_admins_quantity int
	if err := admins.Scan(&check_admins_quantity); err != nil {
		slog.ErrorContext(
			ctx,
			"failed to scan comment",
			"operation", "Register",
		)
		return domain.ErrDatabase
	}
	if check_admins_quantity >= 1 {
		slog.ErrorContext(
			ctx,
			"Admin already exists",
			"operation", "Register",
		)
		return domain.ErrAdminAlreadyExists
	}
	_, err := r.pool.Exec(ctx, "INSERT INTO admins (login, password) VALUES ($1, $2)", login, password)
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

func (r *Repository) Login(ctx context.Context, login string) (int, string, error) {
	var id int
	var hash string
	err := r.pool.QueryRow(ctx, "SELECT id, password FROM admins WHERE login = $1", login).Scan(&id, &hash)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			slog.ErrorContext(
				ctx,
				"failed to find admin for login",
				"operation", "Login",
				"error", err,
			)
			return 0, "", domain.ErrInvalidCredentials
		}
		return 0, "", domain.ErrDatabase
	}
	return id, hash, nil
}
