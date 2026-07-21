package domain

import "time"

type Comment struct {
	Id         int
	Content    string
	Created_at time.Time
}
