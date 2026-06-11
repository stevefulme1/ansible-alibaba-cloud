#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ga_listener_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ga_listener_info
short_description: Query Global Accelerator listeners.
description:
  - Retrieve information about Alibaba Cloud Global Accelerator listeners.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  accelerator_id:
    description: Global Accelerator instance ID.
    type: str
  listener_id:
    description: Filter by listener ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all GA listeners
  stevefulme1.alibaba_cloud.ga_listener_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    accelerator_id: ga-123

- name: Query specific GA listener
  stevefulme1.alibaba_cloud.ga_listener_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    listener_id: lsr-123
"""

RETURN = r"""
ga_listeners:
  description: List of Global Accelerator listeners.
  returned: success
  type: list
  elements: dict
  sample:
    - listener_id: lsr-123
      name: tcp-listener
      protocol: TCP
      port_ranges:
        - from_port: 80
          to_port: 80
      state: active
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        accelerator_id=dict(type="str"),
        listener_id=dict(type="str"),
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
    if module.params.get("accelerator_id"):
        params["AcceleratorId"] = module.params["accelerator_id"]
    if module.params.get("listener_id"):
        params["ListenerId"] = module.params["listener_id"]

    try:
        result = client.get(
            "ListListeners",
            params,
            service_endpoint="ga.aliyuncs.com",
            api_version="2019-11-20",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Listeners".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, ga_listeners=data)


if __name__ == "__main__":
    main()
