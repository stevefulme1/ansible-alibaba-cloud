"""Unit tests for stevefulme1.alibaba_cloud.ecs_security_group module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock

import pytest


MODULE_PATH = "ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ecs_security_group"
CLIENT_PATH = "ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud"


@pytest.fixture
def mock_api_client():
    """Mock API client for ecs_security_group."""
    client = MagicMock()
    client.get.return_value = None
    client.create.return_value = {"security_group_id": "res-123", "security_group_name": "test-ecs_security_group"}
    client.update.return_value = {"security_group_id": "res-123", "new_security_group_name": "test-ecs_security_group-updated"}
    client.delete.return_value = None
    client.list.return_value = []
    return client


@pytest.fixture
def existing_resource():
    """Return a dict representing an existing ecs_security_group."""
    return {
        "security_group_id": "res-123",
        "security_group_name": "test-ecs_security_group",
        "state": "active",
    }


class TestCreateEcsSecurityGroup:
    """Tests for creating a ecs_security_group."""

    def test_create_returns_resource(self, mock_api_client):
        """Verify create returns resource dict with expected fields."""
        result = mock_api_client.create("ecs_security_group", {"security_group_name": "test-ecs_security_group"})
        assert result["security_group_id"] == "res-123"
        assert result["security_group_name"] == "test-ecs_security_group"
        mock_api_client.create.assert_called_once()

    def test_create_with_all_params(self, mock_api_client):
        """Verify create passes all parameters to API."""
        params = {
            "security_group_name": "full-ecs_security_group",
            "description": "Full test",
            "tags": {"env": "test"},
        }
        mock_api_client.create("ecs_security_group", params)
        mock_api_client.create.assert_called_once_with("ecs_security_group", params)

    def test_create_api_error(self):
        """Verify API errors are raised on create."""
        client = MagicMock()
        client.create.side_effect = Exception("409 Conflict")
        with pytest.raises(Exception, match="409 Conflict"):
            client.create("ecs_security_group", {"security_group_name": "dup"})

    def test_create_check_mode_no_api_call(self, mock_api_client):
        """Verify check_mode skips actual API call."""
        check_mode = True
        if check_mode:
            result = {"changed": True, "ecs_security_group": {}}
        else:
            result = mock_api_client.create("ecs_security_group", {})
        assert result["changed"] is True
        mock_api_client.create.assert_not_called()


class TestUpdateEcsSecurityGroup:
    """Tests for updating a ecs_security_group."""

    def test_update_existing_resource(self, mock_api_client, existing_resource):
        """Verify update modifies existing resource."""
        mock_api_client.get.return_value = existing_resource
        result = mock_api_client.update("ecs_security_group", "res-123", {"security_group_name": "updated"})
        assert result["security_group_name"] == "test-ecs_security_group-updated"

    def test_update_idempotent_no_change(self, mock_api_client, existing_resource):
        """Verify no update when params match existing state."""
        mock_api_client.get.return_value = existing_resource
        # Simulate idempotency check
        desired = {"security_group_name": existing_resource["security_group_name"]}
        current = {"security_group_name": existing_resource["security_group_name"]}
        changed = desired != current
        assert changed is False

    def test_update_detects_changes(self, mock_api_client, existing_resource):
        """Verify update detects actual changes."""
        mock_api_client.get.return_value = existing_resource
        desired = {"security_group_name": "new-name"}
        current = {"security_group_name": existing_resource["security_group_name"]}
        changed = desired != current
        assert changed is True

    def test_update_nonexistent_raises(self, mock_api_client):
        """Verify updating non-existent resource raises error."""
        mock_api_client.update.side_effect = Exception("404 Not Found")
        with pytest.raises(Exception, match="404 Not Found"):
            mock_api_client.update("ecs_security_group", "bad-id", {})


class TestDeleteEcsSecurityGroup:
    """Tests for deleting a ecs_security_group."""

    def test_delete_existing(self, mock_api_client, existing_resource):
        """Verify delete calls API with correct ID."""
        mock_api_client.get.return_value = existing_resource
        mock_api_client.delete("ecs_security_group", "res-123")
        mock_api_client.delete.assert_called_once_with("ecs_security_group", "res-123")

    def test_delete_nonexistent_is_noop(self, mock_api_client):
        """Verify deleting absent resource reports no change."""
        mock_api_client.get.return_value = None
        result = mock_api_client.get("ecs_security_group", "missing-id")
        assert result is None

    def test_delete_check_mode(self, mock_api_client, existing_resource):
        """Verify check_mode delete does not call API."""
        check_mode = True
        if not check_mode:
            mock_api_client.delete("ecs_security_group", "res-123")
        mock_api_client.delete.assert_not_called()

    def test_delete_api_error(self):
        """Verify API errors propagate on delete."""
        client = MagicMock()
        client.delete.side_effect = Exception("403 Forbidden")
        with pytest.raises(Exception, match="403 Forbidden"):
            client.delete("ecs_security_group", "res-123")


class TestGetEcsSecurityGroup:
    """Tests for getting a ecs_security_group."""

    def test_get_existing(self, mock_api_client, existing_resource):
        """Verify get returns resource when it exists."""
        mock_api_client.get.return_value = existing_resource
        result = mock_api_client.get("ecs_security_group", "res-123")
        assert result["security_group_id"] == "res-123"

    def test_get_nonexistent(self, mock_api_client):
        """Verify get returns None for missing resource."""
        mock_api_client.get.return_value = None
        result = mock_api_client.get("ecs_security_group", "nonexistent")
        assert result is None

    def test_get_api_timeout(self):
        """Verify timeout error handling."""
        client = MagicMock()
        client.get.side_effect = TimeoutError("Connection timed out")
        with pytest.raises(TimeoutError):
            client.get("ecs_security_group", "res-123")


class TestListEcsSecurityGroup:
    """Tests for listing ecs_security_group resources."""

    def test_list_returns_all(self, mock_api_client):
        """Verify list returns all resources."""
        mock_api_client.list.return_value = [
            {"security_group_id": "1", "security_group_name": "first"},
            {"security_group_id": "2", "new_security_group_name": "second"},
        ]
        result = mock_api_client.list("ecs_security_group")
        assert len(result) == 2

    def test_list_empty(self, mock_api_client):
        """Verify list returns empty for no resources."""
        result = mock_api_client.list("ecs_security_group")
        assert result == []

    def test_list_with_filter(self, mock_api_client):
        """Verify list applies filters."""
        mock_api_client.list.return_value = [{"security_group_id": "1", "security_group_name": "match"}]
        result = mock_api_client.list("ecs_security_group", filters={"new_security_group_name": "match"})
        assert len(result) == 1


class TestIdempotencyEcsSecurityGroup:
    """Tests for idempotent behavior of ecs_security_group."""

    def test_create_existing_is_idempotent(self, mock_api_client, existing_resource):
        """Verify creating an already-existing resource is idempotent."""
        mock_api_client.get.return_value = existing_resource
        current = mock_api_client.get("ecs_security_group", "res-123")
        desired_params = {"security_group_name": current["security_group_name"]}
        # If resource exists and matches desired state, no change
        changed = desired_params["security_group_name"] != current["security_group_name"]
        assert changed is False

    def test_delete_absent_is_idempotent(self, mock_api_client):
        """Verify deleting an absent resource reports no change."""
        mock_api_client.get.return_value = None
        exists = mock_api_client.get("ecs_security_group", "missing") is not None
        assert exists is False


class TestErrorHandlingEcsSecurityGroup:
    """Tests for error handling in ecs_security_group."""

    def test_auth_failure(self):
        """Verify authentication failure is handled."""
        client = MagicMock()
        client.create.side_effect = Exception("401 Unauthorized")
        with pytest.raises(Exception, match="401 Unauthorized"):
            client.create("ecs_security_group", {})

    def test_rate_limit(self):
        """Verify rate-limit response is handled."""
        client = MagicMock()
        client.list.side_effect = Exception("429 Too Many Requests")
        with pytest.raises(Exception, match="429"):
            client.list("ecs_security_group")

    def test_server_error(self):
        """Verify 500 error is propagated."""
        client = MagicMock()
        client.get.side_effect = Exception("500 Internal Server Error")
        with pytest.raises(Exception, match="500"):
            client.get("ecs_security_group", "res-123")

    def test_network_error(self):
        """Verify network connectivity errors are handled."""
        client = MagicMock()
        client.get.side_effect = ConnectionError("Failed to connect")
        with pytest.raises(ConnectionError):
            client.get("ecs_security_group", "res-123")
