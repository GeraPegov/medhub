package domain

import "time"

type Article struct {
	Id        int       `json:"article_id"`
	Title     string    `json:"title"`
	UserID    int       `json:"user_id"`
	CreatedAt time.Time `json:"created_at"`
}
