#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.hbr_vault"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: hbr_vault
short_description: Manage HBR backup vaults.
description:
  - Create or delete manage hbr backup vaults.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  vault_id:
    description: Backup vault ID.
    type: str
  vault_name:
    description: Vault display name.
    type: str
  vault_type:
    description: Vault type.
    type: str
    choices: ['STANDARD', 'OTS_BACKUP']"""

EXAMPLES = r"""
- name: Manage HBR backup vaults.
  stevefulme1.alibaba_cloud.hbr_vault:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
hbr_vault:
  description: Resource details.
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
        state=dict(type="str", choices=["present", "absent"], default="present"),
        vault_id=dict(type="str"),
        vault_name=dict(type="str"),
        vault_type=dict(type="str", choices=["STANDARD", "OTS_BACKUP"]),
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
        existing = client.get(
            "DescribeVaults",
            {},
            service_endpoint="hbr.aliyuncs.com",
            api_version="2017-09-08",
        )

        data = existing
        for key in "Vaults.Vault".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateVault",
                    {},
                    service_endpoint="hbr.aliyuncs.com",
                    api_version="2017-09-08",
                )
                changed = True
                module.exit_json(changed=changed, hbr_vault=result)
            else:
                module.exit_json(changed=False, hbr_vault=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteVault",
                    {},
                    service_endpoint="hbr.aliyuncs.com",
                    api_version="2017-09-08",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
