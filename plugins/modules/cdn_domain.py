#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cdn_domain"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cdn_domain
short_description: Manage CDN domains.
description:
  - Add, update, or remove Alibaba Cloud CDN domain acceleration.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  domain_name:
    description: Domain name to accelerate.
    type: str
  cdn_type:
    description: CDN business type.
    type: str
    choices: ['web', 'download', 'video']
  sources:
    description: Origin server address.
    type: str
  source_type:
    description: Origin server type.
    type: str
    choices: ['ipaddr', 'domain', 'oss']
"""

EXAMPLES = r"""
- name: Manage CDN domains
  stevefulme1.alibaba_cloud.cdn_domain:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
cdn_domain:
  description: Resource details.
  returned: success
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        state=dict(type="str", choices=["present", "absent"], default="present"),
        domain_name=dict(type="str"),
        cdn_type=dict(type="str", choices=["web", "download", "video"]),
        sources=dict(type="str"),
        source_type=dict(type="str", choices=["ipaddr", "domain", "oss"]),
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

    params = {}
    if module.params.get("domain_name") is not None:
        params["DomainName"] = module.params["domain_name"]
    if module.params.get("cdn_type") is not None:
        params["CdnType"] = module.params["cdn_type"]
    if module.params.get("sources") is not None:
        params["Sources"] = module.params["sources"]
    if module.params.get("source_type") is not None:
        params["SourceType"] = module.params["source_type"]


    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeUserDomains",
            params,
            service_endpoint="cdn.aliyuncs.com",
            api_version="2018-05-10",
        )

        data = existing
        for key in "Domains.PageData".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AddCdnDomain",
                    params,
                    service_endpoint="cdn.aliyuncs.com",
                    api_version="2018-05-10",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    cdn_domain=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    cdn_domain=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteCdnDomain",
                    params,
                    service_endpoint="cdn.aliyuncs.com",
                    api_version="2018-05-10",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
