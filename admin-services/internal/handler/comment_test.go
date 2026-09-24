package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"new_prog/internal/domain"
	"testing"
	"time"
)

func TestGetComments_searchForArticleID_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}

	handler := NewAdminHandler(service)
	articleID := 1
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/comments?article_id=%d", articleID),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetComments(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultComments[0].ArticleID != articleID {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.Comment
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].ArticleID != articleID {
		t.Fatalf("Returned %d, excepted %d", bodyResponse[0].ArticleID, articleID)
	}
}

func TestGetComments_searchForUserId_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	userId := 1
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/comments?user_id=%d", userId),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetComments(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultComments[0].UserID != userId {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.Comment
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].UserID != userId {
		t.Fatalf("Returned %d, excepted %d", bodyResponse[0].UserID, userId)
	}
}

func TestGetComments_searchForDate_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	date := time.Now().Format("2006-01-02")
	date_from_db, err := time.Parse("2006-01-02", date)
	if err != nil {
		t.Fatalf("Failed for parse Date, %e", err)
	}
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/comments?public_date=%s", date),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetComments(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultComments[0].CreatedAt != date_from_db {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.Comment
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].CreatedAt != date_from_db {
		t.Fatalf("Returned %s, excepted %s", bodyResponse[0].CreatedAt, date)
	}
}

func TestGetComment_return_BadRequest(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	r := httptest.NewRequest(
		http.MethodGet,
		"/admin/comments?article_id=one",
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetComments(w, r)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("Status code = %d, excepeted = %d", w.Code, http.StatusBadRequest)
	}
}

func TestDeleteComment_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/comments/1",
		nil,
	)
	r.SetPathValue("id", "1")
	w := httptest.NewRecorder()

	handler.DeleteComment(w, r)

	if w.Code != http.StatusNoContent {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNoContent)
	}

	if service.commentId != 1 {
		t.Fatalf("DeleteComment() returning %d, excepted 1", service.commentId)
	}
}

func TestDeleteComment_return_StatusBadRequest(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/comments/1",
		nil,
	)
	r.SetPathValue("comment_id", "1")
	w := httptest.NewRecorder()

	handler.DeleteComment(w, r)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNoContent)
	}
}

func TestDeleteComment_return_StatusNotFound(t *testing.T) {
	service := &adminServiceStub{
		errComments: domain.ErrRowsNotFound,
	}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/comments/1",
		nil,
	)
	r.SetPathValue("id", "1")
	w := httptest.NewRecorder()

	handler.DeleteComment(w, r)

	if w.Code != http.StatusNotFound {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNotFound)
	}
}
