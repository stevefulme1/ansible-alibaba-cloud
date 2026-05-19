# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Alibaba Cloud dynamic inventory plugin."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
name: alibaba_cloud_inventory
short_description: Alibaba Cloud ECS dynamic inventory.
description:
  - Queries ECS instances to build a dynamic Ansible inventory.
  - Groups hosts by region, instance type, status, VPC, and security group.
  - Populates host variables with instance metadata.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - constructed
  - inventory_cache
options:
  access_key_id:
    description: Alibaba Cloud access key ID.
    type: str
    required: true
    env:
      - name: ALIBABA_CLOUD_ACCESS_KEY_ID
  access_key_secret:
    description: Alibaba Cloud access key secret.
    type: str
    required: true
    secret: true
    env:
      - name: ALIBABA_CLOUD_ACCESS_KEY_SECRET
  region_id:
    description:
      - Region to query. If omitted, queries all available regions.
    type: str
  filters:
    description: Key-value filters to narrow instance results.
    type: dict
    default: {}
  compose:
    description: Template expressions for computed host variables.
    type: dict
    default: {}
  groups:
    description: Group definitions using Jinja2 conditionals.
    type: dict
    default: {}
  keyed_groups:
    description: Create groups from host variable values.
    type: list
    elements: dict
    default: []
"""

EXAMPLES = r"""
# alibaba_cloud_inventory.yml
plugin: stevefulme1.alibaba_cloud.alibaba_cloud_inventory
access_key_id: "{{ lookup('env', 'ALIBABA_CLOUD_ACCESS_KEY_ID') }}"
access_key_secret: "{{ lookup('env', 'ALIBABA_CLOUD_ACCESS_KEY_SECRET') }}"
region_id: cn-hangzhou
filters:
  Status: Running
keyed_groups:
  - key: instance_type
    prefix: type
  - key: region_id
    prefix: region
"""

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
)


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    """Alibaba Cloud ECS dynamic inventory plugin."""

    NAME = "stevefulme1.alibaba_cloud.alibaba_cloud_inventory"

    def verify_file(self, path):
        """Return True if the file is a valid inventory source."""
        valid = False
        if super().verify_file(path):
            if path.endswith(
                (
                    "alibaba_cloud.yml",
                    "alibaba_cloud.yaml",
                    "alibaba_cloud_inventory.yml",
                    "alibaba_cloud_inventory.yaml",
                )
            ):
                valid = True
        return valid

    def _get_regions(self, client):
        """Retrieve all available regions."""
        try:
            result = client.get(
                "DescribeRegions",
                {},
                service_endpoint="ecs.aliyuncs.com",
                api_version="2014-05-26",
            )
        except AlibabaCloudError as exc:
            raise AnsibleError("Failed to list regions: %s" % str(exc))

        data = result.get("Regions", {}).get("Region", [])
        return [r["RegionId"] for r in data]

    def _get_instances(self, client, region_id, filters):
        """Retrieve ECS instances for a region."""
        params = {"RegionId": region_id}
        if filters:
            params.update(filters)

        try:
            result = client.get(
                "DescribeInstances",
                params,
                service_endpoint="ecs.%s.aliyuncs.com" % region_id,
                api_version="2014-05-26",
            )
        except AlibabaCloudError as exc:
            raise AnsibleError("Failed to list instances in %s: %s" % (region_id, str(exc)))

        data = result.get("Instances", {}).get("Instance", [])
        if not isinstance(data, list):
            data = []
        return data

    def _populate(self, instances):
        """Populate inventory from instance list."""
        for inst in instances:
            instance_id = inst.get("InstanceId", "")
            if not instance_id:
                continue

            # Use private IP as hostname, fall back to instance ID.
            private_ip = ""
            vpc_attrs = inst.get("VpcAttributes", {})
            private_ips = vpc_attrs.get("PrivateIpAddress", {}).get("IpAddress", [])
            if private_ips:
                private_ip = private_ips[0]

            public_ips = inst.get("PublicIpAddress", {}).get("IpAddress", [])
            public_ip = public_ips[0] if public_ips else ""

            hostname = private_ip or public_ip or instance_id
            self.inventory.add_host(hostname)

            # Set host variables.
            hostvars = {
                "instance_id": instance_id,
                "instance_type": inst.get("InstanceType", ""),
                "region_id": inst.get("RegionId", ""),
                "vpc_id": vpc_attrs.get("VpcId", ""),
                "private_ip": private_ip,
                "public_ip": public_ip,
                "status": inst.get("Status", ""),
                "tags": inst.get("Tags", {}).get("Tag", []),
            }
            for key, val in hostvars.items():
                self.inventory.set_variable(hostname, key, val)

            # Built-in groups.
            region = inst.get("RegionId", "unknown")
            self.inventory.add_group("region_%s" % region.replace("-", "_"))
            self.inventory.add_host(hostname, "region_%s" % region.replace("-", "_"))

            itype = inst.get("InstanceType", "unknown")
            self.inventory.add_group("type_%s" % itype.replace(".", "_"))
            self.inventory.add_host(hostname, "type_%s" % itype.replace(".", "_"))

            status = inst.get("Status", "Unknown").lower()
            self.inventory.add_group("status_%s" % status)
            self.inventory.add_host(hostname, "status_%s" % status)

            vpc_id = vpc_attrs.get("VpcId", "")
            if vpc_id:
                self.inventory.add_group("vpc_%s" % vpc_id.replace("-", "_"))
                self.inventory.add_host(hostname, "vpc_%s" % vpc_id.replace("-", "_"))

            sg_ids = inst.get("SecurityGroupIds", {}).get("SecurityGroupId", [])
            for sg in sg_ids:
                self.inventory.add_group("sg_%s" % sg.replace("-", "_"))
                self.inventory.add_host(hostname, "sg_%s" % sg.replace("-", "_"))

            # Support constructed features.
            strict = self.get_option("strict")
            self._set_composite_vars(self.get_option("compose"), hostvars, hostname, strict=strict)
            self._add_host_to_composed_groups(self.get_option("groups"), hostvars, hostname, strict=strict)
            self._add_host_to_keyed_groups(
                self.get_option("keyed_groups"),
                hostvars,
                hostname,
                strict=strict,
            )

    def parse(self, inventory, loader, path, cache=True):
        """Parse the inventory source and populate inventory."""
        super().parse(inventory, loader, path, cache)
        self._read_config_data(path)

        access_key_id = self.get_option("access_key_id")
        access_key_secret = self.get_option("access_key_secret")
        region_id = self.get_option("region_id")
        filters = self.get_option("filters") or {}

        client = AlibabaCloudClient(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region_id=region_id or "cn-hangzhou",
        )

        if region_id:
            regions = [region_id]
        else:
            regions = self._get_regions(client)

        all_instances = []
        for reg in regions:
            instances = self._get_instances(client, reg, filters)
            all_instances.extend(instances)

        self._populate(all_instances)
