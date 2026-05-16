#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sso_user"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sso_user
short_description: Manage CloudSSO users.
description:
  - Create or delete manage cloudsso users.
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
  directory_id:
    description: CloudSSO directory ID.
    type: str
    required: true
  user_name:
    description: CloudSSO user name.
    type: str
  display_name:
    description: User display name.
    type: str
  email:
    description: User email address.
    type: str"""

EXAMPLES = r"""
- name: Manage CloudSSO users.
  stevefulme1.alibaba_cloud.sso_user:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
sso_user:
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
        directory_id=dict(type="str", required=True),
        user_name=dict(type="str"),
        display_name=dict(type="str"),
        email=dict(type="str"),
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
            "ListUsers",
            {},
            service_endpoint="cloudsso.aliyuncs.com",
            api_version="2021-05-15",
        )

        data = existing
        for key in "Users".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateUser",
                    {},
                    service_endpoint="cloudsso.aliyuncs.com",
                    api_version="2021-05-15",
                )
                changed = True
                module.exit_json(changed=changed, sso_user=result)
            else:
                module.exit_json(changed=False, sso_user=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteUser",
                    {},
                    service_endpoint="cloudsso.aliyuncs.com",
                    api_version="2021-05-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
