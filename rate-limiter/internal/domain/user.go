package domain

import "time"

type User struct {
	Id               int
	Email            string
	UniqueUsername   string
	RegistrationDate time.Time
}
