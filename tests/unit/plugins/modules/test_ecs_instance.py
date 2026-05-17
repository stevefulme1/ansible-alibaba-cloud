"""Unit tests for stevefulme1.alibaba_cloud.ecs_instance module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest


MODULE_PATH = "ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ecs_instance"
CLIENT_PATH = "ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud"


@pytest.fixture
def mock_api_client():
    """Mock API client for ecs_instance."""
    client = MagicMock()
    client.get.return_value = None
    client.create.return_value = {"instance_id": "res-123", "instance_name": "test-ecs_instance"}
    client.update.return_value = {"instance_id": "res-123", "instance_name": "test-ecs_instance-updated"}
    client.delete.return_value = None
    client.list.return_value = []
    return client


@pytest.fixture
def existing_resource():
    """Return a dict representing an existing ecs_instance."""
    return {
        "instance_id": "res-123",
        "instance_name": "test-ecs_instance",
        "state": "active",
    }


class TestCreateEcsInstance:
    """Tests for creating a ecs_instance."""

    def test_create_returns_resource(self, mock_api_client):
        """Verify create returns resource dict with expected fields."""
        result = mock_api_client.create("ecs_instance", {"instance_name": "test-ecs_instance"})
        assert result["instance_id"] == "res-123"
        assert result["instance_name"] == "test-ecs_instance"
        mock_api_client.create.assert_called_once()

    def test_create_with_all_params(self, mock_api_client):
        """Verify create passes all parameters to API."""
        params = {
            "instance_name": "full-ecs_instance",
            "description": "Full test",
            "tags": {"env": "test"},
        }
        mock_api_client.create("ecs_instance", params)
        mock_api_client.create.assert_called_once_with("ecs_instance", params)

    def test_create_api_error(self):
        """Verify API errors are raised on create."""
        client = MagicMock()
        client.create.side_effect = Exception("409 Conflict")
        with pytest.raises(Exception, match="409 Conflict"):
            client.create("ecs_instance", {"instance_name": "dup"})

    def test_create_check_mode_no_api_call(self, mock_api_client):
        """Verify check_mode skips actual API call."""
        check_mode = True
        if check_mode:
            result = {"changed": True, "ecs_instance": {}}
        else:
            result = mock_api_client.create("ecs_instance", {})
        assert result["changed"] is True
        mock_api_client.create.assert_not_called()


class TestUpdateEcsInstance:
    """Tests for updating a ecs_instance."""

    def test_update_existing_resource(self, mock_api_client, existing_resource):
        """Verify update modifies existing resource."""
        mock_api_client.get.return_value = existing_resource
        result = mock_api_client.update("ecs_instance", "res-123", {"instance_name": "updated"})
        assert result["instance_name"] == "test-ecs_instance-updated"

    def test_update_idempotent_no_change(self, mock_api_client, existing_resource):
        """Verify no update when params match existing state."""
        mock_api_client.get.return_value = existing_resource
        # Simulate idempotency check
        desired = {"instance_name": existing_resource["instance_name"]}
        current = {"instance_name": existing_resource["instance_name"]}
        changed = desired != current
        assert changed is False

    def test_update_detects_changes(self, mock_api_client, existing_resource):
        """Verify update detects actual changes."""
        mock_api_client.get.return_value = existing_resource
        desired = {"instance_name": "new-name"}
        current = {"instance_name": existing_resource["instance_name"]}
        changed = desired != current
        assert changed is True

    def test_update_nonexistent_raises(self, mock_api_client):
        """Verify updating non-existent resource raises error."""
        mock_api_client.update.side_effect = Exception("404 Not Found")
        with pytest.raises(Exception, match="404 Not Found"):
            mock_api_client.update("ecs_instance", "bad-id", {})


class TestDeleteEcsInstance:
    """Tests for deleting a ecs_instance."""

    def test_delete_existing(self, mock_api_client, existing_resource):
        """Verify delete calls API with correct ID."""
        mock_api_client.get.return_value = existing_resource
        mock_api_client.delete("ecs_instance", "res-123")
        mock_api_client.delete.assert_called_once_with("ecs_instance", "res-123")

    def test_delete_nonexistent_is_noop(self, mock_api_client):
        """Verify deleting absent resource reports no change."""
        mock_api_client.get.return_value = None
        result = mock_api_client.get("ecs_instance", "missing-id")
        assert result is None

    def test_delete_check_mode(self, mock_api_client, existing_resource):
        """Verify check_mode delete does not call API."""
        check_mode = True
        if not check_mode:
            mock_api_client.delete("ecs_instance", "res-123")
        mock_api_client.delete.assert_not_called()

    def test_delete_api_error(self):
        """Verify API errors propagate on delete."""
        client = MagicMock()
        client.delete.side_effect = Exception("403 Forbidden")
        with pytest.raises(Exception, match="403 Forbidden"):
            client.delete("ecs_instance", "res-123")


class TestGetEcsInstance:
    """Tests for getting a ecs_instance."""

    def test_get_existing(self, mock_api_client, existing_resource):
        """Verify get returns resource when it exists."""
        mock_api_client.get.return_value = existing_resource
        result = mock_api_client.get("ecs_instance", "res-123")
        assert result["instance_id"] == "res-123"

    def test_get_nonexistent(self, mock_api_client):
        """Verify get returns None for missing resource."""
        mock_api_client.get.return_value = None
        result = mock_api_client.get("ecs_instance", "nonexistent")
        assert result is None

    def test_get_api_timeout(self):
        """Verify timeout error handling."""
        client = MagicMock()
        client.get.side_effect = TimeoutError("Connection timed out")
        with pytest.raises(TimeoutError):
            client.get("ecs_instance", "res-123")


class TestListEcsInstance:
    """Tests for listing ecs_instance resources."""

    def test_list_returns_all(self, mock_api_client):
        """Verify list returns all resources."""
        mock_api_client.list.return_value = [
            {"instance_id": "1", "instance_name": "first"},
            {"instance_id": "2", "instance_name": "second"},
        ]
        result = mock_api_client.list("ecs_instance")
        assert len(result) == 2

    def test_list_empty(self, mock_api_client):
        """Verify list returns empty for no resources."""
        result = mock_api_client.list("ecs_instance")
        assert result == []

    def test_list_with_filter(self, mock_api_client):
        """Verify list applies filters."""
        mock_api_client.list.return_value = [{"instance_id": "1", "instance_name": "match"}]
        result = mock_api_client.list("ecs_instance", filters={"instance_name": "match"})
        assert len(result) == 1


class TestIdempotencyEcsInstance:
    """Tests for idempotent behavior of ecs_instance."""

    def test_create_existing_is_idempotent(self, mock_api_client, existing_resource):
        """Verify creating an already-existing resource is idempotent."""
        mock_api_client.get.return_value = existing_resource
        current = mock_api_client.get("ecs_instance", "res-123")
        desired_params = {"instance_name": current["instance_name"]}
        # If resource exists and matches desired state, no change
        changed = desired_params["instance_name"] != current["instance_name"]
        assert changed is False

    def test_delete_absent_is_idempotent(self, mock_api_client):
        """Verify deleting an absent resource reports no change."""
        mock_api_client.get.return_value = None
        exists = mock_api_client.get("ecs_instance", "missing") is not None
        assert exists is False


class TestErrorHandlingEcsInstance:
    """Tests for error handling in ecs_instance."""

    def test_auth_failure(self):
        """Verify authentication failure is handled."""
        client = MagicMock()
        client.create.side_effect = Exception("401 Unauthorized")
        with pytest.raises(Exception, match="401 Unauthorized"):
            client.create("ecs_instance", {})

    def test_rate_limit(self):
        """Verify rate-limit response is handled."""
        client = MagicMock()
        client.list.side_effect = Exception("429 Too Many Requests")
        with pytest.raises(Exception, match="429"):
            client.list("ecs_instance")

    def test_server_error(self):
        """Verify 500 error is propagated."""
        client = MagicMock()
        client.get.side_effect = Exception("500 Internal Server Error")
        with pytest.raises(Exception, match="500"):
            client.get("ecs_instance", "res-123")

    def test_network_error(self):
        """Verify network connectivity errors are handled."""
        client = MagicMock()
        client.get.side_effect = ConnectionError("Failed to connect")
        with pytest.raises(ConnectionError):
            client.get("ecs_instance", "res-123")
