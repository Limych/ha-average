*Please :star: this repo if you find it useful*

# Average Sensor for Home Assistant

[![GitHub Release](https://img.shields.io/github/tag-date/Limych/ha-average?label=release&style=popout)](https://github.com/Limych/ha-average/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Limych/ha-average.svg?style=popout)](https://github.com/Limych/ha-average/commits/master)
[![License](https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout)](LICENSE.md)
![Requires.io](https://img.shields.io/requires/github/Limych/ha-average)

[![hacs](https://img.shields.io/badge/HACS-Default-orange.svg?style=popout)][hacs]
![Project Maintenance](https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout)

[![GitHub pull requests](https://img.shields.io/github/issues-pr/Limych/ha-average?style=popout)](https://github.com/Limych/ha-average/pulls)
[![Bugs](https://img.shields.io/github/issues/Limych/ha-average/bug.svg?colorB=red&label=bugs&style=popout)](https://github.com/Limych/ha-average/issues?q=is%3Aopen+is%3Aissue+label%3ABug)

[![Community Forum](https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout)][forum-support]

This sensor allows you to calculate the average state for one or more sensors over a specified period. Or just the average current state for one or more sensors, if you do not need historical data.

Initially it was written special for calculating of average temperature, but now it can calculate average of any numerical data.

![Example](example.png)

What makes this sensor different from others built into HA:

**Compare with the min-max sensor:**\
This sensor in the mean mode produces exactly the same average value from several sensors. But, unlike our sensor, it cannot receive the current temperature data from a weather, climate and water heater entities.

**Compare with statistics sensor:**\
This sensor copes with the averaging of data over a certain period of time. However… 1) it cannot work with several sources at once (and can't receive temperature from weather, climate and water heater entities, like min-max sensor), 2) when calculating the average, it does not take into account how much time the temperature value was kept, 3) it has a limit on the number of values ​​it averages - if by chance there are more values, they will be dropped.

> **_Note_**:\
> You can find a real example of using this component in [my Home Assistant configuration](https://github.com/Limych/HomeAssistantConfiguration).

I also suggest you [visit the support topic][forum-support] on the community forum.

## Breaking changes

* Since version 1.3.0 the default sensor name is “Average” instead of “Average Temperature”

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `average`.
1. Download _all_ the files from the `custom_components/average/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. Add `average` sensor to your `configuration.yaml` file:

    To measure the average current temperature from multiple sources:
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

    To measure average temperature for some period:
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
<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=UAGFL5L6M8RN2&item_name=[average]+Donation+for+a+big+barrel+of+coffee+:)&currency_code=EUR&source=url" target="_blank"><img src="http://khrolenok.ru/support_paypal.png" alt="PayPal" width="250" height="48"></a>
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
> The `/dev-template` page of your home-assistant UI can help you check if the values for `start`, `end` or `duration` are correct. If you want to check if your period is right, just click on your component, the `start` and `end` attributes will show the start and end of the period, nicely formatted.

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok][limych].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

[forum-support]: https://community.home-assistant.io/t/average-sensor/111674
[hacs]: https://github.com/custom-components/hacs
