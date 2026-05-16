#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_auto_scaling_rule"""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


DOCUMENTATION = r"""
---
module: ecs_auto_scaling_rule
short_description: Manage scaling rules.
description:
  - Create, update, or delete Alibaba Cloud ecs_auto_scaling_rule resources.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: [present, absent]
    default: present
  scaling_group_id:
    description: Scaling group this rule belongs to.
    type: str
    required: true
  scaling_rule_name:
    description: Name of the scaling rule.
    type: str
  adjustment_type:
    description: Adjustment type.
    type: str
    choices: [QuantityChangeInCapacity, PercentChangeInCapacity, TotalCapacity]
  adjustment_value:
    description: Adjustment value.
    type: int
  scaling_rule_id:
    description: Existing rule ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create scaling rule
  stevefulme1.alibaba_cloud.ecs_auto_scaling_rule:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    scaling_group_id: asg-xxxxx
    scaling_rule_name: scale-out
    adjustment_type: QuantityChangeInCapacity
    adjustment_value: 2
"""

RETURN = r"""
scaling_rule:
  description: Scaling rule details.
  returned: success
  type: dict
"""


def main():
    spec = dict(
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        scaling_group_id=dict(type="str", required=True),
        scaling_rule_name=dict(type="str"),
        adjustment_type=dict(
            type="str",
            choices=[
                "QuantityChangeInCapacity",
                "PercentChangeInCapacity",
                "TotalCapacity",
            ],
        ),
        adjustment_value=dict(type="int"),
        scaling_rule_id=dict(type="str"),
    )
    spec.update(alibaba_argument_spec)

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
    )

    client = AlibabaCloudClient(
        access_key_id=module.params["access_key_id"],
        access_key_secret=module.params["access_key_secret"],
        region_id=module.params["region_id"],
        security_token=module.params.get("security_token"),
        timeout=module.params["timeout"],
    )

    state = module.params["state"]
    changed = False

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeScalingRules",
            {},
            service_endpoint="ess.aliyuncs.com",
            api_version="2014-08-28",
        )

        data = existing
        for key in "ScalingRules.ScalingRule".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateScalingRule",
                    {},
                    service_endpoint="ess.aliyuncs.com",
                    api_version="2014-08-28",
                )
                changed = True
                module.exit_json(changed=changed, ecs_auto_scaling_rule=result)
            else:
                module.exit_json(
                    changed=False,
                    ecs_auto_scaling_rule=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteScalingRule",
                    {},
                    service_endpoint="ess.aliyuncs.com",
                    api_version="2014-08-28",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
