"""Unit tests for vpc module."""

from __future__ import annotations


class TestVpcDocumentation:
    """Verify VPC module documentation structure."""

    def test_has_documentation(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.vpc import (
            DOCUMENTATION,
        )

        assert "vpc_name" in DOCUMENTATION or "name" in DOCUMENTATION
        assert "cidr_block" in DOCUMENTATION

    def test_has_examples(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.vpc import (
            EXAMPLES,
        )

        assert "stevefulme1.alibaba_cloud" in EXAMPLES

    def test_has_return(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.vpc import (
            RETURN,
        )

        assert len(RETURN) > 0


class TestVpcInfoDocumentation:
    """Verify VPC info module documentation."""

    def test_has_documentation(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.vpc_info import (
            DOCUMENTATION,
        )

        assert len(DOCUMENTATION) > 0

    def test_has_return(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.vpc_info import (
            RETURN,
        )

        assert "vpcs" in RETURN or "resources" in RETURN
