#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dcdn_ipa_domain_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dcdn_ipa_domain_info
short_description: Query DCDN IPA domains.
description:
  - Retrieve information about Alibaba Cloud Dynamic CDN IPA (IP Application Accelerator) domains.
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
- name: Query all DCDN IPA domains
  stevefulme1.alibaba_cloud.dcdn_ipa_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific DCDN IPA domain
  stevefulme1.alibaba_cloud.dcdn_ipa_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    domain_name: example.com
"""

RETURN = r"""
dcdn_ipa_domains:
  description: List of DCDN IPA domains.
  returned: success
  type: list
  elements: dict
  sample:
    - domain_name: example.com
      cname: example.com.w.kunlunsl.com
      domain_status: online
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
            "DescribeDcdnIpaDomain",
            params,
            service_endpoint="dcdn.aliyuncs.com",
            api_version="2018-01-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Domains.Domain".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dcdn_ipa_domains=data)


if __name__ == "__main__":
    main()
