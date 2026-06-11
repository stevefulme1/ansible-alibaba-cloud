#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_security_group_rule_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_security_group_rule_info
short_description: Query ECS security group rules.
description:
  - Retrieve information about Alibaba Cloud ECS security group rules.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  security_group_id:
    description: Security group ID.
    type: str
    required: true
  direction:
    description: Filter by rule direction.
    type: str
    choices: [ingress, egress]
  nic_type:
    description: Filter by NIC type.
    type: str
    choices: [internet, intranet]
"""

EXAMPLES = r"""
- name: Query all security group rules
  stevefulme1.alibaba_cloud.ecs_security_group_rule_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    security_group_id: sg-123

- name: Query ingress security group rules
  stevefulme1.alibaba_cloud.ecs_security_group_rule_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    security_group_id: sg-123
    direction: ingress
"""

RETURN = r"""
ecs_security_group_rules:
  description: List of security group rules.
  returned: success
  type: list
  elements: dict
  sample:
    - security_group_rule_id: sgr-123
      ip_protocol: TCP
      port_range: 22/22
      source_cidr_ip: 0.0.0.0/0
      direction: ingress
      policy: Accept
      priority: 1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        security_group_id=dict(type="str", required=True),
        direction=dict(type="str", choices=["ingress", "egress"]),
        nic_type=dict(type="str", choices=["internet", "intranet"]),
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

    params = {
        "SecurityGroupId": module.params["security_group_id"],
    }
    if module.params.get("direction"):
        params["Direction"] = module.params["direction"]
    if module.params.get("nic_type"):
        params["NicType"] = module.params["nic_type"]

    try:
        result = client.get(
            "DescribeSecurityGroupAttribute",
            params,
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Permissions.Permission".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, ecs_security_group_rules=data)


if __name__ == "__main__":
    main()
