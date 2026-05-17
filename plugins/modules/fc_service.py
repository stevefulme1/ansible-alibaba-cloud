#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.fc_service"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: fc_service
short_description: Manage Function Compute services.
description:
  - Create, update, or delete Alibaba Cloud fc_service resources.
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
  service_name:
    description: Name of the Function Compute service.
    type: str
    required: true
  description:
    description: Service description.
    type: str
  role:
    description: RAM role ARN for the service.
    type: str
  log_config:
    description: Log configuration for the service.
    type: dict
"""

EXAMPLES = r"""
- name: Manage fc_service resource
  stevefulme1.alibaba_cloud.fc_service:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    service_name: my-fc-service
"""

RETURN = r"""
fc_service:
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
        service_name=dict(type="str", required=True),
        description=dict(type="str"),
        role=dict(type="str"),
        log_config=dict(type="dict"),
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
    if module.params.get("service_name") is not None:
        params["ServiceName"] = module.params["service_name"]
    if module.params.get("description") is not None:
        params["Description"] = module.params["description"]
    if module.params.get("role") is not None:
        params["Role"] = module.params["role"]
    if module.params.get("log_config") is not None:
        params["LogConfig"] = module.params["log_config"]

    try:
        existing = client.get(
            "ListServices",
            params,
            service_endpoint="fc.aliyuncs.com",
            api_version="2021-04-06",
        )

        data = existing
        for key in "services".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateService",
                    params,
                    service_endpoint="fc.aliyuncs.com",
                    api_version="2021-04-06",
                )
                changed = True
                module.exit_json(changed=changed, fc_service=result)
            else:
                module.exit_json(changed=False, fc_service=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteService",
                    params,
                    service_endpoint="fc.aliyuncs.com",
                    api_version="2021-04-06",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
