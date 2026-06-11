#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dns_record_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dns_record_info
short_description: Query Alibaba Cloud DNS records.
description:
  - Retrieve information about Alibaba Cloud DNS records.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  domain_name:
    description: Domain name.
    type: str
  record_id:
    description: Filter by record ID.
    type: str
  type:
    description: Filter by record type (A, AAAA, CNAME, etc.).
    type: str
  rr:
    description: Filter by host record (RR).
    type: str
"""

EXAMPLES = r"""
- name: Query all DNS records for a domain
  stevefulme1.alibaba_cloud.dns_record_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    domain_name: example.com

- name: Query specific DNS record
  stevefulme1.alibaba_cloud.dns_record_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    domain_name: example.com
    record_id: "123456"
"""

RETURN = r"""
dns_records:
  description: List of DNS records.
  returned: success
  type: list
  elements: dict
  sample:
    - record_id: "123456"
      rr: www
      type: A
      value: 192.0.2.1
      ttl: 600
      priority: 10
      status: ENABLE
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
        record_id=dict(type="str"),
        type=dict(type="str"),
        rr=dict(type="str"),
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
    if module.params.get("record_id"):
        params["RecordId"] = module.params["record_id"]
    if module.params.get("type"):
        params["Type"] = module.params["type"]
    if module.params.get("rr"):
        params["RRKeyWord"] = module.params["rr"]

    try:
        result = client.get(
            "DescribeDomainRecords",
            params,
            service_endpoint="alidns.aliyuncs.com",
            api_version="2015-01-09",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "DomainRecords.Record".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dns_records=data)


if __name__ == "__main__":
    main()
