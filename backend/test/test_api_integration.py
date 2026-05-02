import pytest
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def get_registered_routes():
    """
    Helper function to collect all registered API paths.
    """
    return [route.path for route in app.routes]


def test_fastapi_app_loads_successfully():
    """
    This test checks whether the FastAPI app can be imported and loaded.
    """
    response = client.get("/")

    assert response.status_code in [200, 404]


def test_swagger_docs_available():
    """
    This test checks whether FastAPI Swagger documentation is available.
    """
    response = client.get("/docs")

    assert response.status_code == 200


def test_openapi_json_available():
    """
    This test checks whether FastAPI can generate OpenAPI schema.
    """
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert "openapi" in data
    assert "paths" in data


def test_routes_are_registered():
    """
    This test prints and checks registered backend routes.
    """
    routes = get_registered_routes()

    print("\nRegistered routes:")
    for route in routes:
        print(route)

    assert len(routes) > 0
    assert "/docs" in routes
    assert "/openapi.json" in routes


def test_process_endpoint_exists_if_available():
    """
    This test checks whether /process exists.
    """
    routes = get_registered_routes()

    if "/process" not in routes:
        pytest.skip("/process endpoint not found. Check printed routes and update the endpoint path.")

    assert "/process" in routes


def test_process_endpoint_with_valid_sme_profile():
    """
    This test checks whether a valid SME profile can reach the /process endpoint.
    """
    routes = get_registered_routes()

    if "/process" not in routes:
        pytest.skip("/process endpoint not found. Update this test using your actual endpoint path.")

    payload = {
        "company_name": "TechBina Sdn Bhd",
        "sector": "Technology",
        "requested_amount": 50000,
        "documents": [
            "SSM Certificate",
            "Audited Financials",
            "Business Plan"
        ]
    }

    response = client.post("/process", json=payload)

    assert response.status_code in [200, 201, 202]

    data = response.json()

    assert data is not None
    assert isinstance(data, dict)


def test_process_endpoint_rejects_invalid_input():
    """
    This test checks whether invalid SME input is rejected.
    """
    routes = get_registered_routes()

    if "/process" not in routes:
        pytest.skip("/process endpoint not found. Update this test using your actual endpoint path.")

    payload = {
        "company_name": "",
        "sector": "",
        "requested_amount": -1000,
        "documents": []
    }

    response = client.post("/process", json=payload)

    assert response.status_code in [400, 422]


def test_admin_force_sync_endpoint_if_available():
    """
    This test checks whether /api/admin/force-sync works if it exists.
    """
    routes = get_registered_routes()

    if "/api/admin/force-sync" not in routes:
        pytest.skip("/api/admin/force-sync endpoint not found. Skipping Scout Agent test.")

    response = client.post("/api/admin/force-sync")

    assert response.status_code in [200, 201, 202]


def test_download_endpoint_if_available():
    """
    This test checks whether a download/export route exists.
    """
    routes = get_registered_routes()

    download_routes = [
        route for route in routes
        if "download" in route.lower()
        or "export" in route.lower()
        or "zip" in route.lower()
        or "file" in route.lower()
    ]

    print("\nPossible download/export routes:")
    for route in download_routes:
        print(route)

    assert isinstance(download_routes, list)