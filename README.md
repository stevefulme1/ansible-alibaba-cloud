# stevefulme1.alibaba_cloud

Ansible collection for managing Alibaba Cloud resources. Full-scope coverage of ECS, VPC, SLB, RAM, KMS, RDS, PolarDB, ActionTrail, and more.

## Overview

This collection provides **297 modules** for automating Alibaba Cloud infrastructure, along with 5 operational roles, a dynamic inventory plugin, and CI/CD workflows.

## Requirements

- ansible-core >= 2.16
- Python >= 3.11

## Installation

```bash
ansible-galaxy collection install stevefulme1.alibaba_cloud
```

Or from source:

```bash
ansible-galaxy collection build
ansible-galaxy collection install stevefulme1-alibaba_cloud-2.0.0.tar.gz
```

## Included Content

### Modules (297)

This collection includes CRUD and info modules for the following Alibaba Cloud services:

- **ECS** — instances, security groups, disks, images, snapshots, key pairs
- **VPC** — VPCs, vSwitches, route tables, NAT gateways, EIPs
- **SLB** — load balancers, listeners, server groups, health checks
- **RAM** — users, groups, roles, policies, access keys
- **KMS** — keys, aliases, secrets
- **RDS** — instances, databases, accounts, backups
- **PolarDB** — clusters, databases, accounts, endpoints
- **OSS** — buckets, lifecycle rules
- **ActionTrail** — trails, event logging
- **DNS** — domains, records
- **CDN** — domains, cache rules
- And many more

### Roles (5)

| Role | Description |
|------|-------------|
| `ecs_provision` | Provision ECS instances with networking |
| `network_stack` | Set up VPC, vSwitch, security groups |
| `oss_setup` | Configure OSS buckets and policies |
| `ram_bootstrap` | Bootstrap RAM users, roles, and policies |
| `rds_deploy` | Deploy and configure RDS instances |

### Inventory Plugin

- `alibaba_cloud_inventory` — Dynamic inventory from Alibaba Cloud API

## Usage

```yaml
- name: Create an ECS instance
  stevefulme1.alibaba_cloud.ecs_instance:
    access_key: "{{ ali_access_key }}"
    secret_key: "{{ ali_secret_key }}"
    region: cn-hangzhou
    instance_name: my-instance
    image_id: ubuntu_22_04_x64
    instance_type: ecs.t6-c1m1.large
    state: present
```

## License

GPL-3.0-or-later
