package postgres

import (
	"context"
	"fmt"
	"testing"
	"time"
)

func TestQuantityArticles(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)

	dateFrom := time.Date(2026, time.January, 1, 12, 0, 0, 0, time.UTC)
	dateTo := time.Date(2026, time.January, 3, 12, 0, 0, 0, time.UTC)
	for i := 0; i < 3; i++ {
		email := fmt.Sprintf("example%d@mail.com", i)
		username := fmt.Sprintf("username%d", i)
		createTestArticle(t, repository, email, username, createdAt)
	}

	number, err := repository.QuantityArticles(context.Background(), dateFrom, dateTo)
	if err != nil {
		t.Fatalf("QuantityArticles() returned an unexpected error: %v", err)
	}
	if number != 3 {
		t.Fatalf("QuantityArticles() = %d, expected 3", number)
	}
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
