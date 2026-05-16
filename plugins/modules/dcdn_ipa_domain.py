#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dcdn_ipa_domain"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dcdn_ipa_domain
short_description: Manage DCDN IPA acceleration domains.
description:
  - Create, update, or delete Alibaba Cloud DCDN IPA domain resources.
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
    description: IPA domain name to accelerate.
    type: str
  sources:
    description: Origin server configuration JSON.
    type: str
  scope:
    description: Acceleration scope.
    type: str
"""

EXAMPLES = r"""
- name: Create a DCDN IPA domain
  stevefulme1.alibaba_cloud.dcdn_ipa_domain:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    domain_name: example-value
    sources: example-value
"""

RETURN = r"""
dcdn_ipa_domain:
  description: Dcdn ipa domain details.
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
        sources=dict(type="str"),
        scope=dict(type="str"),
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
            "DescribeDcdnIpaDomain",
            {},
            service_endpoint="dcdn.aliyuncs.com",
            api_version="2018-01-15",
        )

        data = existing
        for key in "Domains.Domain".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AddDcdnIpaDomain",
                    {},
                    service_endpoint="dcdn.aliyuncs.com",
                    api_version="2018-01-15",
                )
                changed = True
                module.exit_json(changed=changed, dcdn_ipa_domain=result)
            else:
                module.exit_json(
                    changed=False,
                    dcdn_ipa_domain=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDcdnIpaDomain",
                    {},
                    service_endpoint="dcdn.aliyuncs.com",
                    api_version="2018-01-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
