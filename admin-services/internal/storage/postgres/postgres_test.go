package postgres

import (
	"context"
	"log/slog"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
)

var pool *pgxpool.Pool

func truncateRecords(ctx context.Context, pool *pgxpool.Pool) error {
	_, err := pool.Exec(ctx, `
        TRUNCATE TABLE
            reactions,
            comments,
            articles,
            users,
            admins
        RESTART IDENTITY CASCADE
    `)
	return err
}

func setupTest(t *testing.T) *Repository {
	t.Helper()

	ctx := context.Background()
	if err := truncateRecords(ctx, pool); err != nil {
		t.Fatalf("failed to prepare test database: %v", err)
	}

	t.Cleanup(func() {
		if err := truncateRecords(ctx, pool); err != nil {
			t.Errorf("failed to clean test database: %v", err)
		}
	})

	return &Repository{pool: pool}
}

func createTestComment(
	t *testing.T,
	repository *Repository,
	content string,
	userId int,
	articleId int,
	createdAt time.Time,
) int {
	t.Helper()
	var id int
	err := repository.pool.QueryRow(context.Background(), `
		INSERT INTO comments (
			content,
			created_at,
			user_id,
			article_id
		) VALUES (
			$1,
			$2,
			$3,
			$4
		) RETURNING id
	`, content, createdAt, userId, articleId).Scan(&id)
	if err != nil {
		t.Fatalf("failed to create test comment: %v", err)
	}
	return id
}

func createTestArticle(
	t *testing.T,
	repository *Repository,
	email string,
	username string,
	createdAt time.Time,
) (int, int) {
	t.Helper()

	var articleID int
	var userID int
	err := repository.pool.QueryRow(context.Background(), `
			WITH new_user AS (
				INSERT INTO users (
					email,
					nickname,
					unique_username,
					password_hash
				)
				VALUES (
					$1,
					'test',
					$2,
					'test_hash'
				)
				RETURNING id
			)
			INSERT INTO articles (
				title,
				content,
				user_id,
				category,
				created_at
			)
			SELECT
				'title example',
				'test content',
				id,
				'test category',
				$3
			FROM new_user
			RETURNING id, user_id
		`, email, username, createdAt).Scan(&articleID, &userID)
	if err != nil {
		t.Fatalf("failed to create test article: %v", err)
	}

	return articleID, userID
}

func TestMain(m *testing.M) {
	ctx := context.Background()
	_ = godotenv.Load(".env.tests")

	databaseURL := os.Getenv("TEST_DB_URL")
	if databaseURL == "" {
		slog.Error("TEST_DB_URL is not set")
		os.Exit(1)
	}

	var err error
	pool, err = pgxpool.New(ctx, databaseURL)
	if err != nil {
		slog.Error("failed to create test pool", "error", err)
		os.Exit(1)
	}
	if err := pool.Ping(ctx); err != nil {
		slog.Error("failed to ping test database", "error", err)
		pool.Close()
		os.Exit(1)
	}

	exitCode := m.Run()

	if err := truncateRecords(ctx, pool); err != nil {
		slog.Error("failed to clean test database", "error", err)
		exitCode = 1
	}
	pool.Close()
	os.Exit(exitCode)
}
