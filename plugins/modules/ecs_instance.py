#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_instance
short_description: Manage ECS instances.
description:
  - Create, update, or delete Alibaba Cloud ecs_instance resources.
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
  instance_name:
    description: Display name of the ECS instance.
    type: str
  instance_type:
    description: Instance specification, e.g. C(ecs.g6.large).
    type: str
  image_id:
    description: Image ID to launch the instance from.
    type: str
  vswitch_id:
    description: VSwitch ID for VPC-based instances.
    type: str
  instance_id:
    description: ID of an existing instance (for stop/delete).
    type: str
"""

EXAMPLES = r"""
- name: Create an ECS instance
  stevefulme1.alibaba_cloud.ecs_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_name: my-ecs
    instance_type: ecs.g6.large
    image_id: centos_7_9_x64_20G_alibase_20230816.vhd
    vswitch_id: vsw-xxxxx
"""

RETURN = r"""
instance:
  description: Instance details.
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
        instance_name=dict(type="str"),
        instance_type=dict(type="str"),
        image_id=dict(type="str"),
        vswitch_id=dict(type="str"),
        instance_id=dict(type="str"),
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
    if module.params.get("instance_name") is not None:
        params["InstanceName"] = module.params["instance_name"]
    if module.params.get("instance_type") is not None:
        params["InstanceType"] = module.params["instance_type"]
    if module.params.get("image_id") is not None:
        params["ImageId"] = module.params["image_id"]
    if module.params.get("vswitch_id") is not None:
        params["VSwitchId"] = module.params["vswitch_id"]
    if module.params.get("instance_id") is not None:
        params["InstanceId"] = module.params["instance_id"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeInstances",
            params,
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )

        data = existing
        for key in "Instances.Instance".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "RunInstances",
                    params,
                    service_endpoint="ecs.aliyuncs.com",
                    api_version="2014-05-26",
                )
                changed = True
                module.exit_json(changed=changed, ecs_instance=result)
            else:
                module.exit_json(
                    changed=False,
                    ecs_instance=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteInstance",
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
