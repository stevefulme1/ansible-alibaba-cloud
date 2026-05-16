#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.alidns_gtm_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: alidns_gtm_instance
short_description: Manage Global Traffic Manager instances.
description:
  - Create or delete manage global traffic manager instances.
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
  instance_id:
    description: GTM instance ID.
    type: str
  instance_name:
    description: GTM instance name.
    type: str
  package_edition:
    description: GTM package edition.
    type: str
    choices: ['standard', 'ultimate']"""

EXAMPLES = r"""
- name: Manage Global Traffic Manager instances.
  stevefulme1.alibaba_cloud.alidns_gtm_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
alidns_gtm_instance:
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
        instance_id=dict(type="str"),
        instance_name=dict(type="str"),
        package_edition=dict(type="str", choices=["standard", "ultimate"]),
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
        existing = client.get(
            "DescribeDnsGtmInstances",
            {},
            service_endpoint="alidns.aliyuncs.com",
            api_version="2015-01-09",
        )

        data = existing
        for key in "GtmInstances".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "AddDnsGtmMonitor",
                    {},
                    service_endpoint="alidns.aliyuncs.com",
                    api_version="2015-01-09",
                )
                changed = True
                module.exit_json(changed=changed, alidns_gtm_instance=result)
            else:
                module.exit_json(changed=False, alidns_gtm_instance=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteGtmInstance",
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
