#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.mongodb_backup"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: mongodb_backup
short_description: Manage MongoDB backups.
description:
  - Create backups for an Alibaba Cloud MongoDB instance.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  db_instance_id:
    description: MongoDB instance ID.
    type: str
  backup_method:
    description: Backup method.
    type: str
    choices: ['Physical', 'Logical']
"""

EXAMPLES = r"""
- name: Manage MongoDB backups
  stevefulme1.alibaba_cloud.mongodb_backup:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
mongodb_backup:
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
        backup_method=dict(type="str", choices=["Physical", "Logical"]),
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
    if module.params.get("backup_method") is not None:
        params["BackupMethod"] = module.params["backup_method"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeBackups",
            params,
            service_endpoint="mongodb.aliyuncs.com",
            api_version="2015-12-01",
        )

        data = existing
        for key in "Backups.Backup".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateBackup",
                    params,
                    service_endpoint="mongodb.aliyuncs.com",
                    api_version="2015-12-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    mongodb_backup=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    mongodb_backup=data[0],
                )

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
