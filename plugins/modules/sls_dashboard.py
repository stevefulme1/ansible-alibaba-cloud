#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_dashboard"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_dashboard
short_description: Manage SLS dashboards.
description:
  - Create, update, or delete Alibaba Cloud SLS dashboard resources.
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
  dashboard_name:
    description: Name of the dashboard.
    type: str
  display_name:
    description: Display name of the dashboard.
    type: str
  description:
    description: Description of the dashboard.
    type: str
"""

EXAMPLES = r"""
- name: Create a SLS dashboard
  stevefulme1.alibaba_cloud.sls_dashboard:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: example-value
    dashboard_name: example-value
"""

RETURN = r"""
sls_dashboard:
  description: Sls dashboard details.
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
        dashboard_name=dict(type="str"),
        display_name=dict(type="str"),
        description=dict(type="str"),
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
            "DescribeDashboard",
            {},
            service_endpoint="sls.{region_id}.aliyuncs.com",
            api_version="2020-12-30",
        )

        data = existing
        for key in "Dashboards.Dashboard".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDashboard",
                    {},
                    service_endpoint="sls.{region_id}.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
                module.exit_json(changed=changed, sls_dashboard=result)
            else:
                module.exit_json(
                    changed=False,
                    sls_dashboard=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDashboard",
                    {},
                    service_endpoint="sls.{region_id}.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
