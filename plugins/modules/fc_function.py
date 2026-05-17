#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.fc_function"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: fc_function
short_description: Manage Function Compute functions.
description:
  - Create, update, or delete Alibaba Cloud fc_function resources.
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
    description: Name of the parent service.
    type: str
    required: true
  function_name:
    description: Name of the function.
    type: str
    required: true
  runtime:
    description: Runtime environment, e.g. C(python3.10), C(nodejs18).
    type: str
  handler:
    description: Entry point handler, e.g. C(index.handler).
    type: str
  memory_size:
    description: Memory size in MB (128 to 32768).
    type: int
  timeout:
    description: Function execution timeout in seconds.
    type: int
"""

EXAMPLES = r"""
- name: Manage fc_function resource
  stevefulme1.alibaba_cloud.fc_function:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    service_name: my-fc-service
    function_name: my-function
    runtime: python3.10
    handler: index.handler
    memory_size: 256
    timeout: 60
"""

RETURN = r"""
fc_function:
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
        function_name=dict(type="str", required=True),
        runtime=dict(type="str"),
        handler=dict(type="str"),
        memory_size=dict(type="int"),
        timeout=dict(type="int"),
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
    if module.params.get("function_name") is not None:
        params["FunctionName"] = module.params["function_name"]
    if module.params.get("runtime") is not None:
        params["Runtime"] = module.params["runtime"]
    if module.params.get("handler") is not None:
        params["Handler"] = module.params["handler"]
    if module.params.get("memory_size") is not None:
        params["MemorySize"] = module.params["memory_size"]


    try:
        existing = client.get(
            "ListFunctions",
            params,
            service_endpoint="fc.aliyuncs.com",
            api_version="2021-04-06",
        )

        data = existing
        for key in "functions".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateFunction",
                    params,
                    service_endpoint="fc.aliyuncs.com",
                    api_version="2021-04-06",
                )
                changed = True
                module.exit_json(changed=changed, fc_function=result)
            else:
                module.exit_json(changed=False, fc_function=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteFunction",
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
