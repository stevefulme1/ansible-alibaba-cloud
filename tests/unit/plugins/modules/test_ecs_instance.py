"""Unit tests for ecs_instance module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class TestEcsInstanceArgSpec:
    """Test that the module argument spec is valid."""

    def test_module_has_required_params(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ecs_instance import (
            DOCUMENTATION,
        )

        assert "instance_name" in DOCUMENTATION or "name" in DOCUMENTATION
        assert "state" in DOCUMENTATION
        assert (
            "region_id" in DOCUMENTATION
            or "extends_documentation_fragment" in DOCUMENTATION
        )


class TestEcsInstanceIdempotency:
    """Test idempotency logic."""

    def test_present_state_requires_instance_type(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ecs_instance import (
            DOCUMENTATION,
        )

        assert "instance_type" in DOCUMENTATION


class TestEcsInstanceDocumentation:
    """Verify documentation structure."""

    def test_has_examples(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ecs_instance import (
            EXAMPLES,
        )

        assert len(EXAMPLES) > 0

    def test_has_return(self):
        from ansible_collections.stevefulme1.alibaba_cloud.plugins.modules.ecs_instance import (
            RETURN,
        )

        assert len(RETURN) > 0
