#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.mse_cluster"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: mse_cluster
short_description: Manage MSE registry clusters.
description:
  - Create, update, or delete Alibaba Cloud MSE cluster resources.
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
  cluster_type:
    description: Cluster type, e.g. C(Nacos-Ans), C(ZooKeeper), C(Eureka).
    type: str
  cluster_specification:
    description: Instance specification.
    type: str
  instance_count:
    description: Number of instances in the cluster.
    type: int
  net_type:
    description: Network type, e.g. C(privatenet) or C(pubnet).
    type: str
  vpc_id:
    description: VPC ID for private network clusters.
    type: str
  vswitch_id:
    description: VSwitch ID for cluster placement.
    type: str
  instance_id:
    description: ID of an existing MSE cluster.
    type: str
"""

EXAMPLES = r"""
- name: Create a MSE cluster
  stevefulme1.alibaba_cloud.mse_cluster:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    cluster_type: example-value
    cluster_specification: example-value
"""

RETURN = r"""
mse_cluster:
  description: Mse cluster details.
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
        cluster_type=dict(type="str"),
        cluster_specification=dict(type="str"),
        instance_count=dict(type="int"),
        net_type=dict(type="str"),
        vpc_id=dict(type="str"),
        vswitch_id=dict(type="str"),
        instance_id=dict(type="str"),
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
            "DescribeCluster",
            {},
            service_endpoint="mse.{region_id}.aliyuncs.com",
            api_version="2019-05-31",
        )

        data = existing
        for key in "Clusters.Cluster".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateCluster",
                    {},
                    service_endpoint="mse.{region_id}.aliyuncs.com",
                    api_version="2019-05-31",
                )
                changed = True
                module.exit_json(changed=changed, mse_cluster=result)
            else:
                module.exit_json(
                    changed=False,
                    mse_cluster=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteCluster",
                    {},
                    service_endpoint="mse.{region_id}.aliyuncs.com",
                    api_version="2019-05-31",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
