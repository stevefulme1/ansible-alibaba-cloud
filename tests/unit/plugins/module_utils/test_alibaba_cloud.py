"""Unit tests for the Alibaba Cloud API client."""

from __future__ import annotations

from unittest.mock import MagicMock

from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


class TestAlibabaArgumentSpec:
    def test_has_required_keys(self):
        assert "access_key_id" in alibaba_argument_spec
        assert "access_key_secret" in alibaba_argument_spec
        assert "region_id" in alibaba_argument_spec

    def test_secret_is_no_log(self):
        assert alibaba_argument_spec["access_key_secret"]["no_log"] is True

    def test_security_token_present(self):
        assert "security_token" in alibaba_argument_spec


class TestAlibabaCloudClient:
    def test_client_init(self):
        client = AlibabaCloudClient("key-id", "key-secret", "cn-hangzhou")
        assert client.access_key_id == "key-id"
        assert client.region_id == "cn-hangzhou"

    def test_client_init_with_security_token(self):
        client = AlibabaCloudClient(
            "key-id", "key-secret", "cn-hangzhou", security_token="sts"
        )
        assert client.security_token == "sts"


class TestAlibabaCloudError:
    def test_error_message(self):
        err = AlibabaCloudError("Something failed")
        assert str(err) == "Something failed"

    def test_error_with_code(self):
        err = AlibabaCloudError("Failed", code="InvalidParameter")
        assert err.code == "InvalidParameter"
