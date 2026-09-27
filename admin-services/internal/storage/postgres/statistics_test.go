package postgres

import (
	"context"
	"fmt"
	"testing"
	"time"
)

func TestStatisticsQuantityArticles(t *testing.T) {
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

func TestStatisticsQuantityUsers(t *testing.T) {
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

func TestPopularityStatisticsFilterByDate(t *testing.T) {
	repository := setupTest(t)
	dateFrom := time.Date(2026, time.January, 1, 0, 0, 0, 0, time.UTC)
	dateTo := time.Date(2026, time.January, 3, 0, 0, 0, 0, time.UTC)

	createTestArticle(t, repository, "first@mail.com", "first", dateFrom)
	createTestArticle(t, repository, "second@mail.com", "second", dateTo.Add(-time.Second))
	createTestArticle(t, repository, "excluded@mail.com", "excluded", dateTo)

	categories, err := repository.PopularityCategory(context.Background(), dateFrom, dateTo)
	if err != nil {
		t.Fatalf("PopularityCategory() returned an unexpected error: %v", err)
	}
	if len(categories) != 1 {
		t.Fatalf("PopularityCategory() returned %d categories, expected 1", len(categories))
	}
	if categories[0].Category != "test category" || categories[0].Quantity != 2 {
		t.Errorf("PopularityCategory() = %#v, expected category %q with quantity 2", categories[0], "test category")
	}

	authors, err := repository.PopularityAuthors(context.Background(), dateFrom, dateTo)
	if err != nil {
		t.Fatalf("PopularityAuthors() returned an unexpected error: %v", err)
	}
	if len(authors) != 2 {
		t.Fatalf("PopularityAuthors() returned %d authors, expected 2", len(authors))
	}

	usernames := make(map[string]struct{}, len(authors))
	for _, author := range authors {
		usernames[author.Username] = struct{}{}
		if author.Quantity != 1 {
			t.Errorf("PopularityAuthors() returned quantity %d for %q, expected 1", author.Quantity, author.Username)
		}
	}
	for _, expectedUsername := range []string{"first", "second"} {
		if _, ok := usernames[expectedUsername]; !ok {
			t.Errorf("PopularityAuthors() did not return %q", expectedUsername)
		}
	}
	if _, ok := usernames["excluded"]; ok {
		t.Error("PopularityAuthors() returned an author outside the requested date range")
	}
}

func TestPopularityStatisticsReturnEmptySlices(t *testing.T) {
	repository := setupTest(t)
	dateFrom := time.Date(2026, time.January, 1, 0, 0, 0, 0, time.UTC)
	dateTo := time.Date(2026, time.January, 3, 0, 0, 0, 0, time.UTC)

	categories, err := repository.PopularityCategory(context.Background(), dateFrom, dateTo)
	if err != nil {
		t.Fatalf("PopularityCategory() returned an unexpected error: %v", err)
	}
	if categories == nil || len(categories) != 0 {
		t.Errorf("PopularityCategory() = %#v, expected a non-nil empty slice", categories)
	}

	authors, err := repository.PopularityAuthors(context.Background(), dateFrom, dateTo)
	if err != nil {
		t.Fatalf("PopularityAuthors() returned an unexpected error: %v", err)
	}
	if authors == nil || len(authors) != 0 {
		t.Errorf("PopularityAuthors() = %#v, expected a non-nil empty slice", authors)
	}
}
