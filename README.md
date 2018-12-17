# Sylvania Lightify Plugin for Indigo

<img src="/assets/img/lightify-icon.png" width="150"/>&nbsp;&nbsp;&nbsp;<img src="/assets/img/indigo-icon.png" width="150"/>

This plugin is for use with the Sylvania Osram Lightify color changing bulbs. The plugin is an extension of the Indigo 'Dimmer'
device type, and hence supports all of the dimmer functionality available in Indigo. It leverages an open source python tcp library
for communicating with the Lightify Hub. The plugin has NOT been tested with any other hubs besides the Lightify Hub.

### Plugin Features
* RGBW Support - extends the Indigo Dimmer device type - supports dimmer actions on/off/brightness/white levels/rgb levels
* Device Types - supports 'Groups' ONLY (not individual bulbs)
* Zigbee Hub - uses an open source tcp library - tested with the Lightify Hub ONLY
* Scenes - supports creation of customized scenes for the group of lights.
** 'Circadian' automatically sets the group of lights based on time of day to match a 'circadian rhythm'
** 'Match Colors' for all bulbs in the group to match
** 'Rotate Colors' switches each bulb in a group to a different color.

### Plugin Config


### Device States

### Actions
{{:plugins:itunes_actions.png|


### Scripting Support
As with all plugins, actions defined by this plugin may be executed by Python scripts. Here's the information you need to script the actions in this plugin.

Plugin ID: com.woodsmachine.indigoplugins.SylvaniaLightify

### Action specific properties

### Support and Troubleshooting
For usage or troubleshooting tips discuss this device on our forum.