# Sylvania Lightify Plugin for Indigo

<img src="/assets/img/lightify-icon.png" width="150"/>&nbsp;&nbsp;&nbsp;<img src="/assets/img/indigo-icon.png" width="150"/>

This plugin is for use with the [Sylvania Osram Lightify][2] color changing bulbs. The plugin is an extension of the Indigo 'Dimmer'
device type, and hence supports all of the dimmer functionality available in Indigo. It leverages an open source python library,
which communicates with the [Lightify Hub][1] via LAN TCP port 4000 using a binary protocol.
The plugin has NOT been tested with any other gateways besides the [Lightify Hub][1].

### Plugin Features
* RGBW Support - extends the Indigo Dimmer device type - supports dimmer actions on/off/brightness/white levels/rgb levels
* Device Types - supports 'Groups' ONLY (not individual bulbs)
* Zigbee Hub - uses an open source tcp library - tested with the Lightify Hub ONLY
* Scenes - supports creation of customized lighting scenes for the group of lights:
  * 'Circadian' - automatically sets the group of lights based on time of day to match a 'circadian rhythm'
  * 'Match Color/Temp' - all bulbs in a group will match the color/temp. Rotates the entire group through each of the different colors specified in the scene
  * 'Rotate Color/Temp' - each bulb in a group can be a different color. Rotates each bulb through all the different colors specified in the scene

It is **strongly recommended** to read the [Wiki Documentation][3] to familiarise yourself with the new way of working which is substantially different to earlier plugin versions (V1, V2 and V3).

**The latest production release is available here: [Plugin Releases][4]**

### README - Supported Bulbs and Device Types

##### Indigo Device Types
As stated above, the plugin has ONLY been setup to work with Lightify Groups. Groups are setup via the Lightify mobile app.
Support for a single bulb Device Type is TBD. You can still use the plugin with a single bulb however, you just need to
setup a Lightify Group comprised of the single bulb. Apologies for this seeming lack of functionality - however, I built the
plugin for use in my house where I'd always done several bulbs combined into a group.

##### Supported Lightify Bulbs
Several different Lightify Zigbee bulbs have been used and work great.
However, the plugin currently doesn't validate or check different Lightify bulbs to see if they are supported.

To date, the bulb types listed below have without issue. Product info can be found on the [Sylvania Osram Lightify][2] site:
  * Color RGBW - A19 / BR30 / Indoor Flex Strip / RT 5|6 Recessed Can
  * Tunable/Adjustable White - MR16 / Under Cabinet Light 18"

The Color RGBW bulbs are more expensive, but highly recommended over the tunable/adjustable white ones. The main
product deficiency with the tunable/adjustable white bulbs is they have a minimum color temp of 2700K. For the 'Circadian'
scene functionality, it is desirable to go down much lower - closer to 1500K for a nice warm yellow/orange glow.

[1]: https://consumer.sylvania.com/our-products/smart/getting-started/
[2]: https://consumer.sylvania.com/our-products/smart/sylvania-smart-zigbee-products-menu/index.jsp
[3]: https://github.com/rbdubz3/sylvania-lightify-indigo/wiki
[4]: https://github.com/rbdubz3/sylvania-lightify-indigo/releases