#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.slb_server_group_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: slb_server_group_info
short_description: Query SLB backend server groups.
description:
  - Retrieve information about Alibaba Cloud SLB backend server groups.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  load_balancer_id:
    description: SLB instance ID.
    type: str
    required: true
  vserver_group_id:
    description: Filter by server group ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all server groups
  stevefulme1.alibaba_cloud.slb_server_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    load_balancer_id: lb-xxxxx

- name: Query specific server group
  stevefulme1.alibaba_cloud.slb_server_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    load_balancer_id: lb-xxxxx
    vserver_group_id: rsp-xxxxx
"""

RETURN = r"""
slb_server_groups:
  description: List of SLB server groups.
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
        load_balancer_id=dict(type="str", required=True),
        vserver_group_id=dict(type="str"),
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
        "LoadBalancerId": module.params["load_balancer_id"],
    }
    if module.params.get("vserver_group_id"):
        params["VserverGroupId"] = module.params["vserver_group_id"]

    try:
        result = client.get(
            "DescribeVServerGroups",
            params,
            service_endpoint="slb.aliyuncs.com",
            api_version="2014-05-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "VServerGroups.VServerGroup".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, slb_server_groups=data)


if __name__ == "__main__":
    main()
