#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.snat_entry"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: snat_entry
short_description: Manage SNAT entries.
description:
  - Create, update, or delete Alibaba Cloud snat_entry resources.
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
  snat_table_id:
    description: SNAT table ID from the NAT gateway.
    type: str
    required: true
  source_vswitch_id:
    description: Source vSwitch ID for SNAT.
    type: str
  snat_ip:
    description: Public IP for SNAT translation.
    type: str
  snat_entry_id:
    description: Existing SNAT entry ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create SNAT entry
  stevefulme1.alibaba_cloud.snat_entry:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    snat_table_id: stb-xxxxx
    source_vswitch_id: vsw-xxxxx
    snat_ip: 47.xx.xx.xx
"""

RETURN = r"""
snat_entry:
  description: SNAT entry details.
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
        snat_table_id=dict(type="str", required=True),
        source_vswitch_id=dict(type="str"),
        snat_ip=dict(type="str"),
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

    state = module.params["state"]
    changed = False

    params = {}
    if module.params.get("snat_table_id") is not None:
        params["SnatTableId"] = module.params["snat_table_id"]
    if module.params.get("source_vswitch_id") is not None:
        params["SourceVswitchId"] = module.params["source_vswitch_id"]
    if module.params.get("snat_ip") is not None:
        params["SnatIp"] = module.params["snat_ip"]
    if module.params.get("snat_entry_id") is not None:
        params["SnatEntryId"] = module.params["snat_entry_id"]


    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeSnatTableEntries",
            params,
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = existing
        for key in "SnatTableEntries.SnatTableEntry".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateSnatEntry",
                    params,
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, snat_entry=result)
            else:
                module.exit_json(
                    changed=False,
                    snat_entry=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteSnatEntry",
                    params,
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
