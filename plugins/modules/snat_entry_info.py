#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.snat_entry_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: snat_entry_info
short_description: Query SNAT entries.
description:
  - Retrieve information about Alibaba Cloud SNAT entries.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  snat_table_id:
    description: SNAT table ID from the NAT gateway.
    type: str
    required: true
  snat_entry_id:
    description: Filter by SNAT entry ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all SNAT entries in a table
  stevefulme1.alibaba_cloud.snat_entry_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    snat_table_id: stb-xxxxx

- name: Query specific SNAT entry
  stevefulme1.alibaba_cloud.snat_entry_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    snat_table_id: stb-xxxxx
    snat_entry_id: snat-xxxxx
"""

RETURN = r"""
snat_entries:
  description: List of SNAT entries.
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
        snat_table_id=dict(type="str", required=True),
        snat_entry_id=dict(type="str"),
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
        "SnatTableId": module.params["snat_table_id"],
    }
    if module.params.get("snat_entry_id"):
        params["SnatEntryId"] = module.params["snat_entry_id"]

    try:
        result = client.get(
            "DescribeSnatTableEntries",
            params,
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "SnatTableEntries.SnatTableEntry".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, snat_entries=data)


if __name__ == "__main__":
    main()
