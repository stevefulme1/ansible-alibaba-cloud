#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.security_group_egress_rule"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: security_group_egress_rule
short_description: Manage security group egress rules.
description:
  - Add or remove egress rules from an Alibaba Cloud security group.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  security_group_id:
    description: Security group ID.
    type: str
  ip_protocol:
    description: IP protocol.
    type: str
    choices: ['tcp', 'udp', 'icmp', 'all']
  port_range:
    description: Port range, e.g. C(80/80) or C(-1/-1).
    type: str
  dest_cidr_ip:
    description: Destination CIDR block.
    type: str
  policy:
    description: Authorization policy.
    type: str
    choices: ['accept', 'drop']
  priority:
    description: Rule priority (1-100).
    type: str
"""

EXAMPLES = r"""
- name: Manage security group egress rules
  stevefulme1.alibaba_cloud.security_group_egress_rule:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
security_group_egress_rule:
  description: Resource details.
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
        state=dict(type="str", choices=["present", "absent"], default="present"),
        security_group_id=dict(type="str"),
        ip_protocol=dict(type="str", choices=["tcp", "udp", "icmp", "all"]),
        port_range=dict(type="str"),
        dest_cidr_ip=dict(type="str"),
        policy=dict(type="str", choices=["accept", "drop"]),
        priority=dict(type="str"),
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

    params = {}
    if module.params.get("security_group_id") is not None:
        params["SecurityGroupId"] = module.params["security_group_id"]
    if module.params.get("ip_protocol") is not None:
        params["IpProtocol"] = module.params["ip_protocol"]
    if module.params.get("port_range") is not None:
        params["PortRange"] = module.params["port_range"]
    if module.params.get("dest_cidr_ip") is not None:
        params["DestCidrIp"] = module.params["dest_cidr_ip"]
    if module.params.get("policy") is not None:
        params["Policy"] = module.params["policy"]
    if module.params.get("priority") is not None:
        params["Priority"] = module.params["priority"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeSecurityGroupAttribute",
            params,
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
                    "AuthorizeSecurityGroupEgress",
                    params,
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    security_group_egress_rule=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    security_group_egress_rule=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "RevokeSecurityGroupEgress",
                    params,
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
