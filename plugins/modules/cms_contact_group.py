#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cms_contact_group"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cms_contact_group
short_description: Manage CloudMonitor contact groups.
description:
  - Create or delete Alibaba Cloud CloudMonitor alarm contact groups.
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
  contact_group_name:
    description: Contact group name.
    type: str
  describe:
    description: Contact group description.
    type: str
  contact_names:
    description: List of contact names in the group.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Manage CloudMonitor contact groups
  stevefulme1.alibaba_cloud.cms_contact_group:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
cms_contact_group:
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
        contact_group_name=dict(type="str"),
        describe=dict(type="str"),
        contact_names=dict(type="list", elements="str"),
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
    if module.params.get("contact_group_name") is not None:
        params["ContactGroupName"] = module.params["contact_group_name"]
    if module.params.get("describe") is not None:
        params["Describe"] = module.params["describe"]
    if module.params.get("contact_names") is not None:
        params["ContactNames"] = module.params["contact_names"]


    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeContactGroupList",
            params,
            service_endpoint="metrics.aliyuncs.com",
            api_version="2019-01-01",
        )

        data = existing
        for key in "ContactGroupList.ContactGroup".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PutContactGroup",
                    params,
                    service_endpoint="metrics.aliyuncs.com",
                    api_version="2019-01-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    cms_contact_group=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    cms_contact_group=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteContactGroup",
                    params,
                    service_endpoint="metrics.aliyuncs.com",
                    api_version="2019-01-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
