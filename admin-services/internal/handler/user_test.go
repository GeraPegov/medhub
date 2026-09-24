package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"new_prog/internal/domain"
	"testing"
)

func TestGetUsers_searchForUserID_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}

	handler := NewAdminHandler(service)
	userID := 1
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/users?user_id=%d", userID),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetUsers(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultUsers[0].Id != userID {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.User
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].Id != userID {
		t.Fatalf("Returned %d, excepted %d", bodyResponse[0].Id, userID)
	}
}

func TestGetUsers_searchForUsername_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	username := "username"
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/Users?username=%s", username),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetUsers(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultUsers[0].UniqueUsername != username {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.User
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].UniqueUsername != username {
		t.Fatalf("Returned %s, excepted %s", bodyResponse[0].UniqueUsername, username)
	}
}

func TestGetUsers_searchForEmail_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	email := "email@example.tu"
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/users?email=%s", email),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetUsers(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultUsers[0].Email != email {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.User
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].Email != email {
		t.Fatalf("Returned %s, excepted %s", bodyResponse[0].Email, email)
	}
}

func TestGetUser_return_BadRequest(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	r := httptest.NewRequest(
		http.MethodGet,
		"/admin/users?user_id=one",
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetUsers(w, r)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("Status code = %d, excepeted = %d", w.Code, http.StatusBadRequest)
	}
}

func TestDeleteUser_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/users/1",
		nil,
	)
	r.SetPathValue("id", "1")
	w := httptest.NewRecorder()

	handler.DeleteComment(w, r)

	if w.Code != http.StatusNoContent {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNoContent)
	}

	if service.commentId != 1 {
		t.Fatalf("DeleteUser() returning %d, excepted 1", service.userId)
	}
}

func TestDeleteUser_return_StatusBadRequest(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/users/1",
		nil,
	)
	r.SetPathValue("user_id", "1")
	w := httptest.NewRecorder()

	handler.DeleteComment(w, r)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNoContent)
	}
}

func TestDeleteUser_return_StatusNotFound(t *testing.T) {
	service := &adminServiceStub{
		errUsers: domain.ErrRowsNotFound,
	}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/users/1",
		nil,
	)
	r.SetPathValue("id", "1")
	w := httptest.NewRecorder()

	handler.DeleteUser(w, r)

	if w.Code != http.StatusNotFound {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNotFound)
	}
}
