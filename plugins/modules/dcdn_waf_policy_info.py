#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dcdn_waf_policy_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dcdn_waf_policy_info
short_description: Query DCDN WAF policies.
description:
  - Retrieve information about Alibaba Cloud Dynamic CDN WAF policies.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  policy_id:
    description: Filter by policy ID.
    type: str
  policy_name:
    description: Filter by policy name.
    type: str
"""

EXAMPLES = r"""
- name: Query all DCDN WAF policies
  stevefulme1.alibaba_cloud.dcdn_waf_policy_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific DCDN WAF policy
  stevefulme1.alibaba_cloud.dcdn_waf_policy_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    policy_id: "123456"
"""

RETURN = r"""
dcdn_waf_policies:
  description: List of DCDN WAF policies.
  returned: success
  type: list
  elements: dict
  sample:
    - policy_id: "123456"
      policy_name: default-policy
      policy_type: custom
      rule_count: 10
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        policy_id=dict(type="str"),
        policy_name=dict(type="str"),
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
    if module.params.get("policy_id"):
        params["PolicyId"] = module.params["policy_id"]
    if module.params.get("policy_name"):
        params["PolicyName"] = module.params["policy_name"]

    try:
        result = client.get(
            "DescribeDcdnWafPolicies",
            params,
            service_endpoint="dcdn.aliyuncs.com",
            api_version="2018-01-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Policies.Policy".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dcdn_waf_policies=data)


if __name__ == "__main__":
    main()
