package domain

import "time"

type UserFilter struct {
	ID       *int
	Email    string
	Username string
}

type ArticleFilter struct {
	ID     *int
	UserID *int
	Title  string
}

type CommentFilter struct {
	ArticleID *int
	UserID    *int
	Date      *time.Time
}
