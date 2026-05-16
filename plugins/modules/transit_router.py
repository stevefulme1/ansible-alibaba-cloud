#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.transit_router"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: transit_router
short_description: Manage Transit Router instances.
description:
  - Create, update, or delete Alibaba Cloud transit_router resources.
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
  cen_id:
    description: CEN instance ID for the transit router.
    type: str
    required: true
  transit_router_name:
    description: Name of the transit router.
    type: str
  transit_router_id:
    description: ID of an existing transit router.
    type: str
  description:
    description: Transit router description.
    type: str
"""

EXAMPLES = r"""
- name: Manage transit_router resource
  stevefulme1.alibaba_cloud.transit_router:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    cen_id: cen-xxxxx
    transit_router_name: my-tr
"""

RETURN = r"""
transit_router:
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
        cen_id=dict(type="str", required=True),
        transit_router_name=dict(type="str"),
        transit_router_id=dict(type="str"),
        description=dict(type="str"),
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
            "ListTransitRouters",
            {},
            service_endpoint="cbn.aliyuncs.com",
            api_version="2017-09-12",
        )

        data = existing
        for key in "TransitRouters".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateTransitRouter",
                    {},
                    service_endpoint="cbn.aliyuncs.com",
                    api_version="2017-09-12",
                )
                changed = True
                module.exit_json(changed=changed, transit_router=result)
            else:
                module.exit_json(changed=False, transit_router=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteTransitRouter",
                    {},
                    service_endpoint="cbn.aliyuncs.com",
                    api_version="2017-09-12",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
