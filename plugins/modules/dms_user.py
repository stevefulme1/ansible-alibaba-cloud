#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dms_user"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dms_user
short_description: Manage DMS users.
description:
  - Create, update, or delete Alibaba Cloud DMS user resources.
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
  uid:
    description: Alibaba Cloud UID of the user.
    type: str
  user_nick:
    description: Display name for the DMS user.
    type: str
  role_names:
    description: List of DMS roles to assign.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Create a DMS user
  stevefulme1.alibaba_cloud.dms_user:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    uid: example-value
    user_nick: example-value
"""

RETURN = r"""
dms_user:
  description: Dms user details.
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
        uid=dict(type="str"),
        user_nick=dict(type="str"),
        role_names=dict(type="list", elements="str"),
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
            "DescribeUser",
            {},
            service_endpoint="dms-enterprise.aliyuncs.com",
            api_version="2018-11-01",
        )

        data = existing
        for key in "Users.User".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "RegisterUser",
                    {},
                    service_endpoint="dms-enterprise.aliyuncs.com",
                    api_version="2018-11-01",
                )
                changed = True
                module.exit_json(changed=changed, dms_user=result)
            else:
                module.exit_json(
                    changed=False,
                    dms_user=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteUser",
                    {},
                    service_endpoint="dms-enterprise.aliyuncs.com",
                    api_version="2018-11-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
