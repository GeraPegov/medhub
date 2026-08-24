package domain

import "errors"

var (
	ErrAdminAlreadyExists = errors.New("admin already exists")
	ErrDatabase           = errors.New("database error")
	ErrInvalidCredentials = errors.New("invalid credentails")
	ErrRowsNotFound       = errors.New("rows not found")
)
