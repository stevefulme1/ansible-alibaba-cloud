#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.adb_cluster"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: adb_cluster
short_description: Manage AnalyticDB clusters.
description:
  - Create, update, or delete Alibaba Cloud adb_cluster resources.
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
  db_cluster_id:
    description: ID of an existing AnalyticDB cluster.
    type: str
  db_cluster_description:
    description: Cluster description.
    type: str
  db_cluster_category:
    description: Cluster category.
    type: str
    choices: [Cluster, MixedStorage]
    default: MixedStorage
  db_cluster_class:
    description: Cluster node specification.
    type: str
  db_node_count:
    description: Number of nodes in the cluster.
    type: int
  db_node_storage:
    description: Storage per node in GB.
    type: int
  pay_type:
    description: Payment type.
    type: str
    choices: [Postpaid, Prepaid]
    default: Postpaid
"""

EXAMPLES = r"""
- name: Manage adb_cluster resource
  stevefulme1.alibaba_cloud.adb_cluster:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    db_cluster_category: MixedStorage
    db_cluster_class: E8
    db_node_count: 2
"""

RETURN = r"""
adb_cluster:
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
        db_cluster_id=dict(type="str"),
        db_cluster_description=dict(type="str"),
        db_cluster_category=dict(
            type="str",
            choices=["Cluster", "MixedStorage"],
            default="MixedStorage",
        ),
        db_cluster_class=dict(type="str"),
        db_node_count=dict(type="int"),
        db_node_storage=dict(type="int"),
        pay_type=dict(type="str", choices=["Postpaid", "Prepaid"], default="Postpaid"),
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
    if module.params.get("db_cluster_id") is not None:
        params["DBClusterId"] = module.params["db_cluster_id"]
    if module.params.get("db_cluster_description") is not None:
        params["DBClusterDescription"] = module.params["db_cluster_description"]
    if module.params.get("db_cluster_category") is not None:
        params["DBClusterCategory"] = module.params["db_cluster_category"]
    if module.params.get("db_cluster_class") is not None:
        params["DBClusterClass"] = module.params["db_cluster_class"]
    if module.params.get("db_node_count") is not None:
        params["DBNodeCount"] = module.params["db_node_count"]
    if module.params.get("db_node_storage") is not None:
        params["DBNodeStorage"] = module.params["db_node_storage"]
    if module.params.get("pay_type") is not None:
        params["PayType"] = module.params["pay_type"]

    try:
        existing = client.get(
            "DescribeDBClusters",
            params,
            service_endpoint="adb.aliyuncs.com",
            api_version="2019-03-15",
        )

        data = existing
        for key in "Items.DBCluster".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDBCluster",
                    params,
                    service_endpoint="adb.aliyuncs.com",
                    api_version="2019-03-15",
                )
                changed = True
                module.exit_json(changed=changed, adb_cluster=result)
            else:
                module.exit_json(changed=False, adb_cluster=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDBCluster",
                    params,
                    service_endpoint="adb.aliyuncs.com",
                    api_version="2019-03-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
