package postgres

import (
	"context"
	"errors"
	"fmt"
	"new_prog/internal/domain"
	"testing"
	"time"
)

func createTestUser(t *testing.T, repository *Repository, email, username string, registeredAt time.Time) int {
	t.Helper()

	var id int
	err := repository.pool.QueryRow(context.Background(), `
		INSERT INTO users (email, nickname, unique_username, password_hash, registration_date)
		VALUES ($1, 'test', $2, 'test_hash', $3)
		RETURNING id
	`, email, username, registeredAt).Scan(&id)
	if err != nil {
		t.Fatalf("failed to create test user: %v", err)
	}
	return id
}

func TestQuantityUsers(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)

	dateFrom := time.Date(2026, time.January, 1, 12, 0, 0, 0, time.UTC)
	dateTo := time.Date(2026, time.January, 3, 12, 0, 0, 0, time.UTC)
	for i := 0; i < 3; i++ {
		email := fmt.Sprintf("example%d@mail.com", i)
		username := fmt.Sprintf("username%d", i)
		createTestUser(t, repository, email, username, createdAt)
	}

	number, err := repository.QuantityUsers(context.Background(), dateFrom, dateTo)
	if err != nil {
		t.Fatalf("QuantityUsers() returned an unexpected error: %v", err)
	}
	if number != 3 {
		t.Fatalf("QuantityUsers() = %d, expected 3", number)
	}
}

func TestSearchUsers_Success(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	userID := createTestUser(t, repository, "example@mail.com", "username", createdAt)
	createTestUser(t, repository, "other@mail.com", "other_username", createdAt)

	filterOneExample := domain.UserFilter{
		Email: "example@mail.com",
	}
	filterTwoExample := domain.UserFilter{
		ID: &userID,
	}
	filterThreeExample := domain.UserFilter{
		Username: "username",
	}

	oneExample, err := repository.SearchUsers(context.Background(), filterOneExample)
	if err != nil {
		t.Fatalf("SearchUsers() by email returned an unexpected error: %v", err)
	}
	assertSingleUser(t, oneExample, userID)

	twoExample, err := repository.SearchUsers(context.Background(), filterTwoExample)
	if err != nil {
		t.Fatalf("SearchUsers() by ID returned an unexpected error: %v", err)
	}
	assertSingleUser(t, twoExample, userID)

	threeExample, err := repository.SearchUsers(context.Background(), filterThreeExample)
	if err != nil {
		t.Fatalf("SearchUsers() by username returned an unexpected error: %v", err)
	}
	assertSingleUser(t, threeExample, userID)
}

func assertSingleUser(t *testing.T, users []domain.User, userID int) {
	t.Helper()

	if len(users) != 1 {
		t.Fatalf("SearchUsers() returned %d users, expected 1", len(users))
	}

	user := users[0]
	if user.Id != userID || user.Email != "example@mail.com" || user.UniqueUsername != "username" {
		t.Fatalf("SearchUsers() returned an unexpected user: %+v", user)
	}
}

func TestDeleteUser_Success(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	userID := createTestUser(t, repository, "example@mail.com", "username", createdAt)

	err := repository.DeleteUser(context.Background(), userID)
	if err != nil {
		t.Fatalf("DeleteUser() returned an unexpected error: %v", err)
	}

	var isDeleted bool
	err = repository.pool.QueryRow(
		context.Background(),
		"SELECT is_deleted FROM users WHERE id = $1",
		userID,
	).Scan(&isDeleted)
	if err != nil {
		t.Fatalf("failed to verify deleted user %d: %v", userID, err)
	}
	if !isDeleted {
		t.Fatalf("user %d was not marked as deleted", userID)
	}
}

func TestDeleteUser_NotFound(t *testing.T) {
	repository := setupTest(t)

	err := repository.DeleteUser(context.Background(), 1)
	if !errors.Is(err, domain.ErrRowsNotFound) {
		t.Fatalf("DeleteUser() error = %v, expected %v", err, domain.ErrRowsNotFound)
	}
}

func TestUsersByDate(t *testing.T) {
	repository := setupTest(t)
	targetTime := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	otherTime := time.Date(2026, time.January, 3, 12, 0, 0, 0, time.UTC)
	expectedIDs := make(map[int]struct{}, 3)

	for i := 0; i < 3; i++ {
		userID := createTestUser(
			t,
			repository,
			fmt.Sprintf("dated%d@mail.com", i),
			fmt.Sprintf("dated_user%d", i),
			targetTime,
		)
		expectedIDs[userID] = struct{}{}
	}

	createTestUser(t, repository, "other-date@mail.com", "other_date_user", otherTime)

	date := targetTime.Format("2006-01-02")
	users, err := repository.UsersByDate(context.Background(), date)
	if err != nil {
		t.Fatalf("UsersByDate(%q) returned an unexpected error: %v", date, err)
	}
	if len(users) != len(expectedIDs) {
		t.Fatalf("UsersByDate(%q) returned %d users, expected %d", date, len(users), len(expectedIDs))
	}
	for _, user := range users {
		if _, ok := expectedIDs[user.Id]; !ok {
			t.Fatalf("UsersByDate(%q) returned unexpected user ID %d", date, user.Id)
		}
		if user.RegistrationDate.Format("2006-01-02") != date {
			t.Fatalf("UsersByDate(%q) returned user with date %q", date, user.RegistrationDate.Format("2006-01-02"))
		}
	}
}
