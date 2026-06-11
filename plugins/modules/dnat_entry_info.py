#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dnat_entry_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dnat_entry_info
short_description: Query DNAT entries.
description:
  - Retrieve information about Alibaba Cloud VPC DNAT (Destination NAT) entries.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  forward_table_id:
    description: Forward table ID.
    type: str
  forward_entry_id:
    description: Filter by forward entry ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all DNAT entries
  stevefulme1.alibaba_cloud.dnat_entry_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    forward_table_id: ftb-123

- name: Query specific DNAT entry
  stevefulme1.alibaba_cloud.dnat_entry_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    forward_table_id: ftb-123
    forward_entry_id: fwd-123
"""

RETURN = r"""
dnat_entries:
  description: List of DNAT entries.
  returned: success
  type: list
  elements: dict
  sample:
    - forward_entry_id: fwd-123
      external_ip: 47.1.2.3
      external_port: "80"
      internal_ip: 192.168.1.10
      internal_port: "8080"
      ip_protocol: TCP
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        forward_table_id=dict(type="str"),
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

    params = {}
    if module.params.get("forward_table_id"):
        params["ForwardTableId"] = module.params["forward_table_id"]
    if module.params.get("forward_entry_id"):
        params["ForwardEntryId"] = module.params["forward_entry_id"]

    try:
        result = client.get(
            "DescribeForwardTableEntries",
            params,
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "ForwardTableEntries.ForwardTableEntry".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dnat_entries=data)


if __name__ == "__main__":
    main()
