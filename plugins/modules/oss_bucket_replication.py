#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.oss_bucket_replication"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oss_bucket_replication
short_description: Manage cross-region replication.
description:
  - Create, update, or delete Alibaba Cloud oss_bucket_replication resources.
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
  bucket_name:
    description: Source bucket name.
    type: str
  target_bucket_name:
    description: Destination bucket name.
    type: str
  target_location:
    description: Destination region.
    type: str
"""

EXAMPLES = r"""
- name: Manage oss_bucket_replication
  stevefulme1.alibaba_cloud.oss_bucket_replication:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    bucket_name: src-bucket
    target_bucket_name: dst-bucket
"""

RETURN = r"""
replication:
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
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        bucket_name=dict(type="str"),
        target_bucket_name=dict(type="str"),
        target_location=dict(type="str"),
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
    if module.params.get("bucket_name") is not None:
        params["BucketName"] = module.params["bucket_name"]
    if module.params.get("target_bucket_name") is not None:
        params["TargetBucketName"] = module.params["target_bucket_name"]
    if module.params.get("target_location") is not None:
        params["TargetLocation"] = module.params["target_location"]

    try:
        result = client.get(
            "GetBucketReplication",
            params,
            service_endpoint="oss.aliyuncs.com",
            api_version="2019-05-17",
        )

        data = result
        for key in ["ReplicationRules"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PutBucketReplication",
                    params,
                    service_endpoint="oss.aliyuncs.com",
                    api_version="2019-05-17",
                )
                changed = True
                module.exit_json(changed=changed, replication=result)
            else:
                module.exit_json(
                    changed=False,
                    replication=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteBucketReplication",
                    params,
                    service_endpoint="oss.aliyuncs.com",
                    api_version="2019-05-17",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
