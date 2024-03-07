*Please :star: this repo if you find it useful*

# Average Sensor for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE.md)

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Support me on Patreon][patreon-shield]][patreon]

[![Community Forum][forum-shield]][forum]

_This sensor allows you to calculate the average state for one or more sensors over a specified period. Or just the average current state for one or more sensors, if you do not need historical data._

Initially it was written special for calculating of average temperature, but now it can calculate average of any numerical data.

![Example][exampleimg]

What makes this sensor different from others built into HA:

**Compare with the min-max sensor:**\
This sensor in the mean mode produces exactly the same average value from several sensors. But, unlike our sensor, it cannot receive the current temperature data from a weather, climate and water heater entities.

**Compare with statistics sensor:**\
This sensor copes with the averaging of data over a certain period of time. However… 1) it cannot work with several sources at once (and can't receive temperature from weather, climate and water heater entities, like min-max sensor), 2) when calculating the average, it does not take into account how much time the temperature value was kept, 3) it has a limit on the number of values ​​it averages - if by chance there are more values, they will be dropped.

> **_Note_**:\
> You can find a real example of using this component in [my Home Assistant configuration](https://github.com/Limych/HomeAssistantConfiguration).

I also suggest you [visit the support topic][forum] on the community forum.

## Breaking changes

* Since version 2.0.0 the mechanism for specifying the unique ID of sensors has been changed. To prevent duplicate sensors from being created, add option `unique_id: __legacy__` to the settings of already available sensors. For more information, see below.\
  Another way is to manually delete all old sensors via Configuration > Entities. Then restart HA and all the _2’s were was the original sensors again complete with their history.\
  [![My Entities](https://my.home-assistant.io/badges/entities.svg)](https://my.home-assistant.io/redirect/entities/)
* Since version 1.3.0 the default sensor name is “Average” instead of “Average Temperature”

## Known Limitations and Issues

* Due to the fact that HA does not store in history the temperature units of measurement for weather, climate and water heater entities, the average sensor always assumes that their values ​​are specified in the same units that are now configured in HA globally.

## Installation

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Search in HACS for "Average" integration or just press the button below:\
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)][hacs-repository]
1. Click Install below the found integration.

... then if you want to use `configuration.yaml` to configure sensor...
1. Add `average` sensor to your `configuration.yaml` file. See configuration examples below.
1. Restart Home Assistant

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `average`.
1. Download file `average.zip` from the [latest release section][releases-latest] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) you created.

... then if you want to use `configuration.yaml` to configure sensor...
1. Add `average` sensor to your `configuration.yaml` file. See configuration examples below.
1. Restart Home Assistant

### Configuration Examples

To measure the average of current values from multiple sources:
```yaml
# Example configuration.yaml entry
sensor:
  - platform: average
    name: 'Average Temperature'
    entities:
      - weather.gismeteo
      - sensor.owm_temperature
      - sensor.dark_sky_temperature
```

To measure the average of all values of a single source over a period:
```yaml
# Example configuration.yaml entry
sensor:
  - platform: average
    name: 'Average Temperature'
    duration:
      days: 1
    entities:
      - sensor.gismeteo_temperature
```

or you can combine this variants for some reason.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

### Configuration Variables

**entities**:\
  _(list) (Required)_\
  A list of temperature sensor entity IDs.

> **_Note_**:\
> You can use weather provider, climate and water heater entities as a data source. For that entities sensor use values of current temperature.

> **_Note_**:\
> You can use groups of entities as a data source. These groups will be automatically expanded to individual entities.

**unique_id**\
  _(string) (Optional)_\
  An ID that uniquely identifies this sensor. Set this to a unique value to allow customization through the UI.

> **_Note_**:\
> If you used the component version 1.4.0 or earlier, you can specify the special value `__legacy__`, so that no duplicates of already existing sensors are created.\
> The use of this special value in newly created sensors is not recommended.
>
> Another way is to manually delete all old sensors via Configuration > Entities. Then restart HA and all the _2’s were was the original sensors again complete with their history.\
  [![My Entities](https://my.home-assistant.io/badges/entities.svg)](https://my.home-assistant.io/redirect/entities/)


**name**:\
  _(string) (Optional)_\
  Name to use in the frontend.\
  _Default value: "Average"_

**start**:\
  _(template) (Optional)_\
  When to start the measure (timestamp or datetime).

**end**:\
  _(template) (Optional)_\
  When to stop the measure (timestamp or datetime).

**duration**:\
  _(time) (Optional)_\
  Duration of the measure.

**precision**:\
  _(number) (Optional)_\
  The number of decimals to use when rounding the sensor state.\
  _Default value: 2_

**process_undef_as**:\
  _(number) (Optional)_\
  Process undefined values (unavailable, sensor undefined, etc.) as specified value.\
  \
  By default, undefined values are not included in the average calculation. Specifying this parameter allows you to calculate the average value taking into account the time intervals of the undefined sensor values.

> **_Note_**:\
> This parameter does not affect the calculation of the count, min and max attributes.

### Average Sensor Attributes

**start**:\
  Timestamp of the beginning of the calculation period (if period was set).

**end**:\
  Timestamp of the end of the calculation period (if period was set).

**sources**:\
  Total expanded list of source sensors.

**count_sources**:\
  Total count of source sensors.

**available_sources**:\
  Count of available source sensors (for current calculation period).

**count**:\
  Total count of processed values of source sensors.

**min**:\
  Minimum value of processed values of source sensors.

**max**:\
  Maximum value of processed values of source sensors.

**trending_towards**:\
  The predicted value if monitored entities keep their current states for the remainder of the period. Requires "end" configuration variable to be set to actual end of period and not now().

## Time periods

The `average` integration will execute a measure within a precise time period. You should provide none, only `duration` (when period ends at now) or exactly 2 of the following:

- When the period starts (`start` variable)
- When the period ends (`end` variable)
- How long is the period (`duration` variable)

As `start` and `end` variables can be either datetimes or timestamps, you can configure almost any period you want.

### Duration

The duration variable is used when the time period is fixed.  Different syntaxes for the duration are supported, as shown below.

  ```yaml
  # 15 seconds
  duration: 15
  ```

  ```yaml
  # 6 hours
  duration: 06:00
  ```

  ```yaml
  # 1 minute, 30 seconds
  duration: 00:01:30
  ```

  ```yaml
  # 2 hours and 30 minutes
  duration:
    # supports seconds, minutes, hours, days
    hours: 2
    minutes: 30
  ```

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

### Examples

Here are some examples of periods you could work with, and what to write in your `configuration.yaml`:

**Last 5 minutes**: ends right now, last 5 minutes.

```yaml
duration:
  minutes: 5
```

**Today**: starts at 00:00 of the current day and ends right now.

```yaml
start: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
end: '{{ now() }}'
```

**Yesterday**: ends today at 00:00, lasts 24 hours.

```yaml
end: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
duration:
  hours: 24
```

**This morning (06:00–11:00)**: starts today at 6, lasts 5 hours.

```yaml
start: '{{ now().replace(hour=6).replace(minute=0).replace(second=0) }}'
duration:
  hours: 5
```

**Current week**: starts last Monday at 00:00, ends right now.

Here, last Monday is _today_ as a timestamp, minus 86400 times the current weekday (86400 is the number of seconds in one day, the weekday is 0 on Monday, 6 on Sunday).

```yaml
start: '{{ as_timestamp( now().replace(hour=0).replace(minute=0).replace(second=0) ) - now().weekday() * 86400 }}'
end: '{{ now() }}'
```

**Last 30 days**: ends today at 00:00, lasts 30 days. Easy one.

```yaml
end: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
duration:
  days: 30
```

**All your history** starts at timestamp = 0, and ends right now.

```yaml
start: '{{ 0 }}'
end: '{{ now() }}'
```

> **_Note_**:\
> The `Template Dev Tools` page of your home-assistant UI can help you check if the values for `start`, `end` or `duration` are correct. If you want to check if your period is right, just click on your component, the `start` and `end` attributes will show the start and end of the period, nicely formatted.\
> [![Developer Tools: Templates](https://my.home-assistant.io/badges/developer_template.svg)](https://my.home-assistant.io/redirect/developer_template/)

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.average: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors,
check [the contributor's page][contributors].

This Home Assistant custom component was created and is updated using the [HA-Blueprint template](https://github.com/Limych/ha-blueprint). You can use this template to maintain your own Home Assistant custom components.

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

***

[component]: https://github.com/Limych/ha-average
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-average.svg?style=popout
[commits]: https://github.com/Limych/ha-average/commits/dev
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=popout
[hacs]: https://hacs.xyz
[hacs-repository]: https://my.home-assistant.io/redirect/hacs_repository/?owner=Limych&repository=ha-average&category=integration
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
