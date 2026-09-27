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

func TestGetArticles_searchForID_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}

	handler := NewAdminHandler(service)
	articleId := 1
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/articles?article_id=%d", articleId),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetArticles(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultArticles[0].Id != articleId {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.Article
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].Id != articleId {
		t.Fatalf("Returned %d, excepted %d", bodyResponse[0].Id, articleId)
	}
}

func TestGetArticles_searchForUserId_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	userId := 1
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/articles?user_id=%d", userId),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetArticles(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultArticles[0].UserID != userId {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.Article
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].UserID != userId {
		t.Fatalf("Returned %d, excepted %d", bodyResponse[0].UserID, userId)
	}
}

func TestGetArticles_searchForTitle_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	title := "example_title"
	r := httptest.NewRequest(
		http.MethodGet,
		fmt.Sprintf("/admin/articles?title=%s", title),
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetArticles(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	if service.resultArticles[0].Title != title {
		t.Fatalf("Send wrong data in service")
	}
	var bodyResponse []domain.Article
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if bodyResponse[0].Title != title {
		t.Fatalf("Returned %s, excepted %s", bodyResponse[0].Title, title)
	}
}

func TestGetArticlesSearchByDate(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)
	publicationDate := "2026-09-27"
	request := httptest.NewRequest(
		http.MethodGet,
		"/admin/articles?public_date="+publicationDate,
		nil,
	)
	responseRecorder := httptest.NewRecorder()

	handler.GetArticles(responseRecorder, request)

	if responseRecorder.Code != http.StatusOK {
		t.Fatalf("status code = %d, expected %d", responseRecorder.Code, http.StatusOK)
	}
	if len(service.resultArticles) != 1 {
		t.Fatalf("service received %d matching articles, expected 1", len(service.resultArticles))
	}
	expectedDate, err := time.Parse("2006-01-02", publicationDate)
	if err != nil {
		t.Fatalf("parse expected date: %v", err)
	}
	if !service.resultArticles[0].CreatedAt.Equal(expectedDate) {
		t.Errorf(
			"service received date %s, expected %s",
			service.resultArticles[0].CreatedAt.Format("2006-01-02"),
			publicationDate,
		)
	}
}

func TestGetArticlesRejectsInvalidDate(t *testing.T) {
	handler := NewAdminHandler(&adminServiceStub{})
	request := httptest.NewRequest(
		http.MethodGet,
		"/admin/articles?public_date=27-09-2026",
		nil,
	)
	responseRecorder := httptest.NewRecorder()

	handler.GetArticles(responseRecorder, request)

	if responseRecorder.Code != http.StatusBadRequest {
		t.Fatalf("status code = %d, expected %d", responseRecorder.Code, http.StatusBadRequest)
	}
}

func TestGetArticle_return_BadRequest(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)

	r := httptest.NewRequest(
		http.MethodGet,
		"/admin/articles?article_id=one",
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetArticles(w, r)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("Status code = %d, excepeted = %d", w.Code, http.StatusBadRequest)
	}
}

func TestDeleteArticle_return_StatusNoContent(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/articles/1",
		nil,
	)
	r.SetPathValue("id", "1")
	w := httptest.NewRecorder()

	handler.DeleteArticle(w, r)

	if w.Code != http.StatusNoContent {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNoContent)
	}

	if service.articleId != 1 {
		t.Fatalf("DeleteArticle() returning %d, excepted 1", service.articleId)
	}
}

func TestDeleteArticle_return_StatusBadRequest(t *testing.T) {
	service := &adminServiceStub{}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/articles/1",
		nil,
	)
	r.SetPathValue("article_id", "1")
	w := httptest.NewRecorder()

	handler.DeleteArticle(w, r)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNoContent)
	}
}

func TestDeleteArticle_return_StatusNotFound(t *testing.T) {
	service := &adminServiceStub{
		errArticles: domain.ErrRowsNotFound,
	}
	handler := NewAdminHandler(service)
	r := httptest.NewRequest(
		http.MethodPost,
		"/admin/articles/1",
		nil,
	)
	r.SetPathValue("id", "1")
	w := httptest.NewRecorder()

	handler.DeleteArticle(w, r)

	if w.Code != http.StatusNotFound {
		t.Fatalf("Status code = %d, excepted = %d", w.Code, http.StatusNoContent)
	}
}
