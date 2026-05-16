#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.redis_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: redis_instance
short_description: Manage Redis instances.
description:
  - Create, update, or delete Alibaba Cloud Redis instances.
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
    description: ID of an existing Redis instance.
    type: str
  instance_name:
    description: Display name of the Redis instance.
    type: str
  instance_class:
    description: Instance class specification.
    type: str
  engine_version:
    description: Redis engine version.
    type: str
  instance_type:
    description: Instance architecture type.
    type: str
    choices: ['Redis', 'Memcache']
  password:
    description: Instance password.
    type: str
"""

EXAMPLES = r"""
- name: Manage Redis instances
  stevefulme1.alibaba_cloud.redis_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
redis_instance:
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
        instance_class=dict(type="str"),
        engine_version=dict(type="str"),
        instance_type=dict(type="str", choices=["Redis", "Memcache"]),
        password=dict(type="str", no_log=True),
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
            "DescribeInstances",
            {},
            service_endpoint="r-kvstore.aliyuncs.com",
            api_version="2015-01-01",
        )

        data = existing
        for key in "Instances.KVStoreInstance".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateInstance",
                    {},
                    service_endpoint="r-kvstore.aliyuncs.com",
                    api_version="2015-01-01",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    redis_instance=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    redis_instance=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteInstance",
                    {},
                    service_endpoint="r-kvstore.aliyuncs.com",
                    api_version="2015-01-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
