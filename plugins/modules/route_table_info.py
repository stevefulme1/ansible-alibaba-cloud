#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.route_table_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: route_table_info
short_description: Query route tables.
description:
  - Retrieve information about Alibaba Cloud route tables.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  vpc_id:
    description: Filter by VPC ID.
    type: str
  route_table_id:
    description: Filter by route table ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all route tables
  stevefulme1.alibaba_cloud.route_table_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query route tables in a VPC
  stevefulme1.alibaba_cloud.route_table_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    vpc_id: vpc-xxxxx
"""

RETURN = r"""
route_tables:
  description: List of route tables.
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
        vpc_id=dict(type="str"),
        route_table_id=dict(type="str"),
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

    params = {}
    if module.params.get("vpc_id"):
        params["VpcId"] = module.params["vpc_id"]
    if module.params.get("route_table_id"):
        params["RouteTableId"] = module.params["route_table_id"]

    try:
        result = client.get(
            "DescribeRouteTableList",
            params,
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "RouterTableList.RouterTableListType".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, route_tables=data)


if __name__ == "__main__":
    main()
