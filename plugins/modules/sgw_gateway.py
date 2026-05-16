#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sgw_gateway"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sgw_gateway
short_description: Manage Cloud Storage Gateways.
description:
  - Create or delete manage cloud storage gateways.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  gateway_id:
    description: Storage gateway ID.
    type: str
  name:
    description: Gateway display name.
    type: str
  gateway_class:
    description: Gateway performance class.
    type: str
    choices: ['Basic', 'Standard', 'Enhanced', 'Advanced']"""

EXAMPLES = r"""
- name: Manage Cloud Storage Gateways.
  stevefulme1.alibaba_cloud.sgw_gateway:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
sgw_gateway:
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
        gateway_id=dict(type="str"),
        name=dict(type="str"),
        gateway_class=dict(
            type="str", choices=["Basic", "Standard", "Enhanced", "Advanced"]
        ),
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
            "DescribeGateways",
            {},
            service_endpoint="sgw.aliyuncs.com",
            api_version="2018-05-11",
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
                    "CreateGateway",
                    {},
                    service_endpoint="sgw.aliyuncs.com",
                    api_version="2018-05-11",
                )
                changed = True
                module.exit_json(changed=changed, sgw_gateway=result)
            else:
                module.exit_json(changed=False, sgw_gateway=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteGateway",
                    {},
                    service_endpoint="sgw.aliyuncs.com",
                    api_version="2018-05-11",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
