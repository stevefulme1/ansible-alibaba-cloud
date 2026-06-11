#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.redis_backup_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: redis_backup_info
short_description: Query Redis backups.
description:
  - Retrieve information about Alibaba Cloud Redis instance backups.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Redis instance ID.
    type: str
    required: true
  backup_id:
    description: Filter by backup ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all Redis backups
  stevefulme1.alibaba_cloud.redis_backup_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: r-xxxxx

- name: Query specific Redis backup
  stevefulme1.alibaba_cloud.redis_backup_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: r-xxxxx
    backup_id: 12345
"""

RETURN = r"""
redis_backups:
  description: List of Redis backups.
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
        instance_id=dict(type="str", required=True),
        backup_id=dict(type="str"),
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
        "InstanceId": module.params["instance_id"],
    }
    if module.params.get("backup_id"):
        params["BackupId"] = module.params["backup_id"]

    try:
        result = client.get(
            "DescribeBackups",
            params,
            service_endpoint="r-kvstore.aliyuncs.com",
            api_version="2015-01-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Backups.Backup".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, redis_backups=data)


if __name__ == "__main__":
    main()
