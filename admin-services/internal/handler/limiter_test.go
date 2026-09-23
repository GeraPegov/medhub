package handler

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

type limiterServiceStub struct {
	articleResult int
	articleErr    error

	receivedUserId    string
	receivedArticleId string

	commentResult int
	commentErr    error
}

func (l *limiterServiceStub) GetIncrementLimiterArticle(ctx context.Context, userId string) (int, error) {
	l.receivedUserId = userId
	return l.articleResult, l.articleErr
}

func (l *limiterServiceStub) GetIncrementLimiterComment(ctx context.Context, userId string, articleId string) (int, error) {
	l.receivedArticleId = articleId
	l.receivedUserId = userId
	return l.commentResult, l.commentErr
}

func TestLimiterArticle(t *testing.T) {
	service := &limiterServiceStub{
		articleResult: 1,
	}
	handler := NewLimiterHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/limiter/1/articles",
		nil,
	)
	r.SetPathValue("user_id", "1")

	w := httptest.NewRecorder()

	handler.LimiterArticle(w, r)

	if w.Code != http.StatusNoContent {
		t.Errorf("status = %d, expected %d", w.Code, http.StatusNoContent)
	}
	if service.receivedUserId != "1" {
		t.Errorf(
			"userID = %q, expected %q",
			service.receivedUserId,
			"1",
		)
	}
}

func TestLimiterComment(t *testing.T) {
	service := &limiterServiceStub{
		commentResult: 1,
	}
	handler := NewLimiterHandler(service)

	r := httptest.NewRequest(
		http.MethodPost,
		"/limiter/1/1/comments",
		nil,
	)
	r.SetPathValue("user_id", "1")
	r.SetPathValue("article_id", "1")
	w := httptest.NewRecorder()

	handler.LimiterComment(w, r)

	if w.Code != http.StatusNoContent {
		t.Errorf("status = %d, expected %d", w.Code, http.StatusNoContent)
	}
	if service.receivedArticleId != "1" {
		t.Errorf(
			"userID = %q, expected %q",
			service.receivedArticleId,
			"1",
		)
	}
	if service.receivedUserId != "1" {
		t.Errorf(
			"userID = %q, expected %q",
			service.receivedUserId,
			"1",
		)
	}
}
