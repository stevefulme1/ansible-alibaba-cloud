#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.arms_alert_contact"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: arms_alert_contact
short_description: Manage ARMS alert contacts.
description:
  - Create or delete manage arms alert contacts.
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
  contact_id:
    description: Alert contact ID.
    type: int
  contact_name:
    description: Contact name.
    type: str
  email:
    description: Contact email address.
    type: str
  phone:
    description: Contact phone number.
    type: str"""

EXAMPLES = r"""
- name: Manage ARMS alert contacts.
  stevefulme1.alibaba_cloud.arms_alert_contact:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
arms_alert_contact:
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
        contact_id=dict(type="int"),
        contact_name=dict(type="str"),
        email=dict(type="str"),
        phone=dict(type="str"),
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
            "SearchAlertContact",
            {},
            service_endpoint="arms.aliyuncs.com",
            api_version="2019-08-08",
        )

        data = existing
        for key in "PageBean.Contacts".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateAlertContact",
                    {},
                    service_endpoint="arms.aliyuncs.com",
                    api_version="2019-08-08",
                )
                changed = True
                module.exit_json(changed=changed, arms_alert_contact=result)
            else:
                module.exit_json(changed=False, arms_alert_contact=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteAlertContact",
                    {},
                    service_endpoint="arms.aliyuncs.com",
                    api_version="2019-08-08",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
