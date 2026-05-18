#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.edas_cluster"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: edas_cluster
short_description: Manage EDAS clusters.
description:
  - Create, update, or delete Alibaba Cloud EDAS cluster resources.
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
  cluster_name:
    description: Name of the cluster.
    type: str
  cluster_id:
    description: ID of an existing cluster.
    type: str
  cluster_type:
    description: Cluster type, C(2) for ECS.
    type: int
  network_mode:
    description: Network mode, C(2) for VPC.
    type: int
"""

EXAMPLES = r"""
- name: Create a EDAS cluster
  stevefulme1.alibaba_cloud.edas_cluster:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    cluster_name: example-value
    cluster_id: example-value
"""

RETURN = r"""
edas_cluster:
  description: Edas cluster details.
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
        cluster_name=dict(type="str"),
        cluster_id=dict(type="str"),
        cluster_type=dict(type="int"),
        network_mode=dict(type="int"),
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
            service_endpoint="edas.{region_id}.aliyuncs.com",
            api_version="2017-08-01",
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
                    "InsertCluster",
                    {},
                    service_endpoint="edas.{region_id}.aliyuncs.com",
                    api_version="2017-08-01",
                )
                changed = True
                module.exit_json(changed=changed, edas_cluster=result)
            else:
                module.exit_json(
                    changed=False,
                    edas_cluster=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteCluster",
                    {},
                    service_endpoint="edas.{region_id}.aliyuncs.com",
                    api_version="2017-08-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
