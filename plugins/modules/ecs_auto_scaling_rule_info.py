#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_auto_scaling_rule_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_auto_scaling_rule_info
short_description: Query ECS Auto Scaling rules.
description:
  - Retrieve information about Alibaba Cloud ECS Auto Scaling rules.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  scaling_group_id:
    description: Scaling group ID.
    type: str
  scaling_rule_id:
    description: Filter by scaling rule ID.
    type: str
  scaling_rule_name:
    description: Filter by scaling rule name.
    type: str
"""

EXAMPLES = r"""
- name: Query all Auto Scaling rules
  stevefulme1.alibaba_cloud.ecs_auto_scaling_rule_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    scaling_group_id: asg-123

- name: Query specific Auto Scaling rule
  stevefulme1.alibaba_cloud.ecs_auto_scaling_rule_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    scaling_rule_id: asr-123
"""

RETURN = r"""
ecs_auto_scaling_rules:
  description: List of Auto Scaling rules.
  returned: success
  type: list
  elements: dict
  sample:
    - scaling_rule_id: asr-123
      scaling_rule_name: scale-out-rule
      scaling_rule_ari: ari:acs:ess:cn-hangzhou:123:scalingrule/asr-123
      scaling_group_id: asg-123
      adjustment_type: QuantityChangeInCapacity
      adjustment_value: 2
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        scaling_group_id=dict(type="str"),
        scaling_rule_id=dict(type="str"),
        scaling_rule_name=dict(type="str"),
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

    params = {}
    if module.params.get("scaling_group_id"):
        params["ScalingGroupId"] = module.params["scaling_group_id"]
    if module.params.get("scaling_rule_id"):
        params["ScalingRuleId"] = module.params["scaling_rule_id"]
    if module.params.get("scaling_rule_name"):
        params["ScalingRuleName"] = module.params["scaling_rule_name"]

    try:
        result = client.get(
            "DescribeScalingRules",
            params,
            service_endpoint="ess.aliyuncs.com",
            api_version="2014-08-28",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "ScalingRules.ScalingRule".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, ecs_auto_scaling_rules=data)


if __name__ == "__main__":
    main()
