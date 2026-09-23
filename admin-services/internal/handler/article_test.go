package handler

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"new_prog/internal/domain"
	"testing"
)

func TestGetArticles(t *testing.T) {
	article := domain.Article{
		Id: 1,
	}
	articles := []domain.Article{}
	articles = append(articles, article)

	service := &adminServiceStub{
		resultArticles: articles,
	}

	handler := NewAdminHandler(service)

	r := httptest.NewRequest(
		http.MethodGet,
		"/admin/articles?article_id=1",
		nil,
	)
	w := httptest.NewRecorder()

	handler.GetArticles(w, r)

	if w.Code != http.StatusOK {
		t.Fatalf("response code = %d, excepted = %d", w.Code, http.StatusOK)
	}
	var bodyResponse []domain.Article
	if err := json.Unmarshal(w.Body.Bytes(), &bodyResponse); err != nil {
		t.Fatalf("decode response body: %v", err)
	}
	if len(bodyResponse) != len(articles) {
		t.Fatalf(
			"returned %d articles, expected %d",
			len(bodyResponse),
			len(articles),
		)
	}
	if bodyResponse[0].Id != articles[0].Id {
		t.Fatalf("Returned %d, excepted %d", bodyResponse[0].Id, articles[0].Id)
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
