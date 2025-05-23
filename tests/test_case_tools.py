"""Tests for the case management tools."""

import unittest
from unittest.mock import MagicMock, patch

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.tools.case_tools import (
    ListCasesParams,
    list_cases,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


class TestCaseTools(unittest.TestCase):
    """Tests for case management tools."""

    def setUp(self):
        self.config = ServerConfig(
            instance_url="https://example.service-now.com",
            auth=AuthConfig(
                type=AuthType.BASIC,
                basic=BasicAuthConfig(username="admin", password="password"),
            ),
        )
        self.auth_manager = AuthManager(self.config.auth)
        self.auth_manager.get_headers = MagicMock(return_value={"Authorization": "Basic"})

    @patch("servicenow_mcp.tools.case_tools.requests.get")
    def test_list_cases_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "result": [
                {
                    "sys_id": "case1",
                    "number": "CASE001",
                    "short_description": "Test case",
                    "state": "open",
                    "priority": "1",
                    "assigned_to": {"display_value": "Agent"},
                }
            ]
        }
        mock_get.return_value = mock_response

        params = ListCasesParams(limit=1)
        result = list_cases(self.config, self.auth_manager, params)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["cases"]), 1)
        self.assertEqual(result["cases"][0]["number"], "CASE001")


if __name__ == "__main__":
    unittest.main()
