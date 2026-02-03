package service

import (
    "context"
    "fmt"
    "time"
)

type Storage interface {
    IncrementCounter(ctx context.Context, key string, ttl time.Duration) (int64, error)
    GetCounter(ctx context.Context, key string) (int64, error)
}

type LimiterService struct {
    storage Storage
}

func NewLimiterService(storage Storage) *LimiterService {
    return &LimiterService{storage: storage}
}

type CheckLimitRequest struct {
    UserID int64  `json:"user_id" binding:"required"`
    Action string `json:"action" binding:"required"`
    Limit  int64  `json:"limit" binding:"required,min=1"`
}

type CheckLimitResponse struct {
    Allowed    bool  `json:"allowed"`
    Current    int64 `json:"current"`
    Limit      int64 `json:"limit"`
    RetryAfter int64 `json:"retry_after,omitempty"`
}

func (s *LimiterService) CheckAndIncrement(ctx context.Context, req CheckLimitRequest) (*CheckLimitResponse, error) {
    key := s.generateKey(req.UserID, req.Action)

    current, err := s.storage.GetCounter(ctx, key)
    if err != nil {
        return nil, fmt.Errorf("failed to check limit: %w", err)
    }

    if current >= req.Limit {
        return &CheckLimitResponse{
            Allowed:    false,
            Current:    current,
            Limit:      req.Limit,
            RetryAfter: s.getSecondsUntilMidnight(),
        }, nil
    }

    newCount, err := s.storage.IncrementCounter(ctx, key, 24*time.Hour)
    if err != nil {
        return nil, fmt.Errorf("failed to increment counter: %w", err)
    }

    return &CheckLimitResponse{
        Allowed: true,
        Current: newCount,
        Limit:   req.Limit,
    }, nil
}

func (s *LimiterService) generateKey(userID int64, action string) string {
    date := time.Now().UTC().Format("2006-01-02")
    return fmt.Sprintf("limit:user:%d:%s:%s", userID, action, date)
}

func (s *LimiterService) getSecondsUntilMidnight() int64 {
    now := time.Now().UTC()
    midnight := time.Date(now.Year(), now.Month(), now.Day()+1, 0, 0, 0, 0, time.UTC)
    return int64(midnight.Sub(now).Seconds())
}
