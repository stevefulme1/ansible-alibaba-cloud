#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.arms_prometheus_config_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: arms_prometheus_config_info
short_description: Query ARMS Prometheus configurations.
description:
  - Retrieve information about Alibaba Cloud ARMS Prometheus monitoring configurations.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  cluster_id:
    description: Filter by cluster ID.
    type: str
  exporter_type:
    description: Filter by exporter type.
    type: str
"""

EXAMPLES = r"""
- name: Query all ARMS Prometheus configurations
  stevefulme1.alibaba_cloud.arms_prometheus_config_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query Prometheus configurations for specific cluster
  stevefulme1.alibaba_cloud.arms_prometheus_config_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    cluster_id: cluster-123
"""

RETURN = r"""
arms_prometheus_configs:
  description: List of ARMS Prometheus configurations.
  returned: success
  type: list
  elements: dict
  sample:
    - cluster_id: cluster-123
      exporter_type: node-exporter
      config_yaml: "scrape_configs: []"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        cluster_id=dict(type="str"),
        exporter_type=dict(type="str"),
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

    params = {}
    if module.params.get("cluster_id"):
        params["ClusterId"] = module.params["cluster_id"]
    if module.params.get("exporter_type"):
        params["ExporterType"] = module.params["exporter_type"]

    try:
        result = client.get(
            "ListPrometheusAlertRules",
            params,
            service_endpoint="arms.aliyuncs.com",
            api_version="2019-08-08",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Exporters".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, arms_prometheus_configs=data)


if __name__ == "__main__":
    main()
