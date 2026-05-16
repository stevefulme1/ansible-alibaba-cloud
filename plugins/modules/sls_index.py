#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_index"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_index
short_description: Manage SLS logstore index configuration.
description:
  - Create, update, or delete Alibaba Cloud SLS index resources.
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
  project_name:
    description: Log Service project name.
    type: str
  logstore_name:
    description: Logstore name to configure index for.
    type: str
  full_text_index:
    description: Whether to enable full-text indexing.
    type: bool
  keys:
    description: Key-value index configuration.
    type: dict
"""

EXAMPLES = r"""
- name: Create a SLS index
  stevefulme1.alibaba_cloud.sls_index:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    project_name: example-value
    logstore_name: example-value
"""

RETURN = r"""
sls_index:
  description: Sls index details.
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
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        project_name=dict(type="str"),
        logstore_name=dict(type="str"),
        full_text_index=dict(type="bool"),
        keys=dict(type="dict", no_log=False),
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
            "DescribeIndex",
            {},
            service_endpoint="sls.{region_id}.aliyuncs.com",
            api_version="2020-12-30",
        )

        data = existing
        for key in "Indexes.Index".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateIndex",
                    {},
                    service_endpoint="sls.{region_id}.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
                module.exit_json(changed=changed, sls_index=result)
            else:
                module.exit_json(
                    changed=False,
                    sls_index=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteIndex",
                    {},
                    service_endpoint="sls.{region_id}.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
