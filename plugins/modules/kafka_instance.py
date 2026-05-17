#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.kafka_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: kafka_instance
short_description: Manage Kafka instances.
description:
  - Create, update, or delete Alibaba Cloud Kafka instance resources.
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
  instance_name:
    description: Display name of the Kafka instance.
    type: str
  instance_id:
    description: ID of an existing Kafka instance.
    type: str
  disk_type:
    description: Disk type, e.g. C(0) for SSD.
    type: str
  disk_size:
    description: Disk size in GB.
    type: int
  deploy_type:
    description: Deployment type, e.g. C(5) for VPC.
    type: str
  io_max:
    description: Maximum I/O throughput in MB/s.
    type: int
"""

EXAMPLES = r"""
- name: Create a Kafka instance
  stevefulme1.alibaba_cloud.kafka_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_name: example-value
    instance_id: example-value
"""

RETURN = r"""
kafka_instance:
  description: Kafka instance details.
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
        instance_name=dict(type="str"),
        instance_id=dict(type="str"),
        disk_type=dict(type="str"),
        disk_size=dict(type="int"),
        deploy_type=dict(type="str"),
        io_max=dict(type="int"),
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
    if module.params.get("instance_name") is not None:
        params["InstanceName"] = module.params["instance_name"]
    if module.params.get("instance_id") is not None:
        params["InstanceId"] = module.params["instance_id"]
    if module.params.get("disk_type") is not None:
        params["DiskType"] = module.params["disk_type"]
    if module.params.get("disk_size") is not None:
        params["DiskSize"] = module.params["disk_size"]
    if module.params.get("deploy_type") is not None:
        params["DeployType"] = module.params["deploy_type"]
    if module.params.get("io_max") is not None:
        params["IoMax"] = module.params["io_max"]


    try:
        existing = client.get(
            "DescribeInstance",
            params,
            service_endpoint="alikafka.{region_id}.aliyuncs.com",
            api_version="2019-09-16",
        )

        data = existing
        for key in "Instances.InstanceVO".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "Create",
                    params,
                    service_endpoint="alikafka.{region_id}.aliyuncs.com",
                    api_version="2019-09-16",
                )
                changed = True
                module.exit_json(changed=changed, kafka_instance=result)
            else:
                module.exit_json(
                    changed=False,
                    kafka_instance=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteInstance",
                    params,
                    service_endpoint="alikafka.{region_id}.aliyuncs.com",
                    api_version="2019-09-16",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
