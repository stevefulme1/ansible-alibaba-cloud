#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.slb_listener_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: slb_listener_info
short_description: Query SLB listeners.
description:
  - Retrieve information about Alibaba Cloud SLB listeners.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  load_balancer_id:
    description: SLB instance ID.
    type: str
    required: true
  listener_port:
    description: Filter by listener port number.
    type: int
"""

EXAMPLES = r"""
- name: Query all SLB listeners
  stevefulme1.alibaba_cloud.slb_listener_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    load_balancer_id: lb-xxxxx

- name: Query specific listener
  stevefulme1.alibaba_cloud.slb_listener_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    load_balancer_id: lb-xxxxx
    listener_port: 80
"""

RETURN = r"""
slb_listeners:
  description: List of SLB listeners.
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
        listener_port=dict(type="int"),
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
    if module.params.get("listener_port"):
        params["ListenerPort"] = module.params["listener_port"]

    try:
        result = client.get(
            "DescribeLoadBalancerListeners",
            params,
            service_endpoint="slb.aliyuncs.com",
            api_version="2014-05-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Listeners".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, slb_listeners=data)


if __name__ == "__main__":
    main()
