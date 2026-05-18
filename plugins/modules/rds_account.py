#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.rds_account"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rds_account
short_description: Manage RDS database accounts.
description:
  - Create or delete database accounts on an Alibaba Cloud RDS instance.
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
  db_instance_id:
    description: RDS instance ID.
    type: str
  account_name:
    description: Account username.
    type: str
  account_password:
    description: Account password.
    type: str
  account_type:
    description: Account type.
    type: str
    choices: ['Normal', 'Super']
  account_description:
    description: Account description.
    type: str
"""

EXAMPLES = r"""
- name: Manage RDS database accounts
  stevefulme1.alibaba_cloud.rds_account:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
rds_account:
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
        db_instance_id=dict(type="str"),
        account_name=dict(type="str"),
        account_password=dict(type="str", no_log=True),
        account_type=dict(type="str", choices=["Normal", "Super"]),
        account_description=dict(type="str"),
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
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeAccounts",
            {},
            service_endpoint="rds.aliyuncs.com",
            api_version="2014-08-15",
        )

        data = existing
        for key in "Accounts.DBInstanceAccount".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateAccount",
                    {},
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    rds_account=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    rds_account=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteAccount",
                    {},
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
