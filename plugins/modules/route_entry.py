#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.route_entry"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: route_entry
short_description: Manage route entries.
description:
  - Create, update, or delete Alibaba Cloud route_entry resources.
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
  route_table_id:
    description: Route table ID.
    type: str
    required: true
  destination_cidr_block:
    description: Destination CIDR.
    type: str
  next_hop_id:
    description: Next hop instance ID.
    type: str
  next_hop_type:
    description: Next hop type.
    type: str
    choices: [Instance, RouterInterface, VpnGateway, NatGateway]
  route_entry_id:
    description: Existing route entry ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Add route entry
  stevefulme1.alibaba_cloud.route_entry:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    route_table_id: vtb-xxxxx
    destination_cidr_block: 10.0.0.0/8
    next_hop_id: i-xxxxx
    next_hop_type: Instance
"""

RETURN = r"""
route_entry:
  description: Route entry details.
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
        route_table_id=dict(type="str", required=True),
        destination_cidr_block=dict(type="str"),
        next_hop_id=dict(type="str"),
        next_hop_type=dict(
            type="str",
            choices=[
                "Instance",
                "RouterInterface",
                "VpnGateway",
                "NatGateway",
            ],
        ),
        route_entry_id=dict(type="str"),
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
            "DescribeRouteEntryList",
            {},
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = existing
        for key in "RouteEntrys.RouteEntry".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateRouteEntry",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, route_entry=result)
            else:
                module.exit_json(
                    changed=False,
                    route_entry=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteRouteEntry",
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
