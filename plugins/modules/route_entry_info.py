#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.route_entry_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: route_entry_info
short_description: Query route entries.
description:
  - Retrieve information about Alibaba Cloud route entries.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  route_table_id:
    description: Route table ID.
    type: str
    required: true
  route_entry_id:
    description: Filter by route entry ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all route entries in a table
  stevefulme1.alibaba_cloud.route_entry_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    route_table_id: vtb-xxxxx

- name: Query specific route entry
  stevefulme1.alibaba_cloud.route_entry_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    route_table_id: vtb-xxxxx
    route_entry_id: rte-xxxxx
"""

RETURN = r"""
route_entries:
  description: List of route entries.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        route_table_id=dict(type="str", required=True),
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

    params = {
        "RouteTableId": module.params["route_table_id"],
    }
    if module.params.get("route_entry_id"):
        params["RouteEntryId"] = module.params["route_entry_id"]

    try:
        result = client.get(
            "DescribeRouteEntryList",
            params,
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "RouteEntrys.RouteEntry".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, route_entries=data)


if __name__ == "__main__":
    main()
