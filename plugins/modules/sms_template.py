#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sms_template"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sms_template
short_description: Manage SMS template.
description:
  - Create, update, or delete Alibaba Cloud sms_template resources.
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
  template_name:
    description: SMS template name.
    type: str
  template_type:
    description: Template type (0=verification, 1=notification, 2=promotion).
    type: int
  template_content:
    description: Template body content.
    type: str
  template_code:
    description: Template code for delete.
    type: str
"""

EXAMPLES = r"""
- name: Manage sms_template
  stevefulme1.alibaba_cloud.sms_template:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    template_name: order-confirm
    template_content: Your code is ${code}
"""

RETURN = r"""
sms_template:
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
        template_name=dict(type="str"),
        template_type=dict(type="int"),
        template_content=dict(type="str"),
        template_code=dict(type="str"),
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
        result = client.get(
            "QuerySmsTemplateList",
            {},
            service_endpoint="dysmsapi.aliyuncs.com",
            api_version="2017-05-25",
        )

        data = result
        for key in ["SmsTemplateList", "SmsTemplate"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AddSmsTemplate",
                    {},
                    service_endpoint="dysmsapi.aliyuncs.com",
                    api_version="2017-05-25",
                )
                changed = True
                module.exit_json(changed=changed, sms_template=result)
            else:
                module.exit_json(
                    changed=False,
                    sms_template=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteSmsTemplate",
                    {},
                    service_endpoint="dysmsapi.aliyuncs.com",
                    api_version="2017-05-25",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
