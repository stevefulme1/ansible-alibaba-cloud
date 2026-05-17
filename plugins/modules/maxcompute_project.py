#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.maxcompute_project"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: maxcompute_project
short_description: Manage MaxCompute projects.
description:
  - Create, update, or delete Alibaba Cloud maxcompute_project resources.
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
    description: Name of the MaxCompute project.
    type: str
    required: true
  comment:
    description: Project comment/description.
    type: str
  default_quota:
    description: Default computing quota name.
    type: str
"""

EXAMPLES = r"""
- name: Manage maxcompute_project resource
  stevefulme1.alibaba_cloud.maxcompute_project:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: my_odps_project
"""

RETURN = r"""
maxcompute_project:
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
        comment=dict(type="str"),
        default_quota=dict(type="str"),
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
    if module.params.get("comment") is not None:
        params["Comment"] = module.params["comment"]
    if module.params.get("default_quota") is not None:
        params["DefaultQuota"] = module.params["default_quota"]

    try:
        existing = client.get(
            "ListProjects",
            params,
            service_endpoint="maxcompute.aliyuncs.com",
            api_version="2022-01-04",
        )

        data = existing
        for key in "data.projects".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateProject",
                    params,
                    service_endpoint="maxcompute.aliyuncs.com",
                    api_version="2022-01-04",
                )
                changed = True
                module.exit_json(changed=changed, maxcompute_project=result)
            else:
                module.exit_json(changed=False, maxcompute_project=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteProject",
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
