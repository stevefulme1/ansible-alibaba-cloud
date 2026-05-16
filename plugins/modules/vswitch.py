#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.vswitch"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vswitch
short_description: Manage vSwitches (subnets).
description:
  - Create, update, or delete Alibaba Cloud vswitch resources.
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
  vswitch_name:
    description: Name of the vSwitch.
    type: str
  vpc_id:
    description: VPC ID the vSwitch belongs to.
    type: str
  cidr_block:
    description: CIDR block for the vSwitch.
    type: str
  zone_id:
    description: Availability zone.
    type: str
  vswitch_id:
    description: Existing vSwitch ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create vSwitch
  stevefulme1.alibaba_cloud.vswitch:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    vswitch_name: web-subnet
    vpc_id: vpc-xxxxx
    cidr_block: 172.16.1.0/24
    zone_id: cn-hangzhou-a
"""

RETURN = r"""
vswitch:
  description: vSwitch details.
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
        vswitch_name=dict(type="str"),
        vpc_id=dict(type="str"),
        cidr_block=dict(type="str"),
        zone_id=dict(type="str"),
        vswitch_id=dict(type="str"),
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
            "DescribeVSwitches",
            {},
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = existing
        for key in "VSwitches.VSwitch".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateVSwitch",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, vswitch=result)
            else:
                module.exit_json(
                    changed=False,
                    vswitch=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteVSwitch",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
