package service

import (
	"context"
	"new_prog/internal/domain"
	"testing"

	"golang.org/x/crypto/bcrypt"
)

type authRepositoryStub struct {
	receivedId             int
	receivedLogin          string
	receivedHash           []byte
	receivedErr            error
	receivedPasswordFromDb string
}

func (a *authRepositoryStub) Register(ctx context.Context, login string, password []byte) error {
	a.receivedLogin = login
	a.receivedHash = password
	return a.receivedErr
}

func (a *authRepositoryStub) Login(ctx context.Context, login string) (int, string, error) {
	return a.receivedId, a.receivedPasswordFromDb, a.receivedErr
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

func TestLogin(t *testing.T) {
	hash, err := bcrypt.GenerateFromPassword(
		[]byte("Vera"),
		bcrypt.DefaultCost,
	)
	if err != nil {
		t.Fatal(err)
	}
	repository := &authRepositoryStub{
		receivedId:             1,
		receivedPasswordFromDb: string(hash),
	}
	service := NewAuthService(repository)

	admin := domain.Admin{Login: "Gera", Password: "Vera"}
	token, err := service.Login(context.Background(), admin)
	if err != nil {
		t.Fatalf("user failed access login, %v", err)
	}

	claims, err := ValidateToken(token)
	if err != nil || claims.UserID <= 0 {
		t.Fatal("token failed validation")
	}
}
