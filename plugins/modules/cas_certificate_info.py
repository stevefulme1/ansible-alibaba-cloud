#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cas_certificate_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cas_certificate_info
short_description: Query SSL certificates.
description:
  - Retrieve information about Alibaba Cloud SSL certificates.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  order_id:
    description: Filter by certificate order ID.
    type: str
  status:
    description: Filter by certificate status.
    type: str
"""

EXAMPLES = r"""
- name: Query all SSL certificates
  stevefulme1.alibaba_cloud.cas_certificate_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific SSL certificate
  stevefulme1.alibaba_cloud.cas_certificate_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    order_id: "123456"
"""

RETURN = r"""
cas_certificates:
  description: List of SSL certificates.
  returned: success
  type: list
  elements: dict
  sample:
    - order_id: "123456"
      domain: example.com
      status: issued
      cert_type: DV
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        order_id=dict(type="str"),
        status=dict(type="str"),
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
    if module.params.get("order_id"):
        params["OrderId"] = module.params["order_id"]
    if module.params.get("status"):
        params["Status"] = module.params["status"]

    try:
        result = client.get(
            "ListUserCertificateOrder",
            params,
            service_endpoint="cas.aliyuncs.com",
            api_version="2020-04-07",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "CertificateOrderList".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, cas_certificates=data)


if __name__ == "__main__":
    main()
