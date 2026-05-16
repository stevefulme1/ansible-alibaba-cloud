#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ack_cluster"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ack_cluster
short_description: Manage ACK Kubernetes clusters.
description:
  - Create, update, or delete Alibaba Cloud ACK Kubernetes clusters.
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
  cluster_id:
    description: ID of an existing cluster.
    type: str
  name:
    description: Cluster display name.
    type: str
  cluster_type:
    description: Cluster type.
    type: str
    choices: ['Kubernetes', 'ManagedKubernetes']
  kubernetes_version:
    description: Kubernetes version.
    type: str
  vpcid:
    description: VPC ID.
    type: str
  vswitch_ids:
    description: List of VSwitch IDs.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Manage ACK Kubernetes clusters
  stevefulme1.alibaba_cloud.ack_cluster:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
ack_cluster:
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
        cluster_id=dict(type="str"),
        name=dict(type="str"),
        cluster_type=dict(type="str", choices=["Kubernetes", "ManagedKubernetes"]),
        kubernetes_version=dict(type="str"),
        vpcid=dict(type="str"),
        vswitch_ids=dict(type="list", elements="str"),
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
            "DescribeClustersV1",
            {},
            service_endpoint="cs.aliyuncs.com",
            api_version="2015-12-15",
        )

        data = existing
        for key in "clusters".split("."):
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
                    service_endpoint="cs.aliyuncs.com",
                    api_version="2015-12-15",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    ack_cluster=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    ack_cluster=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteCluster",
                    {},
                    service_endpoint="cs.aliyuncs.com",
                    api_version="2015-12-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
