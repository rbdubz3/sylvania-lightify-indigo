# Sylvania Lightify Plugin for Indigo

<img src="/assets/img/lightify-icon.png" width="150"/>&nbsp;&nbsp;&nbsp;<img src="/assets/img/indigo-icon.png" width="150"/>

This plugin is for use with the Sylvania Osram Lightify color changing bulbs. The plugin is an extension of the Indigo 'Dimmer'
device type, and hence supports all of the dimmer functionality available in Indigo. It leverages an open source python tcp library
for communicating with the Lightify Hub. The plugin has NOT been tested with any other hubs besides the Lightify Hub.

### Plugin Features
* RGBW Support - extends the Indigo Dimmer device type - supports dimmer actions on/off/brightness/white levels/rgb levels
* Device Types - supports 'Groups' ONLY (not individual bulbs)
* Zigbee Hub - uses an open source tcp library - tested with the Lightify Hub ONLY
* Scenes - supports creation of customized lighting scenes for the group of lights:
  * 'Circadian' automatically sets the group of lights based on time of day to match a 'circadian rhythm'
  * 'Match Colors' for all bulbs in the group to match
  * 'Rotate Colors' switches each bulb in a group to a different color.

### Sylvania Required Setup

In order to use the Indigo plugin, you must first setup the Sylvania Lightify system according to the manufacturer specs.
One caveat and I'll apologize up front. Lightify doesn't entirely seem to have their act together - I think the products
originated from a subsidiary and when you communicate with their tech support you get bounced around alot. Also their docs
are hit and miss. I found the following PDF - https://cache-m2.smarthome.com/manuals/46355-FAQ.pdf . Setup is pretty
easy with the mobile app, and there is alot of youtube videos.

So far the plugin is ONLY setup to work with a Lightify Group. You can create a group with a single light bulb as well.

### Plugin Config

<img src="/assets/img/plugin-config.png"/>

* IP address - REQUIRED - this is the IP address as configured in the hub
* Enable Debugging - set to 'ON' to get debug output.

### Device Config

<img src="/assets/img/group-device-config.png"/>

* Choose Lightify Group - select from the list of groups configured on the Lightify Hub
* Supports RGB - select if the devices in the group support RGB. This will also show the RGB color pickers
* Supports White Temp - select if the devices in the group support tunable white temperature.

### Scenes

The plugin supports creation of custom scenes - Circadian, Match Colors, and Rotate Colors.
NOTE: Sylvania Lightify app and hub also supports creation of scenes. The plugin scenes are completely separate
and don't integrate with the scenes from the Sylvania app.

##### Circadian

Automatically update color temperature and brightness based on circadian rythym (requires bulbs to support 'White Temperature').
Temperature values are in Kelvin and Brightness values are a percentage. The values form a gradient that increases from
sunrise to midday, and decreases at the end of day around sunset. The algorithm will adjust based on a percentage of each
interval. The values must be ordered such that: Late Night&lt;Pre-Sunrise&lt;Post-Sunrise&lt;AM Peak&lt;Max,
also Max&gt;Pre-Sunset&gt;Post-Sunset&gt;Late Night.

<img src="/assets/img/circadian-scene.png"/>

* Format: Late Night, Pre-Sunrise, Post-Sunrise, AM Peak, Max Temp, Pre-Sunset, Post-Sunset.
Examples below:
  * Color Temp(1500K-6500K): 1500,2300,4000,6400,6500,4500,2200</Label>
  * Brightness(1%-100%): 15,35,80,95,100,80,40</Label>


##### Match Colors

<img src="/assets/img/match-colors-scene.png"/>

##### Rotate Colors

<img src="/assets/img/rotate-colors-scene.png"/>


### Actions
{{:plugins:itunes_actions.png|


### Scripting Support
As with all plugins, actions defined by this plugin may be executed by Python scripts. Here's the information you need to script the actions in this plugin.

Plugin ID: com.woodsmachine.indigoplugins.SylvaniaLightify

### Action specific properties

### Support and Troubleshooting
For usage or troubleshooting tips discuss this device on our forum.