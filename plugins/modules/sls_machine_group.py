#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_machine_group"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_machine_group
short_description: Manage SLS machine group.
description:
  - Create, update, or delete Alibaba Cloud sls_machine_group resources.
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
    description: Log Service project name.
    type: str
  group_name:
    description: Machine group name.
    type: str
  machine_list:
    description: List of machine identifiers.
    type: str
"""

EXAMPLES = r"""
- name: Manage sls_machine_group
  stevefulme1.alibaba_cloud.sls_machine_group:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: my-sls-project
    group_name: web-servers
"""

RETURN = r"""
sls_machine_group:
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
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        project_name=dict(type="str"),
        group_name=dict(type="str"),
        machine_list=dict(type="str"),
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
    if module.params.get("group_name") is not None:
        params["GroupName"] = module.params["group_name"]
    if module.params.get("machine_list") is not None:
        params["MachineList"] = module.params["machine_list"]

    try:
        result = client.get(
            "ListMachineGroup",
            params,
            service_endpoint="sls.aliyuncs.com",
            api_version="2020-12-30",
        )

        data = result
        for key in ["MachineGroups"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateMachineGroup",
                    params,
                    service_endpoint="sls.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
                module.exit_json(changed=changed, sls_machine_group=result)
            else:
                module.exit_json(
                    changed=False,
                    sls_machine_group=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteMachineGroup",
                    params,
                    service_endpoint="sls.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
