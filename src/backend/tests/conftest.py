"""
Global test configuration for Wi$h Li$t backend.

This conftest.py runs before any test module is imported.
It mocks all third-party modules that require real credentials
or native C extensions so that unit and API tests can run
without a real Supabase connection, Groq API key, or browser TLS stack.
"""

import os
import sys
from unittest.mock import MagicMock

# ------------------------------------------------------------------ #
# 1. Inject fake env vars before dotenv/supabase is ever imported     #
# ------------------------------------------------------------------ #
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-api-key-placeholder-0000")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key-placeholder")

# ------------------------------------------------------------------ #
# 2. Create a real exception class for postgrest APIError             #
#    (needed because it appears in `except` clauses)                  #
# ------------------------------------------------------------------ #
class FakeAPIError(Exception):
    def __init__(self, message: str = "", code: str = None):
        super().__init__(message)
        self.code = code

# ------------------------------------------------------------------ #
# 3. Stub out third-party modules before any app code is imported     #
# ------------------------------------------------------------------ #

# supabase client
_mock_supabase = MagicMock()
_mock_supabase.create_client.return_value = MagicMock()
sys.modules["supabase"] = _mock_supabase

# postgrest (used by repositories for APIError)
_mock_postgrest = MagicMock()
_mock_postgrest.exceptions.APIError = FakeAPIError
sys.modules["postgrest"] = _mock_postgrest

_mock_postgrest_exc = MagicMock()
_mock_postgrest_exc.APIError = FakeAPIError
sys.modules["postgrest.exceptions"] = _mock_postgrest_exc

# curl_cffi (used by all scrapers for TLS impersonation)
_mock_curl_cffi = MagicMock()
sys.modules["curl_cffi"] = _mock_curl_cffi
sys.modules["curl_cffi.requests"] = MagicMock()

# groq (used by LLMScraper)
_mock_groq = MagicMock()
sys.modules["groq"] = _mock_groq

# apscheduler (used by scheduler.py)
sys.modules["apscheduler"] = MagicMock()
sys.modules["apscheduler.schedulers"] = MagicMock()
sys.modules["apscheduler.schedulers.background"] = MagicMock()
sys.modules["apscheduler.triggers"] = MagicMock()
sys.modules["apscheduler.triggers.interval"] = MagicMock()

# ------------------------------------------------------------------ #
# 4. Shared pytest fixtures                                           #
# ------------------------------------------------------------------ #

import pytest
from uuid import uuid4
from datetime import datetime
from app.schemas.category_schema import Category, CategoryCustom
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.user_schema import UserCreate, UserRead


@pytest.fixture
def user_id():
    """A stable UUID representing a test user."""
    return uuid4()


@pytest.fixture
def sample_category(user_id):
    return Category(
        id=uuid4(),
        name="Technology",
        user_id=user_id,
        category_type="TECHNOLOGY",
    )


@pytest.fixture
def sample_custom_category():
    return CategoryCustom(name="Books", category_type="BOOKS")


@pytest.fixture
def sample_product_create():
    return ProductCreate(
        name="Test Laptop",
        url="https://www.hepsiburada.com/laptop-p-12345",
        priority="medium",
        check_frequency="daily",
        auto_track=True,
        current_price=15999.99,
    )


@pytest.fixture
def sample_product_response(user_id):
    return ProductResponse(
        id=uuid4(),
        user_id=user_id,
        name="Test Laptop",
        url="https://www.hepsiburada.com/laptop-p-12345",
        priority="medium",
        check_frequency="daily",
        auto_track=True,
        current_price=15999.99,
        purchase_state="pending",
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_user_read():
    return UserRead(
        id=uuid4(),
        first_name="Ali",
        last_name="Veli",
        email="ali@example.com",
        created_at=datetime.now(),
    )
