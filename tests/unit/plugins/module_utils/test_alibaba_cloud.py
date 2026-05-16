"""Unit tests for the Alibaba Cloud API client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


class TestAlibabaArgumentSpec:
    def test_has_required_keys(self):
        spec = alibaba_argument_spec()
        assert "access_key_id" in spec
        assert "access_key_secret" in spec
        assert "region_id" in spec

    def test_secret_is_no_log(self):
        spec = alibaba_argument_spec()
        assert spec["access_key_secret"]["no_log"] is True

    def test_security_token_optional(self):
        spec = alibaba_argument_spec()
        assert spec["security_token"]["required"] is False


class TestAlibabaCloudClient:
    def _make_module(self, **kwargs):
        module = MagicMock()
        params = {
            "access_key_id": "test-key-id",
            "access_key_secret": "test-key-secret",
            "region_id": "cn-hangzhou",
            "security_token": None,
            "timeout": 30,
        }
        params.update(kwargs)
        module.params = params
        return module

    def test_client_init(self):
        module = self._make_module()
        client = AlibabaCloudClient(module)
        assert client.access_key_id == "test-key-id"
        assert client.region_id == "cn-hangzhou"

    def test_client_init_with_security_token(self):
        module = self._make_module(security_token="sts-token")
        client = AlibabaCloudClient(module)
        assert client.security_token == "sts-token"


class TestAlibabaCloudError:
    def test_error_message(self):
        err = AlibabaCloudError("Something failed")
        assert str(err) == "Something failed"

    def test_error_with_code(self):
        err = AlibabaCloudError("Failed", error_code="InvalidParameter")
        assert err.error_code == "InvalidParameter"
