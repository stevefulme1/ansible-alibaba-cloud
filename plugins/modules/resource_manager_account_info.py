#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.resource_manager_account_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: resource_manager_account_info
short_description: Query Resource Manager member accounts.
description:
  - Retrieve information about Alibaba Cloud member account resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  account_id:
    description: Filter by member account ID.
    type: str
"""

EXAMPLES = r"""
- name: List all member accounts
  stevefulme1.alibaba_cloud.resource_manager_account_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    account_id: example-value
"""

RETURN = r"""
resource_manager_accounts:
  description: List of member accounts.
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
        account_id=dict(type="str"),
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
            "ListAccounts",
            params,
            service_endpoint="resourcemanager.aliyuncs.com",
            api_version="2020-03-31",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    for key in "Accounts.Account".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, resource_manager_accounts=data)


if __name__ == "__main__":
    main()
