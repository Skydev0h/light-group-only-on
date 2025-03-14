# Light group only ON
Very simple light group for Home Assistant that only forwards modification commands to lights that are already ON.

> Note: Since this light group is built on top of the core light group, it also has that "bouncy" brightness slider [behavior](https://community.home-assistant.io/t/light-groups-bouncy-brightness-slider-behaviour/501539) depending on your setup. 

Strongly inspired and based on: https://github.com/oscarb/relative-brightness-light-group
and https://github.com/phipz/relative-brightness-light-group with all unnecessary "bouncy" and "relative" logic removed.

> N.B. Just like in phipz's variant, if all lights are off, then modification / turn on command is forwarded to all
> lights so that it would be possible to turn them on if all of these are off.

## Installation 

### HACS

To install using HACS, add a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) to HACS.

**Repository:**  `https://github.com/Skydev0h/light-group-only-on`

**Category:**  Integration

Once added, search for "Light group only ON" in HACS to find and download the component. 

### Manual

1. Download this repository
2. Copy over the `custom_components` folder into your Home Assistant `conifg` folder
3. Restart Home Assistant


## Configuration

Using this is as easy as using a normal [light group](https://www.home-assistant.io/integrations/group/). 

In your `configuration.yaml`, simply add: 

```yaml
light:
  - platform: light_group_only_on
    name: The Office
    entities:
      - light.office_desk
      - light.office_spotlights
```

You can also use the following options for additional functionality:

* `stay_off: true` option allows to prevent turning on the group if no lights are on. This can be
useful if you have a very large group (for example, encompassing all your lights in house) and you do not want to
accidentally turn on all the lights at once.
* `prevent_off: true` on the other hand prevents turning off lights in the group. Like in previous example, this can
be used to prevent accidentally turning off a very large group of lights.