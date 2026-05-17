#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.edas_application"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: edas_application
short_description: Manage EDAS applications.
description:
  - Create, update, or delete Alibaba Cloud EDAS application resources.
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
  app_name:
    description: Name of the application.
    type: str
  app_id:
    description: ID of an existing application.
    type: str
  cluster_id:
    description: Cluster ID for deployment.
    type: str
  package_type:
    description: Package type, e.g. C(war) or C(jar).
    type: str
  description:
    description: Application description.
    type: str
"""

EXAMPLES = r"""
- name: Create a EDAS application
  stevefulme1.alibaba_cloud.edas_application:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    app_name: example-value
    app_id: example-value
"""

RETURN = r"""
edas_application:
  description: Edas application details.
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
        app_name=dict(type="str"),
        app_id=dict(type="str"),
        cluster_id=dict(type="str"),
        package_type=dict(type="str"),
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

    params = {}
    if module.params.get("app_name") is not None:
        params["AppName"] = module.params["app_name"]
    if module.params.get("app_id") is not None:
        params["AppId"] = module.params["app_id"]
    if module.params.get("cluster_id") is not None:
        params["ClusterId"] = module.params["cluster_id"]
    if module.params.get("package_type") is not None:
        params["PackageType"] = module.params["package_type"]
    if module.params.get("description") is not None:
        params["Description"] = module.params["description"]

    try:
        existing = client.get(
            "DescribeApplication",
            params,
            service_endpoint="edas.{region_id}.aliyuncs.com",
            api_version="2017-08-01",
        )

        data = existing
        for key in "Applications.Application".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "InsertApplication",
                    params,
                    service_endpoint="edas.{region_id}.aliyuncs.com",
                    api_version="2017-08-01",
                )
                changed = True
                module.exit_json(changed=changed, edas_application=result)
            else:
                module.exit_json(
                    changed=False,
                    edas_application=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteApplication",
                    params,
                    service_endpoint="edas.{region_id}.aliyuncs.com",
                    api_version="2017-08-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
