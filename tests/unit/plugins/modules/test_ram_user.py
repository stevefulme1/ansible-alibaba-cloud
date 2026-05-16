"""Unit tests for ram_user module."""

from __future__ import annotations


class TestRamUserDocumentation:
    """Verify RAM user module documentation."""

    def test_has_documentation(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ram_user import (
            DOCUMENTATION,
        )

        assert "user_name" in DOCUMENTATION or "name" in DOCUMENTATION
        assert "state" in DOCUMENTATION

    def test_has_examples(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ram_user import (
            EXAMPLES,
        )

        assert "stevefulme1.alibaba_cloud" in EXAMPLES


class TestRamUserInfoDocumentation:
    def test_has_documentation(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ram_user_info import (
            DOCUMENTATION,
        )

        assert len(DOCUMENTATION) > 0


class TestRamPolicyDocumentation:
    def test_has_documentation(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ram_policy import (
            DOCUMENTATION,
        )

        assert "policy_name" in DOCUMENTATION or "name" in DOCUMENTATION
