package postgres

import (
	"context"
	"fmt"
	"log/slog"
	"new_prog/internal/domain"
	"strings"
)

func QuantityUsers(ctx context.Context) (int, error) {
	var quantityUsers int
	err := Pool.QueryRow(ctx, "SELECT COUNT(id) FROM users").Scan(&quantityUsers)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to count users",
			"operation", "QuantityUsers",
			"error", err,
		)
		return 0, domain.ErrDatabase
	}
	return quantityUsers, nil
}

func (r *Repository) SearchUsers(ctx context.Context, filter domain.UserFilter) ([]domain.User, error) {
	query := "SELECT id, email, unique_username, registration_date FROM users"
	conditions := []string{"is_deleted = false"}
	args := make([]any, 0, 3)

	if filter.ID != nil {
		args = append(args, *filter.ID)
		conditions = append(conditions, fmt.Sprintf("id = $%d", len(args)))
	}
	if filter.Email != "" {
		args = append(args, filter.Email)
		conditions = append(conditions, fmt.Sprintf("email = $%d", len(args)))
	}
	if filter.Username != "" {
		args = append(args, filter.Username)
		conditions = append(conditions, fmt.Sprintf("unique_username = $%d", len(args)))
	}

	query += " WHERE " + strings.Join(conditions, " AND ")
	rows, err := r.pool.Query(ctx, query, args...)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to search users",
			"operation", "SearchUsers",
			"user_id", filter.ID,
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	defer rows.Close()

	users := make([]domain.User, 0)
	for rows.Next() {
		var u domain.User
		if err := rows.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate); err != nil {
			slog.ErrorContext(
				ctx,
				"failed to scan user",
				"operation", "SearchUsers",
				"error", err,
			)
			return nil, domain.ErrDatabase
		}
		users = append(users, u)
	}
	if err := rows.Err(); err != nil {
		slog.ErrorContext(
			ctx,
			"failed while iterating users",
			"operation", "SearchUsers",
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	return users, nil
}

func (r *Repository) DeleteUser(ctx context.Context, id int) error {
	result, err := r.pool.Exec(ctx, "UPDATE users SET is_deleted = true WHERE id = $1", id)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to delete user",
			"operation", "DeleteUser",
			"user_id", id,
			"error", err,
		)
		return domain.ErrDatabase
	}
	if result.RowsAffected() == 0 {
		slog.WarnContext(
			ctx,
			"user not found",
			"operation", "DeleteUser",
			"user_id", id,
		)
		return domain.ErrRowsNotFound
	}
	return nil
}

func UsersByDate(ctx context.Context, date string) ([]domain.User, error) {
	rows, err := Pool.Query(ctx, "SELECT id, email, unique_username, registration_date FROM users WHERE registration_date::date = $1", date)
	if err != nil {
		slog.ErrorContext(
			ctx,
			"failed to search users by date",
			"operation", "UsersByDate",
			"date", date,
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	defer rows.Close()

	users := make([]domain.User, 0)
	for rows.Next() {
		var u domain.User
		if err := rows.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate); err != nil {
			slog.ErrorContext(
				ctx,
				"failed to scan user",
				"operation", "UsersByDate",
				"error", err,
			)
			return nil, domain.ErrDatabase
		}
		users = append(users, u)
	}
	if err := rows.Err(); err != nil {
		slog.ErrorContext(
			ctx,
			"failed while iterating users",
			"operation", "UsersByDate",
			"error", err,
		)
		return nil, domain.ErrDatabase
	}
	return users, nil
}
