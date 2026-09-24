package postgres

import (
	"context"
	"errors"
	"fmt"
	"new_prog/internal/domain"
	"testing"
	"time"

	"github.com/jackc/pgx/v5"
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

func TestSearchArticles_Success(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	articleID, userID := createTestArticle(
		t,
		repository,
		"example@mail.com",
		"username",
		createdAt,
	)

	filterOneExample := domain.ArticleFilter{
		Title: "title",
	}
	filterTwoExample := domain.ArticleFilter{
		ID: &articleID,
	}
	filterThreeExample := domain.ArticleFilter{
		UserID: &userID,
	}

	oneExample, err := repository.SearchArticles(context.Background(), filterOneExample)
	if err != nil {
		t.Fatalf("SearchArticles() by title returned an unexpected error: %v", err)
	}
	assertSingleArticle(t, oneExample, articleID, userID)

	twoExample, err := repository.SearchArticles(context.Background(), filterTwoExample)
	if err != nil {
		t.Fatalf("SearchArticles() by ID returned an unexpected error: %v", err)
	}
	assertSingleArticle(t, twoExample, articleID, userID)

	threeExample, err := repository.SearchArticles(context.Background(), filterThreeExample)
	if err != nil {
		t.Fatalf("SearchArticles() by user ID returned an unexpected error: %v", err)
	}
	assertSingleArticle(t, threeExample, articleID, userID)
}

func assertSingleArticle(
	t *testing.T,
	articles []domain.Article,
	articleID int,
	userID int,
) {
	t.Helper()

	if len(articles) != 1 {
		t.Fatalf("SearchArticles() returned %d articles, expected 1", len(articles))
	}

	article := articles[0]
	if article.Id != articleID || article.Title != "title example" || article.UserID != userID {
		t.Fatalf("SearchArticles() returned an unexpected article: %+v", article)
	}
}

func TestArticlesByDate(t *testing.T) {
	repository := setupTest(t)
	targetTime := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	otherTime := time.Date(2026, time.January, 3, 12, 0, 0, 0, time.UTC)
	expectedIDs := make(map[int]struct{}, 3)

	for i := 0; i < 3; i++ {
		articleID, _ := createTestArticle(
			t,
			repository,
			fmt.Sprintf("dated%d@mail.com", i),
			fmt.Sprintf("dated_user%d", i),
			targetTime,
		)
		expectedIDs[articleID] = struct{}{}
	}

	createTestArticle(
		t,
		repository,
		"other-date@mail.com",
		"other_date_user",
		otherTime,
	)

	date := targetTime.Format("2006-01-02")
	articles, err := repository.ArticlesByDate(context.Background(), date)
	if err != nil {
		t.Fatalf("ArticlesByDate(%q) returned an unexpected error: %v", date, err)
	}
	if len(articles) != len(expectedIDs) {
		t.Fatalf("ArticlesByDate(%q) returned %d articles, expected %d", date, len(articles), len(expectedIDs))
	}
	for _, article := range articles {
		if _, ok := expectedIDs[article.Id]; !ok {
			t.Fatalf("ArticlesByDate(%q) returned unexpected article ID %d", date, article.Id)
		}
		if article.CreatedAt.Format("2006-01-02") != date {
			t.Fatalf("ArticlesByDate(%q) returned article with date %q", date, article.CreatedAt.Format("2006-01-02"))
		}
	}
}

func TestDeleteArticle_Success(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	articleID, _ := createTestArticle(
		t,
		repository,
		"example@mail.com",
		"username",
		createdAt,
	)

	err := repository.DeleteArticle(context.Background(), articleID)
	if err != nil {
		t.Fatalf("DeleteArticle() returned an unexpected error: %v", err)
	}

	var foundArticleID int
	err = repository.pool.QueryRow(
		context.Background(),
		"SELECT id FROM articles WHERE id = $1",
		articleID,
	).Scan(&foundArticleID)
	if !errors.Is(err, pgx.ErrNoRows) {
		t.Fatalf("article %d still exists or verification query failed: %v", articleID, err)
	}
}

func TestDeleteArticle_NotFound(t *testing.T) {
	repository := setupTest(t)

	err := repository.DeleteArticle(context.Background(), 1)
	if !errors.Is(err, domain.ErrRowsNotFound) {
		t.Fatalf("DeleteArticle() error = %v, expected %v", err, domain.ErrRowsNotFound)
	}
}
