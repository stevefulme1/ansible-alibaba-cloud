#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.oss_bucket"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oss_bucket
short_description: Manage OSS buckets.
description:
  - Create, update, or delete Alibaba Cloud OSS buckets.
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
  bucket_name:
    description: Name of the OSS bucket.
    type: str
  storage_class:
    description: Storage class.
    type: str
    choices: ['Standard', 'IA', 'Archive']
  acl:
    description: Bucket ACL.
    type: str
    choices: ['private', 'public-read', 'public-read-write']
"""

EXAMPLES = r"""
- name: Manage OSS buckets
  stevefulme1.alibaba_cloud.oss_bucket:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
oss_bucket:
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
        bucket_name=dict(type="str"),
        storage_class=dict(type="str", choices=["Standard", "IA", "Archive"]),
        acl=dict(type="str", choices=["private", "public-read", "public-read-write"]),
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
    if module.params.get("storage_class") is not None:
        params["StorageClass"] = module.params["storage_class"]
    if module.params.get("acl") is not None:
        params["ACL"] = module.params["acl"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "ListBuckets",
            params,
            service_endpoint="oss.aliyuncs.com",
            api_version="2019-05-17",
        )

        data = existing
        for key in "Buckets.Bucket".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PutBucket",
                    params,
                    service_endpoint="oss.aliyuncs.com",
                    api_version="2019-05-17",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    oss_bucket=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    oss_bucket=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteBucket",
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
