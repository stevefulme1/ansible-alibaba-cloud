#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.api_gateway_app"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: api_gateway_app
short_description: Manage API Gateway app authorizations.
description:
  - Create, update, or delete Alibaba Cloud api_gateway_app resources.
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
    description: Name of the API Gateway app.
    type: str
    required: true
  app_id:
    description: ID of an existing app.
    type: str
  description:
    description: App description.
    type: str
"""

EXAMPLES = r"""
- name: Manage api_gateway_app resource
  stevefulme1.alibaba_cloud.api_gateway_app:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    app_name: my-gateway-app
"""

RETURN = r"""
api_gateway_app:
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
        app_name=dict(type="str", required=True),
        app_id=dict(type="str"),
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
    if module.params.get("description") is not None:
        params["Description"] = module.params["description"]


    try:
        existing = client.get(
            "DescribeApps",
            params,
            service_endpoint="apigateway.aliyuncs.com",
            api_version="2016-07-14",
        )

        data = existing
        for key in "Apps.AppItem".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateApp",
                    params,
                    service_endpoint="apigateway.aliyuncs.com",
                    api_version="2016-07-14",
                )
                changed = True
                module.exit_json(changed=changed, api_gateway_app=result)
            else:
                module.exit_json(changed=False, api_gateway_app=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteApp",
                    params,
                    service_endpoint="apigateway.aliyuncs.com",
                    api_version="2016-07-14",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
