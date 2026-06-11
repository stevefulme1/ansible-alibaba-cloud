#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_auto_scaling_group_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_auto_scaling_group_info
short_description: Query ECS Auto Scaling groups.
description:
  - Retrieve information about Alibaba Cloud ECS Auto Scaling groups.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  scaling_group_id:
    description: Filter by scaling group ID.
    type: str
  scaling_group_name:
    description: Filter by scaling group name.
    type: str
"""

EXAMPLES = r"""
- name: Query all Auto Scaling groups
  stevefulme1.alibaba_cloud.ecs_auto_scaling_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific Auto Scaling group
  stevefulme1.alibaba_cloud.ecs_auto_scaling_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    scaling_group_id: asg-123
"""

RETURN = r"""
ecs_auto_scaling_groups:
  description: List of Auto Scaling groups.
  returned: success
  type: list
  elements: dict
  sample:
    - scaling_group_id: asg-123
      scaling_group_name: web-asg
      min_size: 2
      max_size: 10
      total_capacity: 5
      lifecycle_state: Active
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
        scaling_group_name=dict(type="str"),
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
    if module.params.get("scaling_group_name"):
        params["ScalingGroupName"] = module.params["scaling_group_name"]

    try:
        result = client.get(
            "DescribeScalingGroups",
            params,
            service_endpoint="ess.aliyuncs.com",
            api_version="2014-08-28",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "ScalingGroups.ScalingGroup".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, ecs_auto_scaling_groups=data)


if __name__ == "__main__":
    main()
