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

<img src="/assets/img/plugin-config.png" width="500"/>

* IP address - REQUIRED - this is the IP address as configured in the hub
* Enable Debugging - set to 'ON' to get debug output.

### Device Config

<img src="/assets/img/group-device-config.png" width="500"/>

* Choose Lightify Group - select from the list of groups configured on the Lightify Hub
* Supports RGB - select if the devices in the group support RGB. This will also show the RGB color pickers
* Supports White Temp - select if the devices in the group support tunable white temperature.

### Scenes

The plugin supports creation of custom scenes - Circadian, Match Colors, and Rotate Colors.
NOTE: Sylvania Lightify app and hub also supports creation of scenes. The plugin scenes are completely separate
and don't integrate with the scenes from the Sylvania app.

<img src="/assets/img/scene-config.png" width="500"/>

* Scene - select from the list of existing scenes
* Scene Name - update the name of the Scene
* Scene Type - choose between 'Circadian', 'Rotate Color/Temp', or 'Match Color/Temp'
* Scene Interval - Time in seconds between color/temp changes. For circadian, a higher value is
recommeded (i.e. 10min=600secs)

#### Circadian

Automatically update color temperature and brightness based on circadian rythym - requires bulbs to support 'White Temperature'.
Temperature values are in Kelvin and Brightness values are a percentage.

This one is really very cool IMO :). I have several Lightify groups in my house and the Circadian scene provides perfect lighting.
Late night and early morning the lights are dim and yellow/orange-ish. They ramp-up in the morning to be bright and more white/blu-ish.
Hence if you are concerned about too much blue light at night before bed, this scene has you covered.

<img src="/assets/img/circadian-scene.png" width="600"/>

The values form a gradient that increases from
sunrise to midday, and decreases at the end of day around sunset. The algorithm will adjust based on a percentage of each
interval. The values must be ordered such that: Late Night&lt;Pre-Sunrise&lt;Post-Sunrise&lt;AM Peak&lt;Max,
also Max&gt;Pre-Sunset&gt;Post-Sunset&gt;Late Night.

* Format: Late Night, Pre-Sunrise, Post-Sunrise, AM Peak, Max Temp, Pre-Sunset, Post-Sunset.
Examples below:
  * Color Temp(1500K-6500K): 1500,2300,4000,6400,6500,4500,2200</Label>
  * Brightness(1%-100%): 15,35,80,95,100,80,40</Label>


#### Match Color/Temp

Match - Bulbs in the group always match color/temp. The scene allows you to specify a number of different color/temp
settings - including rgb/temp/brightness and transition time in millis.

<img src="/assets/img/match-colors-scene.png" width="600"/>

For each setting below, choose between either RGB or White Temperature. If ColorTemp is provided, the RGB values
will be ignored. RGB values are 0-255, ColorTemp in Kelvin is 1500-6500, Brightness % 0-100,
Transition in milliseconds (1 sec = 1000 millis). If a setting isn't used, just leave empty.

* Format: Values should be formatted as follows: R, G, B, Temp, Brightness, Transition time.
Examples below:
  * RGB: 175,125,29,0,50,1000
  * Color Temp: 255,255,255,3000,75,1000

#### Rotate Color/Temp

Rotate Color/Temp - Bulbs in the group independently rotate through all color/temp settings.

Settings are identical to the 'Match Color/Temp' scene. However, the plugin will set each bulb to a different
color/temp setting and will rotate sequentially.

### Plugin Actions

#### Dimmer Type actions
The plugin extends Indigo 'dimmer type', and as a result can utilize the dimmer device type actions. The plugin
supports the following:
* On/Off
* SetBrightness
* Set RGB
* Set Color Temp

NOTE: Some of the dimmer type actions have yet to be implemented - brighten by/dim by

#### Scene Actions

The plugin provides actions to start and stop a scene.

<img src="/assets/img/start-scene.png" width="500"/>

* For 'Start Scene', simply choose the desired scene for your device.
* When a group is turned off, the scene will automatically be turned off.

### Scripting Support
As with all plugins, actions defined by this plugin may be executed by Python scripts. Here's the information you need to script the actions in this plugin.

Plugin ID: com.woodsmachine.indigoplugins.SylvaniaLightify

### Support and Troubleshooting
For usage or troubleshooting tips discuss this device on our forum.

### Known Issues

---
#### KeyError: (9518399593889895564L,)
> A couple of the recent bulbs I've tried generate errors for some of the actions. I believe it is a precision error that I've yet to debug<br/>Sylvania Lightify Error<br/>Error in plugin execution ExecuteAction:<br/><br/>Traceback (most recent call last):<br/>File "plugin.py", line 894, in startScene<br/>KeyError: (9518399593889895564L,)
