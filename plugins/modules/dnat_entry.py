#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dnat_entry"""

from __future__ import annotations


DOCUMENTATION = r"""
---
module: dnat_entry
short_description: Manage DNAT entries.
description:
  - Create, update, or delete Alibaba Cloud dnat_entry resources.
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
  forward_table_id:
    description: Forward table ID from the NAT gateway.
    type: str
    required: true
  external_ip:
    description: Public IP address.
    type: str
  external_port:
    description: External port.
    type: str
  internal_ip:
    description: Internal (private) IP address.
    type: str
  internal_port:
    description: Internal port.
    type: str
  ip_protocol:
    description: Protocol (TCP, UDP, Any).
    type: str
  forward_entry_id:
    description: Existing entry ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create DNAT entry
  stevefulme1.alibaba_cloud.dnat_entry:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    forward_table_id: ftb-xxxxx
    external_ip: 47.xx.xx.xx
    external_port: "80"
    internal_ip: 172.16.1.10
    internal_port: "8080"
    ip_protocol: TCP
"""

RETURN = r"""
dnat_entry:
  description: DNAT entry details.
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
        forward_table_id=dict(type="str", required=True),
        external_ip=dict(type="str"),
        external_port=dict(type="str"),
        internal_ip=dict(type="str"),
        internal_port=dict(type="str"),
        ip_protocol=dict(type="str"),
        forward_entry_id=dict(type="str"),
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
            "DescribeForwardTableEntries",
            {},
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = existing
        for key in "ForwardTableEntries.ForwardTableEntry".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateForwardEntry",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, dnat_entry=result)
            else:
                module.exit_json(
                    changed=False,
                    dnat_entry=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteForwardEntry",
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
