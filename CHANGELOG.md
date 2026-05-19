# Changelog

## [2.2.2] - 2026-05-18

### Security
- Add `secret: true` to inventory plugin access_key_secret option

## [2.2.1] - 2026-05-18

### Security
- Fixed polardb_account password parameter no_log (was False, now True)
- Added no_log_values protection for RAM access key secret in return value
- Expanded .gitignore to exclude secrets, keys, credentials, and IDE files

## [2.0.0] - 2026-05-17

### Added
- Pagination support (limit/offset) for all _info modules
- 5 operational roles: ecs_provision, network_stack, oss_setup, ram_bootstrap, rds_deploy
- Dynamic inventory plugin
- Comprehensive unit and integration test suites
- Pre-commit and linting configuration (ruff, ansible-lint)

### Fixed
- Module references corrected (removed ali_ prefix)
- Meta versions, namespace, YAML formatting
- CI failures resolved across Python 3.11-3.13
- Galaxy import validation issues
- Role README files added for Galaxy compliance

### Changed
- Auto-formatted all modules with ruff
- Expanded ruff ignore list for compatibility

### Security
- Upgraded EDA signature from HMAC-SHA1 to HMAC-SHA256
- Added no_log to polardb_account password parameter

## [1.0.0] - 2026-05-15

### Added
- 297 modules covering full Alibaba Cloud platform API (ECS, VPC, SLB, RAM, KMS, RDS, PolarDB, ActionTrail, and more)
- CRUD + info module for every resource type
- Dynamic inventory plugin
- Unit tests and CI pipeline
