#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cdn_domain_config_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cdn_domain_config_info
short_description: Query cdn domain config resources.
description:
  - Retrieve information about Alibaba Cloud cdn domain config resources.
  - This is a read-only module that does not modify any resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  domain_name:
    description: Filter by domain name.
    type: str
  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
"""

EXAMPLES = r"""
- name: List all cdn domain config resources
  stevefulme1.alibaba_cloud.cdn_domain_config_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    domain_name: example-value
"""

RETURN = r"""
cdn_domain_configs:
  description: List of cdn domain config resources.
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
        domain_name=dict(type="str"),
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
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
            "DescribeCdnDomainConfigs",
            params,
            service_endpoint="cdn.aliyuncs.com",
            api_version="2018-05-10",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    data = data.get("DomainConfigs", {})
    data = data.get("DomainConfig", {})
    if not isinstance(data, list):
        data = [data] if data else []

    module.exit_json(changed=False, cdn_domain_configs=data)


if __name__ == "__main__":
    main()
