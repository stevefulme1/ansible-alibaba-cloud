#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.mongodb_account"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: mongodb_account
short_description: Manage MongoDB accounts.
description:
  - Create or reset accounts on an Alibaba Cloud MongoDB instance.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  db_instance_id:
    description: MongoDB instance ID.
    type: str
  account_name:
    description: Account username.
    type: str
  account_password:
    description: Account password.
    type: str
"""

EXAMPLES = r"""
- name: Manage MongoDB accounts
  stevefulme1.alibaba_cloud.mongodb_account:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
mongodb_account:
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
        db_instance_id=dict(type="str"),
        account_name=dict(type="str"),
        account_password=dict(type="str", no_log=True),
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
    if module.params.get("db_instance_id") is not None:
        params["DBInstanceId"] = module.params["db_instance_id"]
    if module.params.get("account_name") is not None:
        params["AccountName"] = module.params["account_name"]
    if module.params.get("account_password") is not None:
        params["AccountPassword"] = module.params["account_password"]


    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeAccounts",
            params,
            service_endpoint="mongodb.aliyuncs.com",
            api_version="2015-12-01",
        )

        data = existing
        for key in "Accounts.Account".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "ResetAccountPassword",
                    params,
                    service_endpoint="mongodb.aliyuncs.com",
                    api_version="2015-12-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    mongodb_account=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    mongodb_account=data[0],
                )

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
