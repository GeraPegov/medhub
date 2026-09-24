package domain

import "time"

type Comment struct {
	Id        int       `json:"comment_id"`
	UserID    int       `json:"user_id"`
	ArticleID int       `json:"article_id"`
	Content   string    `json:"content"`
	CreatedAt time.Time `json:"created_at"`
}
