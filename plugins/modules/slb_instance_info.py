#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.slb_instance_info"""

from __future__ import annotations


DOCUMENTATION = r"""
---
module: slb_instance_info
short_description: List SLBs.
description:
  - Retrieve information about Alibaba Cloud slb_instance resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  load_balancer_name:
    description: Filter by name.
    type: str
"""

EXAMPLES = r"""
- name: List SLBs
  stevefulme1.alibaba_cloud.slb_instance_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
"""

RETURN = r"""
load_balancers:
  description: List of SLB instances.
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
        load_balancer_name=dict(type="str"),
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
    try:
        result = client.get(
            "DescribeLoadBalancers",
            params,
            service_endpoint="slb.aliyuncs.com",
            api_version="2014-05-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "LoadBalancers.LoadBalancer".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, slb_instances=data)


if __name__ == "__main__":
    main()
