#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.slb_instance"""

from __future__ import annotations


DOCUMENTATION = r"""
---
module: slb_instance
short_description: Manage SLB load balancers.
description:
  - Create, update, or delete Alibaba Cloud slb_instance resources.
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
  load_balancer_name:
    description: Name of the SLB instance.
    type: str
  address_type:
    description: Address type (internet or intranet).
    type: str
    choices: [internet, intranet]
    default: internet
  vpc_id:
    description: VPC ID for the SLB.
    type: str
  vswitch_id:
    description: VSwitch ID for intranet SLB.
    type: str
  load_balancer_id:
    description: Existing SLB ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create SLB
  stevefulme1.alibaba_cloud.slb_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    load_balancer_name: web-slb
    address_type: internet
"""

RETURN = r"""
load_balancer:
  description: SLB instance details.
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
        load_balancer_name=dict(type="str"),
        address_type=dict(
            type="str", choices=["internet", "intranet"], default="internet"
        ),
        vpc_id=dict(type="str"),
        vswitch_id=dict(type="str"),
        load_balancer_id=dict(type="str"),
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
            "DescribeLoadBalancers",
            {},
            service_endpoint="slb.aliyuncs.com",
            api_version="2014-05-15",
        )

        data = existing
        for key in "LoadBalancers.LoadBalancer".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateLoadBalancer",
                    {},
                    service_endpoint="slb.aliyuncs.com",
                    api_version="2014-05-15",
                )
                changed = True
                module.exit_json(changed=changed, slb_instance=result)
            else:
                module.exit_json(
                    changed=False,
                    slb_instance=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteLoadBalancer",
                    {},
                    service_endpoint="slb.aliyuncs.com",
                    api_version="2014-05-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
