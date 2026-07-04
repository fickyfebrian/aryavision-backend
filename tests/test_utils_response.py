import json

from app.utils.response import error_response, paginated_response, success_response


def body(response) -> dict:
    return json.loads(response.body)


class TestSuccessResponse:
    def test_default_status_and_shape(self):
        res = success_response(data={"id": 1}, message="ok")
        assert res.status_code == 200
        assert body(res) == {"success": True, "message": "ok", "data": {"id": 1}}

    def test_custom_status_code(self):
        res = success_response(data={"id": 1}, message="created", status_code=201)
        assert res.status_code == 201

    def test_defaults_when_no_args_given(self):
        res = success_response()
        payload = body(res)
        assert payload["success"] is True
        assert payload["message"] == "Success"
        assert payload["data"] is None


class TestErrorResponse:
    def test_default_status_and_shape(self):
        res = error_response(message="boom")
        assert res.status_code == 500
        payload = body(res)
        assert payload == {"success": False, "message": "boom"}

    def test_omits_errors_key_when_not_provided(self):
        res = error_response(message="boom")
        assert "errors" not in body(res)

    def test_includes_errors_key_when_provided(self):
        res = error_response(message="boom", status_code=400, errors={"field": "bad"})
        payload = body(res)
        assert payload["errors"] == {"field": "bad"}
        assert res.status_code == 400


class TestPaginatedResponse:
    def test_pagination_metadata_middle_page(self):
        res = paginated_response(items=[1, 2], total_items=25, page=2, limit=10)
        payload = body(res)["data"]["pagination"]
        assert payload == {
            "page": 2,
            "limit": 10,
            "total_items": 25,
            "total_pages": 3,
            "has_next": True,
            "has_previous": True,
        }

    def test_pagination_metadata_first_page(self):
        res = paginated_response(items=[], total_items=25, page=1, limit=10)
        payload = body(res)["data"]["pagination"]
        assert payload["has_previous"] is False
        assert payload["has_next"] is True

    def test_pagination_metadata_last_page(self):
        res = paginated_response(items=[], total_items=25, page=3, limit=10)
        payload = body(res)["data"]["pagination"]
        assert payload["has_next"] is False
        assert payload["has_previous"] is True

    def test_zero_limit_does_not_divide_by_zero(self):
        res = paginated_response(items=[], total_items=0, page=1, limit=0)
        payload = body(res)["data"]["pagination"]
        assert payload["total_pages"] == 1
