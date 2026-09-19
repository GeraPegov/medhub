package service

import (
	"context"
	"errors"
	"testing"
)

type limiterRepositoryStub struct {
	articleNumber int64
	articleErr    error
	commentNumber int64
	commentErr    error
}

func (s *limiterRepositoryStub) LimiterArticle(
	ctx context.Context,
	userID string,
) (int64, error) {
	return s.articleNumber, s.articleErr
}

func (s *limiterRepositoryStub) LimiterComment(
	ctx context.Context,
	userID string,
	articleID string,
) (int64, error) {
	return s.commentNumber, s.commentErr
}

func TestLimiterService_GetIncrementLimiterArticle_AllowsRequest(t *testing.T) {
	// Arrange
	repository := &limiterRepositoryStub{
		articleNumber: 3,
	}
	service := NewLimiterService(repository)

	// Act
	result, err := service.GetIncrementLimiterArticle(
		context.Background(),
		"user-42",
	)

	// Assert
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result != 1 {
		t.Errorf("expected result 1, got %d", result)
	}
}

func TestLimiterService_GetIncrementLimiterComment_AllowRequest(t *testing.T) {
	repository := &limiterRepositoryStub{
		commentNumber: 10,
	}
	service := NewLimiterService(repository)

	result, err := service.GetIncrementLimiterComment(
		context.Background(),
		"3",
		"3",
	)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result != 1 {
		t.Errorf("expected result 1, got %d", result)
	}
}

func TestLimiterService_GetIncrementLimiterArticle_BlocksRequest(t *testing.T) {
	repository := &limiterRepositoryStub{
		articleNumber: 4,
	}
	service := NewLimiterService(repository)

	result, err := service.GetIncrementLimiterArticle(
		context.Background(),
		"3",
	)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result != 0 {
		t.Errorf("expected result 0, got %d", result)
	}
}

func TestLimiterService_GetIncrementLimiterComment_BlocksRequest(t *testing.T) {
	repository := &limiterRepositoryStub{
		commentNumber: 11,
	}
	service := NewLimiterService(repository)

	result, err := service.GetIncrementLimiterComment(
		context.Background(),
		"3",
		"3",
	)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result != 0 {
		t.Errorf("expected result 0, got %d", result)
	}
}

func TestLimiterService_GetIncrementLimiterArticle_ReturnsRepositoryError(t *testing.T) {
	wantErr := errors.New("redis unavailable")
	repository := &limiterRepositoryStub{
		articleErr: wantErr,
	}
	service := NewLimiterService(repository)

	_, err := service.GetIncrementLimiterArticle(
		context.Background(),
		"3",
	)
	if !errors.Is(err, wantErr) {
		t.Fatalf("expected error %v, got %v", wantErr, err)
	}
}

func TestLimiterService_GetIncrementLimiterComment_ReturnsRepositoryError(t *testing.T) {
	wantErr := errors.New("redis unavailable")
	repository := &limiterRepositoryStub{
		commentErr: wantErr,
	}
	service := NewLimiterService(repository)

	_, err := service.GetIncrementLimiterComment(
		context.Background(),
		"3",
		"3",
	)
	if !errors.Is(err, wantErr) {
		t.Fatalf("expected error %v, got %v", wantErr, err)
	}
}
