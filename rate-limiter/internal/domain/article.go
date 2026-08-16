package domain

import "time"

type Article struct {
	Id         int
	Title      string
	User_id    int
	Created_at time.Time
}

type StatArticles struct {
	Value int
	Err   string
}
