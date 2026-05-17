#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_invocation"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_invocation
short_description: Manage command invocation.
description:
  - Create, update, or delete Alibaba Cloud ecs_invocation resources.
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
  command_id:
    description: Command ID to invoke.
    type: str
  instance_ids:
    description: Target instance IDs.
    type: str
  invoke_id:
    description: Invocation ID for stop.
    type: str
"""

EXAMPLES = r"""
- name: Manage ecs_invocation
  stevefulme1.alibaba_cloud.ecs_invocation:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    command_id: c-xxx
    instance_ids: i-xxx
"""

RETURN = r"""
ecs_invocation:
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
        command_id=dict(type="str"),
        instance_ids=dict(type="str"),
        invoke_id=dict(type="str"),
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
    if module.params.get("command_id") is not None:
        params["CommandId"] = module.params["command_id"]
    if module.params.get("instance_ids") is not None:
        params["InstanceIds"] = module.params["instance_ids"]
    if module.params.get("invoke_id") is not None:
        params["InvokeId"] = module.params["invoke_id"]

    try:
        result = client.get(
            "DescribeInvocations",
            params,
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )

        data = result
        for key in ["Invocations", "Invocation"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "InvokeCommand",
                    params,
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(changed=changed, ecs_invocation=result)
            else:
                module.exit_json(
                    changed=False,
                    ecs_invocation=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "StopInvocation",
                    params,
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
