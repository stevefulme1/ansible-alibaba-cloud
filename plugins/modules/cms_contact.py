#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cms_contact"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cms_contact
short_description: Manage CloudMonitor alarm contacts.
description:
  - Create or delete Alibaba Cloud CloudMonitor alarm contacts.
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
  contact_name:
    description: Alarm contact name.
    type: str
  describe:
    description: Contact description.
    type: str
  channels_mail:
    description: Email address for notifications.
    type: str
  channels_sms:
    description: SMS phone number for notifications.
    type: str
"""

EXAMPLES = r"""
- name: Manage CloudMonitor alarm contacts
  stevefulme1.alibaba_cloud.cms_contact:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
cms_contact:
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
        contact_name=dict(type="str"),
        describe=dict(type="str"),
        channels_mail=dict(type="str"),
        channels_sms=dict(type="str"),
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
    if module.params.get("contact_name") is not None:
        params["ContactName"] = module.params["contact_name"]
    if module.params.get("describe") is not None:
        params["Describe"] = module.params["describe"]
    if module.params.get("channels_mail") is not None:
        params["ChannelsMail"] = module.params["channels_mail"]
    if module.params.get("channels_sms") is not None:
        params["ChannelsSms"] = module.params["channels_sms"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeContactList",
            params,
            service_endpoint="metrics.aliyuncs.com",
            api_version="2019-01-01",
        )

        data = existing
        for key in "Contacts.Contact".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PutContact",
                    params,
                    service_endpoint="metrics.aliyuncs.com",
                    api_version="2019-01-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    cms_contact=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    cms_contact=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteContact",
                    params,
                    service_endpoint="metrics.aliyuncs.com",
                    api_version="2019-01-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
