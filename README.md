# Dovecot Quotas

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
![Install Stats][stats]

![Project Maintenance][maintenance-shield]
[![Community Forum][forum-shield]][forum]

This is a custom integration for retrieving Dovecot quota information.

## Prerequirements

You need a ssh login account which lets you execute the following command on a linux server:

- doveadm quota get -A

## Installation

Via HACS:

- Add the following custom repository as an integration:

    - MarcoGos/dovecot_quotas

- Restart Home Assistant

- Add the integration to Home Assistant

## Setup

Provide a hostname, username and password and select the account you want to follow.

## What to expect?

Each selected account will show up as a device.
The following entities will be created for every selected account (device):

- Quota:
    - Quota setup for account. Value will be Unknown if no quota is set.
- Free:
    - Total free space [^1]
- Free (%)
    - Percentage free space based on quota. [^2]
- Used:
    - Total used space
- Used (%): 
    - Percentage used based on quota

The entity information is updated every 60 minutes.

## Known problems

No problem known thus far.

[^1] Is calculated by Quota - Used
[^2] Is calculated by substracting 100% - Used (%)

[commits-shield]: https://img.shields.io/github/commit-activity/y/MarcoGos/dovecot_quotas.svg?style=for-the-badge
[commits]: https://github.com/MarcoGos/dovecot_quotas/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40MarcoGos-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/MarcoGos/dovecot_quotas.svg?style=for-the-badge
[releases]: https://github.com/MarcoGos/dovecot_quotas/releases
[stats]: https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.dovecot_quotas.total&style=for-the-badge
