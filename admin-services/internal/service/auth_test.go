package service

import (
	"context"
	"new_prog/internal/domain"
	"testing"

	"golang.org/x/crypto/bcrypt"
)

type authRepositoryStub struct {
	receivedLogin string
	receivedHash  []byte
	receivedErr   error
}

func (a *authRepositoryStub) Register(ctx context.Context, login string, password []byte) error {
	a.receivedLogin = login
	a.receivedHash = password
	return a.receivedErr
}

func (a *authRepositoryStub) Login(ctx context.Context, login string) (int, string, error) {
	return 1, a.receivedLogin, a.receivedErr
}

func TestRegister(t *testing.T) {
	repository := &authRepositoryStub{}
	service := NewAuthService(repository)
	admin := domain.Admin{Login: "Gera", Password: "Vera"}
	err := service.Register(context.Background(), admin)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if repository.receivedLogin != admin.Login {
		t.Errorf(
			"expected login %q, got %q",
			admin.Login,
			repository.receivedLogin,
		)
	}
	if string(repository.receivedHash) == admin.Password {
		t.Fatal("repository received plain-text password")
	}

	err = bcrypt.CompareHashAndPassword(
		repository.receivedHash,
		[]byte(admin.Password),
	)
	if err != nil {
		t.Fatalf("repository received invalid password hash: %v", err)
	}
}
