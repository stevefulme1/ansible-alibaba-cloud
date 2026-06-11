#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sso_oidc_provider_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sso_oidc_provider_info
short_description: Query OIDC identity providers.
description:
  - Retrieve information about Alibaba Cloud OIDC identity providers.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  oidc_provider_name:
    description: Filter by OIDC provider name.
    type: str
"""

EXAMPLES = r"""
- name: Query all OIDC providers
  stevefulme1.alibaba_cloud.sso_oidc_provider_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific OIDC provider
  stevefulme1.alibaba_cloud.sso_oidc_provider_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    oidc_provider_name: my-provider
"""

RETURN = r"""
sso_oidc_providers:
  description: List of OIDC identity providers.
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
        oidc_provider_name=dict(type="str"),
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
    if module.params.get("oidc_provider_name"):
        params["OIDCProviderName"] = module.params["oidc_provider_name"]

    try:
        result = client.get(
            "ListOIDCProviders",
            params,
            service_endpoint="ims.aliyuncs.com",
            api_version="2019-08-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "OIDCProviders.OIDCProvider".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, sso_oidc_providers=data)


if __name__ == "__main__":
    main()
