package domain

import "time"

type Comment struct {
	Id        int       `json:"comment_id"`
	Content   string    `json:"content"`
	CreatedAt time.Time `json:"created_at"`
}
