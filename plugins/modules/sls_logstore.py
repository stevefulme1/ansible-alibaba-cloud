#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_logstore"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_logstore
short_description: Manage Log Service logstores.
description:
  - Create or delete logstores in an Alibaba Cloud Log Service project.
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
  project_name:
    description: Log Service project name.
    type: str
  logstore_name:
    description: Logstore name.
    type: str
  ttl:
    description: Data retention period in days.
    type: int
  shard_count:
    description: Number of shards.
    type: int
"""

EXAMPLES = r"""
- name: Manage Log Service logstores
  stevefulme1.alibaba_cloud.sls_logstore:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
sls_logstore:
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
        project_name=dict(type="str"),
        logstore_name=dict(type="str"),
        ttl=dict(type="int"),
        shard_count=dict(type="int"),
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
            "GetLogStore",
            {},
            service_endpoint="sls.aliyuncs.com",
            api_version="2020-12-30",
        )

        data = existing
        for key in "logstore".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateLogStore",
                    {},
                    service_endpoint="sls.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    sls_logstore=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    sls_logstore=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteLogStore",
                    {},
                    service_endpoint="sls.aliyuncs.com",
                    api_version="2020-12-30",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
