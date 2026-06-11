#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.waf_domain_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: waf_domain_info
short_description: Query WAF protected domains.
description:
  - Retrieve information about Alibaba Cloud WAF protected domains.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: WAF instance ID.
    type: str
    required: true
  domain:
    description: Filter by domain name.
    type: str
"""

EXAMPLES = r"""
- name: Query all WAF protected domains
  stevefulme1.alibaba_cloud.waf_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: waf-xxxxx

- name: Query specific WAF domain
  stevefulme1.alibaba_cloud.waf_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: waf-xxxxx
    domain: example.com
"""

RETURN = r"""
waf_domains:
  description: List of WAF protected domains.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        instance_id=dict(type="str", required=True),
        domain=dict(type="str"),
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

    params = {
        "InstanceId": module.params["instance_id"],
    }
    if module.params.get("domain"):
        params["Domain"] = module.params["domain"]

    try:
        result = client.get(
            "DescribeDomainList",
            params,
            service_endpoint="wafopenapi.cn-hangzhou.aliyuncs.com",
            api_version="2019-09-10",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "DomainInfos".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, waf_domains=data)


if __name__ == "__main__":
    main()
