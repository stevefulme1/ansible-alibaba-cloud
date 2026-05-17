#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sae_application"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sae_application
short_description: Manage SAE serverless applications.
description:
  - Create, update, or delete Alibaba Cloud SAE application resources.
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
    description: Name of the serverless application.
    type: str
  app_id:
    description: ID of an existing application.
    type: str
  namespace_id:
    description: SAE namespace ID.
    type: str
  package_type:
    description: Package type, e.g. C(FatJar) or C(Image).
    type: str
  replicas:
    description: Number of application instances.
    type: int
  cpu:
    description: CPU specification in millicores.
    type: int
  memory:
    description: Memory specification in MB.
    type: int
"""

EXAMPLES = r"""
- name: Create a SAE application
  stevefulme1.alibaba_cloud.sae_application:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    app_name: example-value
    app_id: example-value
"""

RETURN = r"""
sae_application:
  description: Sae application details.
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
        namespace_id=dict(type="str"),
        package_type=dict(type="str"),
        replicas=dict(type="int"),
        cpu=dict(type="int"),
        memory=dict(type="int"),
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
    if module.params.get("namespace_id") is not None:
        params["NamespaceId"] = module.params["namespace_id"]
    if module.params.get("package_type") is not None:
        params["PackageType"] = module.params["package_type"]
    if module.params.get("replicas") is not None:
        params["Replicas"] = module.params["replicas"]
    if module.params.get("cpu") is not None:
        params["Cpu"] = module.params["cpu"]
    if module.params.get("memory") is not None:
        params["Memory"] = module.params["memory"]


    try:
        existing = client.get(
            "DescribeApplication",
            params,
            service_endpoint="sae.{region_id}.aliyuncs.com",
            api_version="2019-05-06",
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
                    "CreateApplication",
                    params,
                    service_endpoint="sae.{region_id}.aliyuncs.com",
                    api_version="2019-05-06",
                )
                changed = True
                module.exit_json(changed=changed, sae_application=result)
            else:
                module.exit_json(
                    changed=False,
                    sae_application=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteApplication",
                    params,
                    service_endpoint="sae.{region_id}.aliyuncs.com",
                    api_version="2019-05-06",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
