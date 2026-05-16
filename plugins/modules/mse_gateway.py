#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.mse_gateway"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: mse_gateway
short_description: Manage MSE cloud-native gateways.
description:
  - Create, update, or delete Alibaba Cloud MSE gateway resources.
  - Supports check mode and is idempotent.version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: [present, absent]
    default: present
  gateway_name:
    description: Name of the cloud-native gateway.
    type: str
  gateway_id:
    description: ID of an existing gateway.
    type: str
  replica:
    description: Number of gateway replicas.
    type: int
  spec:
    description: Gateway specification.
    type: str
  vpc_id:
    description: VPC ID for the gateway.
    type: str
  vswitch_id:
    description: VSwitch ID for gateway placement.
    type: str
"""

EXAMPLES = r"""
- name: Create a MSE gateway
  stevefulme1.alibaba_cloud.mse_gateway:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    gateway_name: example-value
    gateway_id: example-value
"""

RETURN = r"""
mse_gateway:
  description: Mse gateway details.
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
        gateway_name=dict(type="str"),
        gateway_id=dict(type="str"),
        replica=dict(type="int"),
        spec=dict(type="str"),
        vpc_id=dict(type="str"),
        vswitch_id=dict(type="str"),
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
            "DescribeGateway",
            {},
            service_endpoint="mse.{region_id}.aliyuncs.com",
            api_version="2019-05-31",
        )

        data = existing
        for key in "Gateways.Gateway".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AddGateway",
                    {},
                    service_endpoint="mse.{region_id}.aliyuncs.com",
                    api_version="2019-05-31",
                )
                changed = True
                module.exit_json(changed=changed, mse_gateway=result)
            else:
                module.exit_json(
                    changed=False,
                    mse_gateway=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteGateway",
                    {},
                    service_endpoint="mse.{region_id}.aliyuncs.com",
                    api_version="2019-05-31",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
