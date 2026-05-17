#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.maxcompute_table"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: maxcompute_table
short_description: Manage MaxCompute tables.
description:
  - Create, update, or delete Alibaba Cloud maxcompute_table resources.
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
  project_name:
    description: MaxCompute project for the table.
    type: str
    required: true
  table_name:
    description: Name of the table.
    type: str
    required: true
  columns:
    description: List of column definitions.
    type: list
    elements: dict
  comment:
    description: Table comment.
    type: str
"""

EXAMPLES = r"""
- name: Manage maxcompute_table resource
  stevefulme1.alibaba_cloud.maxcompute_table:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: my_odps_project
    table_name: user_events
"""

RETURN = r"""
maxcompute_table:
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
        project_name=dict(type="str", required=True),
        table_name=dict(type="str", required=True),
        columns=dict(type="list", elements="dict"),
        comment=dict(type="str"),
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
    if module.params.get("project_name") is not None:
        params["ProjectName"] = module.params["project_name"]
    if module.params.get("table_name") is not None:
        params["TableName"] = module.params["table_name"]
    if module.params.get("columns") is not None:
        params["Columns"] = module.params["columns"]
    if module.params.get("comment") is not None:
        params["Comment"] = module.params["comment"]


    try:
        existing = client.get(
            "ListTables",
            params,
            service_endpoint="maxcompute.aliyuncs.com",
            api_version="2022-01-04",
        )

        data = existing
        for key in "data.tables".split("."):
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
                    service_endpoint="maxcompute.aliyuncs.com",
                    api_version="2022-01-04",
                )
                changed = True
                module.exit_json(changed=changed, maxcompute_table=result)
            else:
                module.exit_json(changed=False, maxcompute_table=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteTable",
                    params,
                    service_endpoint="maxcompute.aliyuncs.com",
                    api_version="2022-01-04",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
