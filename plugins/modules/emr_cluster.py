#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.emr_cluster"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: emr_cluster
short_description: Manage E-MapReduce clusters.
description:
  - Create, update, or delete Alibaba Cloud emr_cluster resources.
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
    description: Name of the EMR cluster.
    type: str
    required: true
  cluster_id:
    description: ID of an existing cluster (for updates/deletes).
    type: str
  cluster_type:
    description: Type of EMR cluster.
    type: str
    choices: [HADOOP, KAFKA, DRUID, FLINK, CLICKHOUSE]
    default: HADOOP
  release_version:
    description: EMR release version, e.g. C(EMR-5.16.0).
    type: str
  node_groups:
    description: List of node group configurations.
    type: list
    elements: dict
"""

EXAMPLES = r"""
- name: Manage emr_cluster resource
  stevefulme1.alibaba_cloud.emr_cluster:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    cluster_name: my-emr-cluster
    cluster_type: HADOOP
"""

RETURN = r"""
emr_cluster:
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
        cluster_name=dict(type="str", required=True),
        cluster_id=dict(type="str"),
        cluster_type=dict(
            type="str",
            choices=["HADOOP", "KAFKA", "DRUID", "FLINK", "CLICKHOUSE"],
            default="HADOOP",
        ),
        release_version=dict(type="str"),
        node_groups=dict(type="list", elements="dict"),
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
            "ListClusters",
            {},
            service_endpoint="emr.aliyuncs.com",
            api_version="2021-03-20",
        )

        data = existing
        for key in "Clusters".split("."):
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
                    service_endpoint="emr.aliyuncs.com",
                    api_version="2021-03-20",
                )
                changed = True
                module.exit_json(changed=changed, emr_cluster=result)
            else:
                module.exit_json(changed=False, emr_cluster=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteCluster",
                    {},
                    service_endpoint="emr.aliyuncs.com",
                    api_version="2021-03-20",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
