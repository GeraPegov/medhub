package postgres

import (
	"context"
	"errors"
	"new_prog/internal/domain"
	"testing"
	"time"

	"github.com/jackc/pgx/v5"
)

func TestSearchComments(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	otherDate := createdAt.AddDate(0, 0, 1)
	articleID, userID := createTestArticle(t, repository, "example@mail.com", "example_username", createdAt)
	otherArticleID, otherUserID := createTestArticle(t, repository, "other@mail.com", "other_username", otherDate)
	commentID := createTestComment(t, repository, "example content", otherUserID, articleID, createdAt)
	createTestComment(t, repository, "other content", userID, otherArticleID, otherDate)

	filterOneExample := domain.CommentFilter{
		ArticleID: &articleID,
	}
	filterTwoExample := domain.CommentFilter{
		UserID: &otherUserID,
	}
	filterThreeExample := domain.CommentFilter{
		Date: &createdAt,
	}

	oneExample, err := repository.SearchComments(context.Background(), filterOneExample)
	if err != nil {
		t.Fatalf("SearchComments() by article ID returned an unexpected error: %v", err)
	}
	assertSingleComment(t, oneExample, commentID)

	twoExample, err := repository.SearchComments(context.Background(), filterTwoExample)
	if err != nil {
		t.Fatalf("SearchComments() by user ID returned an unexpected error: %v", err)
	}
	assertSingleComment(t, twoExample, commentID)

	threeExample, err := repository.SearchComments(context.Background(), filterThreeExample)
	if err != nil {
		t.Fatalf("SearchComments() by date returned an unexpected error: %v", err)
	}
	assertSingleComment(t, threeExample, commentID)
}

func assertSingleComment(t *testing.T, comments []domain.Comment, commentID int) {
	t.Helper()

	if len(comments) != 1 {
		t.Fatalf("SearchComments() returned %d comments, expected 1", len(comments))
	}

	comment := comments[0]
	if comment.Id != commentID || comment.Content != "example content" {
		t.Fatalf("SearchComments() returned an unexpected comment: %+v", comment)
	}
}

func TestDeleteComment_Success(t *testing.T) {
	repository := setupTest(t)
	createdAt := time.Date(2026, time.January, 2, 12, 0, 0, 0, time.UTC)
	articleId, userId := createTestArticle(t, repository, "example@mail.com", "example username", createdAt)
	commentId := createTestComment(
		t,
		repository,
		"example content",
		userId,
		articleId,
		createdAt,
	)

	err := repository.DeleteComment(context.Background(), commentId)
	if err != nil {
		t.Fatalf("DeleteComment() returned an unexpected error: %v", err)
	}

	var foundCommentID int
	err = repository.pool.QueryRow(
		context.Background(),
		"SELECT id FROM comments WHERE id = $1",
		commentId,
	).Scan(&foundCommentID)
	if !errors.Is(err, pgx.ErrNoRows) {
		t.Fatalf("comment %d still exists or verification query failed: %v", commentId, err)
	}
}

func TestDeleteComment_NotFound(t *testing.T) {
	repository := setupTest(t)

	err := repository.DeleteComment(context.Background(), 1)
	if !errors.Is(err, domain.ErrRowsNotFound) {
		t.Fatalf("DeleteComment() error = %v, expected %v", err, domain.ErrRowsNotFound)
	}
}
