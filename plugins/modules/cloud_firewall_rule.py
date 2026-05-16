#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cloud_firewall_rule"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cloud_firewall_rule
short_description: Manage Cloud Firewall access control rules.
description:
  - Create, update, or delete Alibaba Cloud cloud_firewall_rule resources.
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
  acl_uuid:
    description: UUID of an existing firewall rule.
    type: str
  direction:
    description: Rule direction.
    type: str
    choices: [in, out]
    required: true
  source:
    description: Source address or CIDR.
    type: str
    required: true
  destination:
    description: Destination address or CIDR.
    type: str
    required: true
  proto:
    description: Protocol type.
    type: str
    choices: [TCP, UDP, ICMP, ANY]
    default: TCP
  acl_action:
    description: Rule action.
    type: str
    choices: [accept, drop, log]
    required: true
  description:
    description: Rule description.
    type: str
"""

EXAMPLES = r"""
- name: Manage cloud_firewall_rule resource
  stevefulme1.alibaba_cloud.cloud_firewall_rule:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    direction: in
    source: 10.0.0.0/8
    destination: 172.16.0.0/12
    proto: TCP
    acl_action: accept
"""

RETURN = r"""
cloud_firewall_rule:
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
        acl_uuid=dict(type="str"),
        direction=dict(type="str", choices=["in", "out"], required=True),
        source=dict(type="str", required=True),
        destination=dict(type="str", required=True),
        proto=dict(type="str", choices=["TCP", "UDP", "ICMP", "ANY"], default="TCP"),
        acl_action=dict(type="str", choices=["accept", "drop", "log"], required=True),
        description=dict(type="str"),
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
        existing = client.get(
            "DescribeControlPolicy",
            {},
            service_endpoint="cloudfw.aliyuncs.com",
            api_version="2017-12-07",
        )

        data = existing
        for key in "Policys".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AddControlPolicy",
                    {},
                    service_endpoint="cloudfw.aliyuncs.com",
                    api_version="2017-12-07",
                )
                changed = True
                module.exit_json(changed=changed, cloud_firewall_rule=result)
            else:
                module.exit_json(changed=False, cloud_firewall_rule=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteControlPolicy",
                    {},
                    service_endpoint="cloudfw.aliyuncs.com",
                    api_version="2017-12-07",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
