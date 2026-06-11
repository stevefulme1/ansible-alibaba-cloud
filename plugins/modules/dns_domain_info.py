#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dns_domain_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dns_domain_info
short_description: Query Alibaba Cloud DNS domains.
description:
  - Retrieve information about Alibaba Cloud DNS domains.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  domain_name:
    description: Filter by domain name.
    type: str
"""

EXAMPLES = r"""
- name: Query all DNS domains
  stevefulme1.alibaba_cloud.dns_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific DNS domain
  stevefulme1.alibaba_cloud.dns_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    domain_name: example.com
"""

RETURN = r"""
dns_domains:
  description: List of DNS domains.
  returned: success
  type: list
  elements: dict
  sample:
    - domain_id: "123456"
      domain_name: example.com
      puny_code: example.com
      ali_domain: false
      record_count: 10
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
    if module.params.get("domain_name"):
        params["DomainName"] = module.params["domain_name"]

    try:
        result = client.get(
            "DescribeDomains",
            params,
            service_endpoint="alidns.aliyuncs.com",
            api_version="2015-01-09",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Domains.Domain".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dns_domains=data)


if __name__ == "__main__":
    main()
