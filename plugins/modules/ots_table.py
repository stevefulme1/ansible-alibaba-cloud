#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ots_table"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ots_table
short_description: Manage Table Store tables.
description:
  - Create or delete manage table store tables.
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
  instance_name:
    description: Table Store instance name.
    type: str
    required: true
  table_name:
    description: Table name.
    type: str
  primary_keys:
    description: List of primary key column definitions.
    type: list
    elements: dict"""

EXAMPLES = r"""
- name: Manage Table Store tables.
  stevefulme1.alibaba_cloud.ots_table:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
ots_table:
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
        instance_name=dict(type="str", required=True),
        table_name=dict(type="str"),
        primary_keys=dict(type="list", elements="dict", no_log=False),
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
    if module.params.get("instance_name") is not None:
        params["InstanceName"] = module.params["instance_name"]
    if module.params.get("table_name") is not None:
        params["TableName"] = module.params["table_name"]
    if module.params.get("primary_keys") is not None:
        params["PrimaryKeys"] = module.params["primary_keys"]

    try:
        existing = client.get(
            "ListTable",
            params,
            service_endpoint="ots.aliyuncs.com",
            api_version="2016-06-20",
        )

        data = existing
        for key in "Tables.Table".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateTable",
                    params,
                    service_endpoint="ots.aliyuncs.com",
                    api_version="2016-06-20",
                )
                changed = True
                module.exit_json(changed=changed, ots_table=result)
            else:
                module.exit_json(changed=False, ots_table=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteTable",
                    params,
                    service_endpoint="ots.aliyuncs.com",
                    api_version="2016-06-20",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
