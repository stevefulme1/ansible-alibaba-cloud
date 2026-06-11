#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dns_domain_group_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dns_domain_group_info
short_description: Query Alibaba Cloud DNS domain groups.
description:
  - Retrieve information about Alibaba Cloud DNS domain groups.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  group_id:
    description: Filter by group ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all DNS domain groups
  stevefulme1.alibaba_cloud.dns_domain_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific DNS domain group
  stevefulme1.alibaba_cloud.dns_domain_group_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    group_id: "123"
"""

RETURN = r"""
dns_domain_groups:
  description: List of DNS domain groups.
  returned: success
  type: list
  elements: dict
  sample:
    - group_id: "123"
      group_name: production
      domain_count: 5
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        group_id=dict(type="str"),
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

    params = {}
    if module.params.get("group_id"):
        params["GroupId"] = module.params["group_id"]

    try:
        result = client.get(
            "DescribeDomainGroups",
            params,
            service_endpoint="alidns.aliyuncs.com",
            api_version="2015-01-09",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "DomainGroups.DomainGroup".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dns_domain_groups=data)


if __name__ == "__main__":
    main()
