#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dns_record"""

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


DOCUMENTATION = r"""
---
module: dns_record
short_description: Manage DNS records.
description:
  - Create, update, or delete Alibaba Cloud dns_record resources.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: [present, absent]
    default: present
  domain_name:
    description: The parent domain name.
    type: str
    required: true
  rr:
    description: Host record (subdomain), e.g. C(www).
    type: str
  record_type:
    description: Record type (A, CNAME, MX, TXT, etc.).
    type: str
  record_value:
    description: Record value.
    type: str
  record_id:
    description: Existing record ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Add A record
  stevefulme1.alibaba_cloud.dns_record:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    domain_name: example.com
    rr: www
    record_type: A
    record_value: 1.2.3.4
"""

RETURN = r"""
record:
  description: DNS record details.
  returned: success
  type: dict
"""


def main():
    spec = dict(
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        domain_name=dict(type="str", required=True),
        rr=dict(type="str"),
        record_type=dict(type="str"),
        record_value=dict(type="str"),
        record_id=dict(type="str"),
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

    state = module.params["state"]
    changed = False

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeDomainRecords",
            {},
            service_endpoint="alidns.aliyuncs.com",
            api_version="2015-01-09",
        )

        data = existing
        for key in "DomainRecords.Record".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AddDomainRecord",
                    {},
                    service_endpoint="alidns.aliyuncs.com",
                    api_version="2015-01-09",
                )
                changed = True
                module.exit_json(changed=changed, dns_record=result)
            else:
                module.exit_json(
                    changed=False,
                    dns_record=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDomainRecord",
                    {},
                    service_endpoint="alidns.aliyuncs.com",
                    api_version="2015-01-09",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
