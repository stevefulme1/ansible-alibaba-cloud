#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.fc_custom_domain"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: fc_custom_domain
short_description: Manage Function Compute custom domain.
description:
  - Create, update, or delete Alibaba Cloud fc_custom_domain resources.
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
  domain_name:
    description: Custom domain name.
    type: str
  protocol:
    description: Protocol type (HTTP, HTTPS, HTTP,HTTPS).
    type: str
"""

EXAMPLES = r"""
- name: Manage fc_custom_domain
  stevefulme1.alibaba_cloud.fc_custom_domain:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    domain_name: api.example.com
    protocol: HTTPS
"""

RETURN = r"""
fc_custom_domain:
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
        domain_name=dict(type="str"),
        protocol=dict(type="str"),
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
            "ListCustomDomains",
            {},
            service_endpoint="fc.aliyuncs.com",
            api_version="2016-08-15",
        )

        data = result
        for key in ["customDomains"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateCustomDomain",
                    {},
                    service_endpoint="fc.aliyuncs.com",
                    api_version="2016-08-15",
                )
                changed = True
                module.exit_json(changed=changed, fc_custom_domain=result)
            else:
                module.exit_json(
                    changed=False,
                    fc_custom_domain=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteCustomDomain",
                    {},
                    service_endpoint="fc.aliyuncs.com",
                    api_version="2016-08-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
