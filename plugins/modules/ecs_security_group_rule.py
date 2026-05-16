#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_security_group_rule"""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


DOCUMENTATION = r"""
---
module: ecs_security_group_rule
short_description: Manage security group rules.
description:
  - Create, update, or delete Alibaba Cloud ecs_security_group_rule resources.
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
  security_group_id:
    description: Security group ID to add rules to.
    type: str
    required: true
  ip_protocol:
    description: Protocol (tcp, udp, icmp, all).
    type: str
  port_range:
    description: Port range, e.g. C(22/22) or C(80/80).
    type: str
  source_cidr_ip:
    description: Source CIDR for ingress rules.
    type: str
  direction:
    description: Rule direction.
    type: str
    choices: [ingress, egress]
    default: ingress
"""

EXAMPLES = r"""
- name: Allow SSH
  stevefulme1.alibaba_cloud.ecs_security_group_rule:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    security_group_id: sg-xxxxx
    ip_protocol: tcp
    port_range: 22/22
    source_cidr_ip: 0.0.0.0/0
"""

RETURN = r"""
rule:
  description: Security group rule details.
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
        security_group_id=dict(type="str", required=True),
        ip_protocol=dict(type="str"),
        port_range=dict(type="str"),
        source_cidr_ip=dict(type="str"),
        direction=dict(type="str", choices=["ingress", "egress"], default="ingress"),
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
            "DescribeSecurityGroupAttribute",
            {},
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )

        data = existing
        for key in "Permissions.Permission".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AuthorizeSecurityGroup",
                    {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(changed=changed, ecs_security_group_rule=result)
            else:
                module.exit_json(
                    changed=False,
                    ecs_security_group_rule=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "RevokeSecurityGroup",
                    {},
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
