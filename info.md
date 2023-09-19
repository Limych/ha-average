{% if prerelease %}
### NB!: This is a Beta version!
{% endif %}
{% if (version_installed.split(".")[0:2] | join | int) < 20 %}
### ATTENTION! Breaking changes!

The mechanism for specifying the unique ID of sensors has been changed. To prevent duplicate sensors from being created, add option `unique_id: __legacy__` to the settings of already available sensors. For more information, see the component's documentation.

Another way is to manually delete all old sensors via Configuration > Entities. Then restart HA and all the _2’s were was the original sensors again complete with their history.\
[![My Entities](https://my.home-assistant.io/badges/entities.svg)](https://my.home-assistant.io/redirect/entities/)
{% endif %}

_This sensor allows you to calculate the average state for one or more sensors over a specified period. Or just the average current state for one or more sensors, if you do not need historical data._

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Support me on Patreon][patreon-shield]][patreon]

[![Community Forum][forum-shield]][forum]

![example][exampleimg]

## Known Limitations and Issues

- Due to the fact that HA does not store in history the temperature units of measurement for weather, climate and water heater entities, the average sensor always assumes that their values ​​are specified in the same units that are now configured in HA globally.

{% if not installed %}
## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Average".

{% endif %}
## Configuration is done in the UI

<!---->

## Useful Links

- [Documentation][component]
- [Report a Bug][report_bug]
- [Suggest an idea][suggest_idea]

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/address/BTC/16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

***

[component]: https://github.com/Limych/ha-average
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-average.svg?style=popout
[commits]: https://github.com/Limych/ha-average/commits/master
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=popout
[hacs]: https://hacs.xyz
[exampleimg]: https://github.com/Limych/ha-average/raw/dev/example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/average-sensor/111674
[license]: https://github.com/Limych/ha-average/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-average.svg?style=popout
[releases]: https://github.com/Limych/ha-average/releases
[releases-latest]: https://github.com/Limych/ha-average/releases/latest
[user_profile]: https://github.com/Limych
[report_bug]: https://github.com/Limych/ha-average/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/Limych/ha-average/issues/new?template=feature_request.md
[contributors]: https://github.com/Limych/ha-average/graphs/contributors
[patreon-shield]: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DLimych%26type%3Dpatrons&style=popout
[patreon]: https://www.patreon.com/join/limych
