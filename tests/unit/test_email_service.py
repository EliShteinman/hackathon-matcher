from unittest.mock import MagicMock

import pytest

from config.email_settings import EmailSettings
from src.email_templates.template_renderer import TemplateRenderer
from src.models.user import User
from src.services.email_service import EmailService


@pytest.fixture
def email_settings():
    return EmailSettings(enabled=False)


@pytest.fixture
def mock_renderer():
    renderer = MagicMock(spec=TemplateRenderer)
    renderer.render_match_request.return_value = "<html>request</html>"
    renderer.render_match_approved.return_value = "<html>approved</html>"
    renderer.render_match_rejected.return_value = "<html>rejected</html>"
    renderer.render_match_cancelled.return_value = "<html>cancelled</html>"
    return renderer


@pytest.fixture
def email_service(email_settings, mock_renderer):
    return EmailService(email_settings, mock_renderer)


@pytest.fixture
def alice():
    return User(id=1, id_number="111", email="alice@t.com", full_name="Alice", branch="TLV")


@pytest.fixture
def bob():
    return User(id=2, id_number="222", email="bob@t.com", full_name="Bob", branch="JLM")


class TestEmailServiceDisabled:
    async def test_send_match_request(self, email_service, mock_renderer, alice, bob):
        await email_service.send_match_request(alice, bob, "uuid-123", "http://localhost:8000")
        mock_renderer.render_match_request.assert_called_once()

    async def test_send_match_approved(self, email_service, mock_renderer, alice, bob):
        await email_service.send_match_approved(alice, bob)
        mock_renderer.render_match_approved.assert_called_once()

    async def test_send_match_rejected(self, email_service, mock_renderer, alice, bob):
        await email_service.send_match_rejected(alice, bob)
        mock_renderer.render_match_rejected.assert_called_once()

    async def test_send_match_cancelled(self, email_service, mock_renderer, alice, bob):
        await email_service.send_match_cancelled(alice, bob)
        mock_renderer.render_match_cancelled.assert_called_once()
