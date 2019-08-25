*Please :star: this repo if you find it useful*

# Average Temperature Sensor for Home Assistant

This sensor allows you to calculate the average temperature for one or more sensors over a specified period. Or just the average current temperature for one or more sensors, if you do not need historical data.

![Example](example.png)

What makes this sensor different from others built into HA:

Compare with the min-max sensor.\
This sensor in the mean mode produces exactly the same average value from several sensors. But, unlike our sensor, it cannot receive the current temperature data from a weather, climate and water heater entities.

Compare with statistics sensor.\
This sensor copes with the averaging of data over a certain period of time. However… 1) it cannot work with several sources at once (and can't receive temperature from weather, climate and water heater entities, like min-max sensor), 2) when calculating the average, it does not take into account how much time the temperature value was kept, 3) it has a limit on the number of values ​​it averages - if by chance there are more values, they will be dropped.

*NB. You can find a real example of using this component in [my Home Assistant configuration](https://github.com/Limych/HomeAssistantConfiguration).*

I also suggest you [visit the support topic](https://community.home-assistant.io/t/average-temperature-sensor/111674) on the community forum.

## Component setup instructions

1. Create a directory `custom_components` in your Home Assistant configuration directory.

1. Create a directory `average` in `custom_components` directory.

1. Copy [average directory](https://github.com/Limych/ha-average/tree/master/custom_components/average) from this project including **all** files and sub-directories into the directory `custom_components`.

    It should look similar to this after installation:
    ```
    <config_dir>/
    |-- custom_components/
    |   |-- average/
    |       |-- __init__.py
    |       |-- sensor.py
    |       |-- etc...
    ```

1. Add `average` sensor to your `configuration.yaml` file:

    To measure the average current temperature from multiple sources:
    ```yaml
    # Example configuration.yaml entry
    sensor:
      - platform: average
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
        duration:
          days: 1
        entities:
          - sensor.gismeteo_temperature
    ```
    
    or you can combine this variants for some reason.

<p align="center">* * *</p>
I put a lot of work into making this repo available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=UAGFL5L6M8RN2&item_name=[average]+Donation+for+a+big+barrel+of+coffee+:)&currency_code=EUR&source=url"><img alt="Buy Me a Coffe" src="https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/donate-with-paypal.png"></a></p>
<p align="center"><a href="https://www.patreon.com/join/limych?"><img alt="Support my work on Patreon" src="https://raw.githubusercontent.com/Limych/HomeAssistantConfiguration/master/docs/images/support-with-patreon.jpg"></a></p>

### Configuration Variables
  
**entities:**\
  *(list)* *(Required)* A list of temperature sensor entity IDs.
  
  *NB* You can use weather provider, climate and water heater entities as a data source. For that entities sensor use values of current temperature.

**name:**\
  *(string)* *(Optional)* Name to use in the frontend.\
  *Default value: Average Temperature*
  
**duration:**\
  *(time)* *(Optional)* Duration of the measure from the current time.
  
  Different syntaxes for the duration are supported, as shown below.

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

## Track updates

You can automatically track new versions of this component and update it by [custom-updater](https://github.com/custom-components/custom_updater).

To initiate tracking add this lines to you `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
custom_updater:
  track:
    - components
  component_urls:
    - https://raw.githubusercontent.com/Limych/ha-average/master/tracker.json
```
