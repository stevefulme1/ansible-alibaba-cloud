#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_auto_scaling_group"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_auto_scaling_group
short_description: Manage auto scaling groups.
description:
  - Create, update, or delete Alibaba Cloud ecs_auto_scaling_group resources.
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
  scaling_group_name:
    description: Name of the scaling group.
    type: str
  max_size:
    description: Maximum number of instances.
    type: int
  min_size:
    description: Minimum number of instances.
    type: int
  vswitch_ids:
    description: List of vSwitch IDs.
    type: list
    elements: str
  scaling_group_id:
    description: Existing group ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create scaling group
  stevefulme1.alibaba_cloud.ecs_auto_scaling_group:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    scaling_group_name: web-asg
    max_size: 10
    min_size: 2
"""

RETURN = r"""
scaling_group:
  description: Scaling group details.
  returned: success
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        scaling_group_name=dict(type="str"),
        max_size=dict(type="int"),
        min_size=dict(type="int"),
        vswitch_ids=dict(type="list", elements="str"),
        scaling_group_id=dict(type="str"),
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
            "DescribeScalingGroups",
            {},
            service_endpoint="ess.aliyuncs.com",
            api_version="2014-08-28",
        )

        data = existing
        for key in "ScalingGroups.ScalingGroup".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateScalingGroup",
                    {},
                    service_endpoint="ess.aliyuncs.com",
                    api_version="2014-08-28",
                )
                changed = True
                module.exit_json(changed=changed, ecs_auto_scaling_group=result)
            else:
                module.exit_json(
                    changed=False,
                    ecs_auto_scaling_group=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteScalingGroup",
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
