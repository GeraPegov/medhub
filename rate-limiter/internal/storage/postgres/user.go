package postgres

import (
	"context"
	"new_prog/internal/domain"
)

func QuantityUsers(ctx context.Context) (int, error) {
	var quantityUsers int
	err := Pool.QueryRow(ctx, "SELECT COUNT(id) FROM users").Scan(&quantityUsers)
	if err != nil {
		return 0, domain.ErrDatabase
	}
	return quantityUsers, nil
}

func DeleteUser(ctx context.Context, user_id string) error {
	_, err := Pool.Exec(ctx, "UPDATE users SET is_deleted = true WHERE id = $1", user_id)
	return err
}

func DeletedUsers(ctx context.Context) ([]domain.User, error) {
	rows, err := Pool.Query(ctx, "SELECT id, email, unique_username, registration_date FROM users WHERE is_deleted = true")
	if err != nil {
		return nil, err
	}
	var Users []domain.User
	for rows.Next() {
		var u domain.User
		rows.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate)
		Users = append(Users, u)
	}
	return Users, nil
}

func AllUsers(ctx context.Context) ([]domain.User, error) {
	rows, err := Pool.Query(ctx, "SELECT id, email, unique_username, registration_date FROM users WHERE is_deleted = false")
	if err != nil {
		return nil, err
	}
	var Users []domain.User

	for rows.Next() {
		var u domain.User
		rows.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate)
		Users = append(Users, u)
	}
	return Users, nil
}

func SearchUserUsername(ctx context.Context, uniqueUsername string) (*domain.User, error) {
	var u domain.User
	row := Pool.QueryRow(ctx, "SELECT id, email, unique_username, registration_date FROM users WHERE unique_username = $1", uniqueUsername)
	err := row.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate)
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func SearchUserId(ctx context.Context, id string) (*domain.User, error) {
	var u domain.User
	row := Pool.QueryRow(ctx, "SELECT id, email, unique_username, registration_date FROM users WHERE id = $1", id)
	err := row.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate)
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func SearchUserEmail(ctx context.Context, email string) (*domain.User, error) {
	var u domain.User
	row := Pool.QueryRow(ctx, "SELECT id, email, unique_username, registration_date FROM users WHERE email = $1", email)
	err := row.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate)
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func UsersByDate(ctx context.Context, date string) ([]domain.User, error) {
	rows, err := Pool.Query(ctx, "SELECT id, email, unique_username, registration_date FROM users WHERE registration_date::date = $1", date)
	if err != nil {
		return nil, err
	}
	var Users []domain.User
	for rows.Next() {
		var u domain.User
		rows.Scan(&u.Id, &u.Email, &u.UniqueUsername, &u.RegistrationDate)
		Users = append(Users, u)
	}
	return Users, nil
}
