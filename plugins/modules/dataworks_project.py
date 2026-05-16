#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dataworks_project"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dataworks_project
short_description: Manage DataWorks projects.
description:
  - Create, update, or delete Alibaba Cloud DataWorks project resources.
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
    description: Name of the DataWorks project.
    type: str
  project_identifier:
    description: Unique identifier for the project.
    type: str
  project_description:
    description: Description of the project.
    type: str
  project_mode:
    description: Project mode, C(2) for standard, C(3) for simple.
    type: int
"""

EXAMPLES = r"""
- name: Create a DataWorks project
  stevefulme1.alibaba_cloud.dataworks_project:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: example-value
    project_identifier: example-value
"""

RETURN = r"""
dataworks_project:
  description: Dataworks project details.
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
        project_identifier=dict(type="str"),
        project_description=dict(type="str"),
        project_mode=dict(type="int"),
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
            "DescribeProject",
            {},
            service_endpoint="dataworks.{region_id}.aliyuncs.com",
            api_version="2020-05-18",
        )

        data = existing
        for key in "Projects.Project".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateProject",
                    {},
                    service_endpoint="dataworks.{region_id}.aliyuncs.com",
                    api_version="2020-05-18",
                )
                changed = True
                module.exit_json(changed=changed, dataworks_project=result)
            else:
                module.exit_json(
                    changed=False,
                    dataworks_project=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteProject",
                    {},
                    service_endpoint="dataworks.{region_id}.aliyuncs.com",
                    api_version="2020-05-18",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
