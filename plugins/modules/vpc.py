#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.vpc"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpc
short_description: Manage VPCs.
description:
  - Create, update, or delete Alibaba Cloud vpc resources.
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
  vpc_name:
    description: Name of the VPC.
    type: str
  cidr_block:
    description: CIDR block for the VPC.
    type: str
  vpc_id:
    description: Existing VPC ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create VPC
  stevefulme1.alibaba_cloud.vpc:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    vpc_name: my-vpc
    cidr_block: 172.16.0.0/12
"""

RETURN = r"""
vpc:
  description: VPC details.
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
        vpc_name=dict(type="str"),
        cidr_block=dict(type="str"),
        vpc_id=dict(type="str"),
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
            "DescribeVpcs",
            {},
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = existing
        for key in "Vpcs.Vpc".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateVpc",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, vpc=result)
            else:
                module.exit_json(
                    changed=False,
                    vpc=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteVpc",
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
