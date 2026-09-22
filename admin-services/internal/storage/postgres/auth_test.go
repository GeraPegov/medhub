package postgres

import (
	"context"
	"errors"
	"new_prog/internal/domain"
	"testing"
)

func TestRegister_Success(t *testing.T) {
	repository := setupTest(t)
	login := "example_login"
	password := []byte("example_password")
	err := repository.Register(context.Background(), login, password)
	if err != nil {
		t.Fatalf("Register() returned an unexpected error: %v", err)
	}

	var storedLogin, storedPassword string
	err = repository.pool.QueryRow(
		context.Background(),
		"SELECT login, password FROM admins",
	).Scan(&storedLogin, &storedPassword)
	if err != nil {
		t.Fatalf("failed to read registered admin: %v", err)
	}
	if storedLogin != login || storedPassword != string(password) {
		t.Fatalf("Register() stored login %q and password %q, expected %q and %q", storedLogin, storedPassword, login, password)
	}
}

func TestRegister_AlreadyExists(t *testing.T) {
	repository := setupTest(t)
	password := []byte("example_password")
	if err := repository.Register(context.Background(), "example_login", password); err != nil {
		t.Fatalf("failed to register first admin: %v", err)
	}

	err := repository.Register(context.Background(), "another_login", password)
	if !errors.Is(err, domain.ErrAdminAlreadyExists) {
		t.Fatalf("Register() error = %v, expected %v", err, domain.ErrAdminAlreadyExists)
	}

	var count int
	if err := repository.pool.QueryRow(context.Background(), "SELECT COUNT(*) FROM admins").Scan(&count); err != nil {
		t.Fatalf("failed to count admins: %v", err)
	}
	if count != 1 {
		t.Fatalf("Register() left %d admins, expected 1", count)
	}
}

func TestLogin_Success(t *testing.T) {
	repository := setupTest(t)
	login := "example_login"
	password := "example_password"
	var adminID int
	err := repository.pool.QueryRow(
		context.Background(),
		"INSERT INTO admins (login, password) VALUES ($1, $2) RETURNING id",
		login, password,
	).Scan(&adminID)
	if err != nil {
		t.Fatalf("failed to create test admin: %v", err)
	}

	gotID, gotPassword, err := repository.Login(context.Background(), login)
	if err != nil {
		t.Fatalf("Login() returned an unexpected error: %v", err)
	}
	if gotID != adminID || gotPassword != password {
		t.Fatalf("Login() returned id %d and password %q, expected %d and %q", gotID, gotPassword, adminID, password)
	}
}

func TestLogin_InvalidCredentials(t *testing.T) {
	repository := setupTest(t)
	_, err := repository.pool.Exec(
		context.Background(),
		"INSERT INTO admins (login, password) VALUES ($1, $2)",
		"example_login", "example_password",
	)
	if err != nil {
		t.Fatalf("failed to create test admin: %v", err)
	}

	_, _, err = repository.Login(context.Background(), "another_login")
	if !errors.Is(err, domain.ErrInvalidCredentials) {
		t.Fatalf("Login() error = %v, expected %v", err, domain.ErrInvalidCredentials)
	}
}
