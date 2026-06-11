#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.fc_custom_domain_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: fc_custom_domain_info
short_description: Query Function Compute custom domains.
description:
  - Retrieve information about Alibaba Cloud Function Compute custom domains.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  domain_name:
    description: Filter by custom domain name.
    type: str
"""

EXAMPLES = r"""
- name: Query all FC custom domains
  stevefulme1.alibaba_cloud.fc_custom_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific FC custom domain
  stevefulme1.alibaba_cloud.fc_custom_domain_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    domain_name: api.example.com
"""

RETURN = r"""
fc_custom_domains:
  description: List of Function Compute custom domains.
  returned: success
  type: list
  elements: dict
  sample:
    - domain_name: api.example.com
      protocol: HTTP,HTTPS
      route_config:
        routes:
          - path: /v1/*
            service_name: my-service
            function_name: my-function
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
            "ListCustomDomains",
            params,
            service_endpoint="fc.aliyuncs.com",
            api_version="2016-08-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in ["customDomains"]:
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, fc_custom_domains=data)


if __name__ == "__main__":
    main()
