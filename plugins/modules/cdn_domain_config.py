#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cdn_domain_config"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cdn_domain_config
short_description: Manage CDN domain configuration.
description:
  - Configure Alibaba Cloud CDN domain settings.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  domain_name:
    description: CDN domain name.
    type: str
  function_name:
    description: Configuration function name.
    type: str
  function_args:
    description: List of function argument dicts.
    type: list
    elements: dict
"""

EXAMPLES = r"""
- name: Manage CDN domain configuration
  stevefulme1.alibaba_cloud.cdn_domain_config:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
cdn_domain_config:
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
        domain_name=dict(type="str"),
        function_name=dict(type="str"),
        function_args=dict(type="list", elements="dict"),
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
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeCdnDomainConfigs",
            {},
            service_endpoint="cdn.aliyuncs.com",
            api_version="2018-05-10",
        )

        data = existing
        for key in "DomainConfigs.DomainConfig".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "BatchSetCdnDomainConfig",
                    {},
                    service_endpoint="cdn.aliyuncs.com",
                    api_version="2018-05-10",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    cdn_domain_config=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    cdn_domain_config=data[0],
                )

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
