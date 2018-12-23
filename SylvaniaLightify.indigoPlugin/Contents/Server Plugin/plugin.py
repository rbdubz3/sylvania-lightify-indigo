#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2016, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com
#

################################################################################
# Imports
################################################################################
import indigo
import urllib2
from xml.dom.minidom import parseString
import lightifydirect
import time
import datetime
import threading
import Queue
import sys
import enum

################################################################################
# Globals
################################################################################

########################################
def updateVar(name, value, folder=0):
    if name not in indigo.variables:
        indigo.variable.create(name, value=value, folder=folder)
    else:
        indigo.variable.updateValue(name, value)


################################################################################
class Plugin(indigo.PluginBase):
    ########################################
    # Class properties
    ########################################

    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get("showDebugInfo", False)
        self.lightifyHubIpAddr = pluginPrefs.get("lightifyHubIpAddr", "172.16.42.100")
        self.lightifyConn = ""
        self.deviceList = []
        self.deviceThreads = []
        self.lightifyLock = threading.Lock()
        self.lightifyQueue = Queue.Queue(100)
        self.lastRefreshTime = datetime.datetime.now()

    ########################################
    def deviceStartComm(self, device):
        indigo.server.log("Starting device: " + device.name + ", lightifyHubIpAddr=" + self.lightifyHubIpAddr)
        if device.id not in self.deviceList and device.deviceTypeId == 'lightifyGroupType':
            props = device.pluginProps
            # Set SupportsColor property so Indigo knows device accepts color actions and should use color UI.
            if props["SupportsRGB"] == True:
                # this is a color bulb
                props["SupportsColor"] = True
            else:
                # this is a tunable white bulb
                props["SupportsColor"] = True
                props["SupportsWhiteTemperature"] = True

            self.debugLog("Updating device id1: " + str(device.id) + ", name: " + device.name)
            device.replacePluginPropsOnServer(props)
            device.updateStateImageOnServer(indigo.kStateImageSel.Auto)

            try:
                self.update(device)
                self.deviceList.append(device.id)
            except Exception as ex:
                self.errorLog("Exception hit in deviceStartComm - " + str(ex))



    ########################################
    def deviceStopComm(self, device):
        for gThread in self.deviceThreads:
            if gThread.indigoDevice.name == device.name:
                gThread.stopDevConcurrentThread()
                self.deviceThreads.remove(gThread)
                indigo.server.log("Stopping device thread: " + device.name)

        if device.id in self.deviceList:
            self.deviceList.remove(device.id)
            indigo.server.log("Stopping device: " + device.name)


    # Startup
    ########################################
    def startup(self):
        indigo.server.log(u"Startup called.")
        indigo.server.log(u"Initializing Lightify Hub, IP Address=" + self.lightifyHubIpAddr)
        try:
            self.lightifyConn = lightifydirect.Lightify(self.lightifyHubIpAddr)
            self.lightifyConn.update_all_light_status()
            self.lightifyConn.update_group_list()
        except Exception as ex:
            self.errorLog("Error initializing Lightify Hub - " + str(ex))
            self.errorLog("Check IP address in Plugin Configuration.")

        # Perform an initial version check.
        self.debugLog(u"Running plugin version check (if enabled).")
        #self.updater.checkVersionPoll()

        # Prior to version 1.0.0, the "scenes" property did not exist in the plugin preferences.
        #   If that property does not exist, add it.
        # As of version 1.0.0, there are now 30 scenes instead of 10.
        if not self.pluginPrefs.get('scenes', False):
            indigo.server.log(u"pluginPrefs lacks scenes.  Adding.")
            # Add the empty scenes list to the prefs.
            self.pluginPrefs['scenes'] = list()
            # Start a new list of empty scenes.
            scenes = list()
            for aNumber in range(1,21):
                # Create a blank sub-list for storing scene name and scene states.
                scene = list()
                # Add the sub-list to the empty scenes list.
                scenes.append(scene)

                if aNumber == 1:
                    self.debugLog(u"pluginPrefs lacks scenes.  Adding Christmas.")
                    # Add the scene name.
                    scene.append('Christmas')
                    scene.append('rotate-colors')
                    scene.append('45')
                    sceneData = list()
                    sceneData.append('0,0,255,0,90,50')
                    sceneData.append('255,125,0,0,90,50')
                    sceneData.append('0,255,0,0,90,50')
                    sceneData.append('255,00,0,0,90,50')
                    sceneData.append('255,255,0,0,90,50')
                    scene.append(sceneData)
                    circadianData = list()
                    circadianData.append('1650,2400,3800,6400,6500,4500,2200')
                    circadianData.append('10,35,90,95,100,80,40')
                    scene.append(circadianData)
                elif aNumber == 2:
                    self.debugLog(u"pluginPrefs lacks scenes.  Adding Halloween.")
                    # Add the scene name.
                    scene.append('Halloween')
                    scene.append('match-colors')
                    scene.append('30')
                    sceneData = list()
                    sceneData.append('40,0,80,0,65,100')
                    sceneData.append('40,0,80,0,40,1000')
                    sceneData.append('100,20,0,0,40,100')
                    sceneData.append('100,20,0,0,65,1000')
                    scene.append(sceneData)
                    circadianData = list()
                    circadianData.append('1650,2400,3800,6400,6500,4500,2200')
                    circadianData.append('10,35,90,95,100,80,40')
                    scene.append(circadianData)
                elif aNumber == 3:
                    self.debugLog(u"pluginPrefs lacks scenes.  Adding St. Patricks.")
                    scene.append('St. Patricks')
                    scene.append('match-colors')
                    scene.append('60')
                    sceneData = list()
                    sceneData.append('13,89,1,0,90,500')
                    sceneData.append('0,255,0,0,10,500')
                    sceneData.append('0,179,22,0,80,500')
                    sceneData.append('13,239,33,0,25,500')
                    scene.append(sceneData)
                    circadianData = list()
                    circadianData.append('1650,2400,3800,6400,6500,4500,2200')
                    circadianData.append('10,35,90,95,100,80,40')
                    scene.append(circadianData)
                elif aNumber == 4:
                    self.debugLog(u"pluginPrefs lacks scenes.  Adding IndoorCirc.")
                    scene.append('IndoorCirc')
                    scene.append('circadian')
                    scene.append('600')
                    sceneData = list()
                    sceneData.append('13,89,1,0,90,500')
                    sceneData.append('0,255,0,0,10,500')
                    scene.append(sceneData)
                    circadianData = list()
                    circadianData.append('1650,2400,3800,6400,6500,4500,2200')
                    circadianData.append('10,35,90,95,100,80,40')
                    scene.append(circadianData)
                elif aNumber == 5:
                    self.debugLog(u"pluginPrefs lacks scenes.  Adding OutdoorCirc.")
                    scene.append('OutdoorCirc')
                    scene.append('circadian')
                    scene.append('600')
                    sceneData = list()
                    sceneData.append('13,89,1,0,90,500')
                    sceneData.append('0,255,0,0,10,500')
                    scene.append(sceneData)
                    circadianData = list()
                    circadianData.append('1850,2600,5500,6400,6500,4000,2400')
                    circadianData.append('20,55,80,95,100,85,60')
                    scene.append(circadianData)
                elif aNumber == 6:
                    self.debugLog(u"pluginPrefs lacks scenes.  Adding MBR Circ.")
                    scene.append('MBR Circ')
                    scene.append('circadian')
                    scene.append('600')
                    sceneData = list()
                    sceneData.append('13,89,1,0,90,500')
                    sceneData.append('0,255,0,0,10,500')
                    scene.append(sceneData)
                    circadianData = list()
                    circadianData.append('1500,2200,5500,6400,6500,4500,2200')
                    circadianData.append('10,35,90,98,100,80,35')
                    scene.append(circadianData)
                else:
                    # Add the scene name.
                    scene.append('Scene ' + unicode(aNumber))
                    scene.append('match-colors')
                    scene.append('60')

            # Add the new list of empty scenes to the prefs.
            self.pluginPrefs['scenes'] = scenes
            self.debugLog(u"pluginPrefs now contains 20 scenes.")
        # If scenes exist, make sure there are 30 of them.



    ########################################
    def runConcurrentThread(self):
        indigo.server.log("Starting concurrent tread")
        try:
            while True:
                # we sleep (30 minutes) first because when the plugin starts, each device
                # is updated as they are started.
                currentTime = datetime.datetime.now()
                # find the number of minutes since Some Date
                timeDelta = currentTime - self.lastRefreshTime
                diffMinutes = int(timeDelta.days * 1440 + timeDelta.seconds/60)
                if diffMinutes > 30:
                    try:
                        have_it = self.lightifyLock.acquire(0)
                        if have_it is True:
                            self.debugLog('...Refreshing Lightify Device Status')
                            self.lightifyConn.update_all_light_status()
                            self.lightifyConn.update_group_list()
                            for (addr, light) in self.lightifyConn.lights().iteritems():
                                self.debugLog('...light details=' + str(light) + ', on=' + str(light.on()))

                            # now we cycle through each hub/group
                            for deviceId in self.deviceList:
                                # call the update method with the device instance
                                theDevice = indigo.devices[deviceId]
                                self.update(theDevice)
                                self.debugLog("...Updating Lightify Group: Name=" + str(theDevice.name) + ", " + str(theDevice.states))
                                theGroup = self.getLightifyGroup(theDevice)
                                grpOnOffState = theDevice.states['onOffState']
                                for curLight in theGroup.lights():
                                    theLight = self.lightifyConn.lights()[curLight]
                                    if theLight is not None:
                                        self.debugLog('...groupLight =' + str(theLight) + ', on=' + str(theLight.on()))
                                        if grpOnOffState is False and theLight.on() is 1 and 'Media' not in theDevice.name:
                                            theLight.set_onoff(0)
                                            self.lightifyConn.update_light_status(theLight)
                                            newLight = self.lightifyConn.light_byname(theLight.name())
                                            self.debugLog('...ATTEMPTED to turnoff light. Updated status =' + str(newLight) + ', on=' + str(newLight.on()))
                            self.lastRefreshTime = datetime.datetime.now()

                            # lets also output all of the threads in action
                            sceneThreadCount = 0
                            for curSceneThread in self.deviceThreads:
                                sceneThreadCount = sceneThreadCount + 1
                                self.debugLog("...Running scene thread - groupName=" + curSceneThread.indigoDevice.name +
                                                  ",thread=" +str(curSceneThread))
                            self.debugLog("...Total scene threads - " + str(sceneThreadCount))

                    finally:
                        if have_it is True:
                            self.debugLog('...runConcurrentThread RELEASING lightifyLock after refreshing Device Status')
                            self.lightifyLock.release()

                # TODO should sleep the minimum of all sleeps for the scenes
                self.sleep(10)

                try:
                    while self.lightifyQueue.empty() == False:
                        workItem = self.lightifyQueue.get_nowait()
                        self.debugLog('...runConcurrentThread WORK ITEM=???')
                        num_tries = 0
                        have_it = False
                        while num_tries < 10 and have_it is False:
                            if num_tries != 0:
                                self.sleep(0.5)
                            self.debugLog('...runConcurrentThread TRYING for lightifyLock')
                            have_it = self.lightifyLock.acquire(0)
                            try:
                                num_tries += 1
                                if have_it:
                                    self.debugLog('...runConcurrentThread lightifyLock ACQUIRED, num_tries=' + str(num_tries))
                                    # simulate a delay as we'd expect from the bulbs
                                    self.debugLog('...runConcurrentThread PROCESSING workItem=[groupName:' + workItem.groupName
                                                  + ',sceneName:' + str(workItem.sceneName)
                                                  + ',isGroup:' + str(workItem.isGroupWork) + ',workItemType:' + str(workItem.workItemType)
                                                  + ',colorTemp:' + str(workItem.colorTemp) + ',brightness=' + str(workItem.brightness)
                                                  + ',rgbValues:' + str(workItem.rgbValues)
                                                  + ']')
                                    ## self.sleep(1)
                                    #...actionControlDevice action=actionValue : ActionProps : (dict)
                                    #    blueLevel : 255 (real)
                                    #    greenLevel : 255 (real)
                                    #    redLevel : 255 (real)
                                    #    whiteLevel : 0 (real)
                                    #    whiteLevel2 : 0 (real)
                                    #    whiteTemperature : 6267 (integer)
                                    #    configured : True
                                    #    delayAmount : 900
                                    #    description : set color levels device to 255 255 255, 0 0 6267 K
                                    #    deviceAction : SetColorLevels
                                    #    deviceId : 31022405
                                    #    replaceExisting : True
                                    #    textToSpeak :
                                    # find a matching thread in the list
                                    sceneThreadActive = False
                                    for gThread in self.deviceThreads:
                                        if gThread.indigoDevice.name == workItem.indigoDevice.name:
                                            sceneThreadActive = True
                                    if sceneThreadActive is True:
                                        if workItem.isGroupWork is False:
                                            lightObject = workItem.theLight
                                            if workItem.workItemType is WorkItemType.RGB:
                                                lightObject.set_rgb(workItem.rgbValues[0], workItem.rgbValues[1],
                                                                    workItem.rgbValues[2], workItem.transitionMillis)
                                            elif workItem.workItemType is WorkItemType.CTEMP:
                                                lightObject.set_temperature(workItem.colorTemp, workItem.transitionMillis)
                                            elif workItem.workItemType is WorkItemType.BRIGHTNESS:
                                                lightObject.set_luminance(workItem.brightness, workItem.transitionMillis)
                                        else:
                                            action = LightifyAction()
                                            action.deviceId = workItem.indigoDevice.id
                                            if workItem.workItemType is WorkItemType.RGB:
                                                action.deviceAction = indigo.kDeviceAction.SetColorLevels
                                                action.actionValue = { "redLevel": workItem.rgbValues[0],
                                                                       "greenLevel": workItem.rgbValues[1],
                                                                       "blueLevel": workItem.rgbValues[2],
                                                                       "whiteLevel": 0,
                                                                       "whiteLevel2": 0,
                                                                       "whiteTemperature": 0}
                                            elif workItem.workItemType is WorkItemType.CTEMP:
                                                action.deviceAction = indigo.kDeviceAction.SetColorLevels
                                                action.actionValue = { "redLevel": 255,
                                                                       "greenLevel": 255,
                                                                       "blueLevel": 255,
                                                                       "whiteLevel": 0,
                                                                       "whiteLevel2": 0,
                                                                       "whiteTemperature": workItem.colorTemp}
                                            elif workItem.workItemType is WorkItemType.BRIGHTNESS:
                                                action.deviceAction = indigo.kDeviceAction.SetBrightness
                                                action.actionValue = workItem.brightness

                                            self.actionControlDevice(action, workItem.indigoDevice, True)
                                    else:
                                        self.debugLog('...runConcurrentThread SKIPPING stale workItem=' + str(workItem))
                                else:
                                    self.debugLog('...runConcurrentThread lightifyLock NOT acquired, num_tries=' + str(num_tries))
                            finally:
                                if have_it:
                                    self.debugLog('...runConcurrentThread RELEASING lightifyLock')
                                    self.lightifyLock.release()
                        self.debugLog('...runConcurrentThread Done, num_tries=' + str(num_tries))
                    self.debugLog('...runConcurrentThread EMPTY QUEUE')
                except Queue.Empty:
                    indigo.server.log('...runConcurrentThread EXCEPTION EMPTY QUEUE, EMPTY QUEUE, EMPTY QUEUE, EMPTY QUEUE')

        except self.StopThread:
            pass


    ########################################
    def groupListGenerator(self, filter="", valuesDict=None, typeId="", targetId=0):
        # Used in actions that need a list of Lightify groups.
        self.debugLog(u"Starting groupListGenerator.\n  filter: "
                      + unicode(filter) + u"\n  valuesDict: " + unicode(valuesDict) + u"\n  typeId: "
                      + unicode(typeId) + u"\n  targetId: " + unicode(targetId))

        returnGroupList = list()

        groupId = 0
        for theGroup in self.lightifyConn.groups():
            #theGroup = self.lightifyConn.groups()[grpName]
            #self.debugLog('...found group name=' + str(grpName))
            self.debugLog('...theGroup - groupId=' + str(groupId) + ', details=' + str(theGroup))
            returnGroupList.append([theGroup, theGroup])
            groupId = groupId + 1

        # Iterate over our bulbs, and return the available list in Indigo's format
        #for bulbId, bulbDetails in self.lightsDict.items():
        #    if typeId == "":
        #        # If no typeId exists, list all devices.
        #        returnBulbList.append([bulbId, bulbDetails['name']])
        #    elif typeId == "hueBulb" and bulbDetails['modelid'] in kHueBulbDeviceIDs:
        #        returnBulbList.append([bulbId, bulbDetails['name']])
        #    elif typeId == "hueAmbiance" and bulbDetails['modelid'] in kAmbianceDeviceIDs:
        #        returnBulbList.append([bulbId, bulbDetails['name']])
        #    elif typeId == "hueLightStrips" and bulbDetails['modelid'] in kLightStripsDeviceIDs:
        #        returnBulbList.append([bulbId, bulbDetails['name']])
        #    elif typeId == "hueLivingColorsBloom" and bulbDetails['modelid'] in kLivingColorsDeviceIDs:
        #        returnBulbList.append([bulbId, bulbDetails['name']])
        #    elif typeId == "hueLivingWhites" and bulbDetails['modelid'] in kLivingWhitesDeviceIDs:
        #        returnBulbList.append([bulbId, bulbDetails['name']])

        # Debug
        self.debugLog(u"groupListGenerator: Return bulb list is %s" % returnGroupList)

        return returnGroupList


    # Generate Scene List
    ########################################
    def sceneListGenerator(self, filter="", valuesDict=None, typeId="", deviceId=0):
        # Used by action dialogs to generate a list of Scenes saved in the plugin prefs.
        self.debugLog(u"Starting sceneListGenerator.\n  filter: " + unicode(filter) + u"\n  valuesDict: "
                      + unicode(valuesDict) + u"\n  typeId: " + unicode(typeId) + u"\n  deviceId: "
                      + unicode(deviceId))

        theList = list()	# Menu item list.

        scenes = self.pluginPrefs.get('scenes', None)
        self.debugLog(u"sceneListGenerator: Scenes in plugin prefs:\n" + unicode(scenes))

        if scenes != None:
            sceneNumber = 0

            for scene in scenes:
                # Determine whether the Scene has saved data or not.
                hasData = ""
                self.debugLog('scene ' + scene[0] + ', length is - ' + str(len(scene)))
                if len(scene) > 3:
                    hasData = "*"

                sceneNumber += 1
                sceneName = scene[0]
                theList.append((sceneNumber, hasData + unicode(sceneNumber) + ": " + sceneName))
        else:
            theList.append((0, "-- no scenes --"))

        return theList

    # Generate List of active scenes
    ########################################
    def activeSceneListGenerator(self, filter="", valuesDict=None, typeId="", deviceId=0):
        # Used by action dialogs to generate a list of Scenes saved in the plugin prefs.
        self.debugLog(u"Starting activeSceneListGenerator.\n  filter: " + unicode(filter) + u"\n  valuesDict: "
                      + unicode(valuesDict) + u"\n  typeId: " + unicode(typeId) + u"\n  deviceId: "
                      + unicode(deviceId))

        theList = list()	# Menu item list.

        scenes = self.pluginPrefs.get('scenes', None)
        #self.debugLog(u"activeSceneListGenerator: Scenes in plugin prefs:\n" + unicode(scenes))

        if scenes != None:
            sceneNumber = 0

            for scene in scenes:
                # Determine whether the Scene has saved data or not.
                hasData = False
                if len(scene) > 3:
                    hasData = True

                sceneNumber += 1
                if hasData is True:
                    sceneName = scene[0]
                    theList.append((sceneNumber, unicode(sceneNumber) + ": " + sceneName))
        else:
            theList.append((0, "-- no scenes --"))

        return theList


    # Scenes List Item Selected (callback from action UI)
    ########################################
    def scenesListItemSelected(self, valuesDict=None, typeId="", deviceId=0):
        self.debugLog(u"Starting scenesListItemSelected.  valuesDict: " + unicode(valuesDict)
                      + u", typeId: " + unicode(typeId) + u", targetId: " + unicode(deviceId))

        self.sceneListSelection = valuesDict['sceneId']
        sceneId = int(valuesDict['sceneId'])
        self.debugLog(u".. sceneId-" + self.sceneListSelection)

        theScene = self.pluginPrefs['scenes'][sceneId-1]

        valuesDict['sceneName'] = theScene[0]
        valuesDict['sceneType'] = theScene[1]
        valuesDict['sceneInterval'] = theScene[2]
        dataLen = 0
        sceneData = ''
        if len(theScene) > 3:
            sceneData = theScene[3]
            dataLen = len(sceneData)

        if dataLen >= 1:
            valuesDict['setting1Value'] = sceneData[0]
        else:
            valuesDict['setting1Value'] = "255,128,128,0,50,100"
        if dataLen >= 2:
            valuesDict['setting2Value'] = sceneData[1]
        else:
            valuesDict['setting2Value'] = "128,255,255,0,75,100"
        if dataLen >= 3:
            valuesDict['setting3Value'] = sceneData[2]
        else:
            valuesDict['setting3Value'] = ""
        if dataLen >= 4:
            valuesDict['setting4Value'] = sceneData[3]
        else:
            valuesDict['setting4Value'] = ""
        if dataLen >= 5:
            valuesDict['setting5Value'] = sceneData[4]
        else:
            valuesDict['setting5Value'] = ""

        circLen = 0
        circadianData = ''
        if len(theScene) > 4:
            circadianData = theScene[4]
            circLen = len(circadianData)

        if circLen >= 1:
            valuesDict['CircadianColorTempValues'] = circadianData[0]
        else:
            valuesDict['CircadianColorTempValues'] = "1500,2300,4000,6400,6500,4500,2200"
        if circLen >= 2:
            valuesDict['CircadianBrightnessValues'] = circadianData[1]
        else:
            valuesDict['CircadianBrightnessValues'] = "15,35,80,95,100,80,40"


        self.debugLog(u"... selected sceneId: " + unicode(sceneId)
                      + u", sceneName: " + unicode(theScene[0]) + u", sceneType: " + unicode(theScene[1])
                      + u", sceneInterval: " + unicode(theScene[2]))
        if dataLen > 0:
            self.debugLog(u"... sceneData:+ u" + unicode(theScene[3]))
        if circLen > 0:
            self.debugLog(u"... circadianData:+ u" + unicode(theScene[4]))

        return valuesDict


    # Save Scene Action
    ########################################
    #def saveScene(self, action, typeId=""):
    def saveScene(self, valuesDict, typeId):
        self.debugLog(u"Starting saveScene. valuesDict values:\n" + unicode(valuesDict)
                      +  ", typeId:\n" + unicode(typeId))
        errorsDict = indigo.Dict()
        errorsDict['showAlertText'] = u""
        actionType = "action"
        ## Work with both Menu and Action actions.
        #try:
        #    actionType = "menu"
        #except AttributeError:
        #    # This is an action, not a menu call.
        #    pass

        # Get the sceneId.
        #if actionType == "menu":
        #    sceneId = action.get('sceneId', False)
        #else:
        #    sceneId = action.props.get('sceneId', False)
        # 124,16,173,0,50,1000
        # 255,255,255,1600,50,1000

        sceneId = valuesDict['sceneId']
        sceneName = valuesDict['sceneName']
        sceneType = valuesDict['sceneType']
        sceneInterval = valuesDict['sceneInterval']

        self.debugLog(u"Starting saveScene. sceneId:" + unicode(sceneId)
                      +  ", name:" + unicode(sceneName)
                      +  ", interval:" + unicode(sceneInterval)
                      +  ", type:" + unicode(sceneType))

        if not sceneId:
            errorText = u"No Scene specified."
            self.errorLog(errorText)
            # Remember the error.
            self.lastErrorMessage = errorText
            return False
        else:
            # Convert to integer.
            sceneId = int(sceneId)
            # Subtract 1 because key values are 0-based.
            sceneId -= 1

        # build the list of data from the UI
        sceneData = list()

        #if not valuesDict['setting1Value']:
        #    #errorText = u"No Setting1 specified."
            #self.errorLog(errorText)
            # Remember the error.
            #self.lastErrorMessage = errorText
            #return False
        #    errorsDict['setting1Value'] =  u"No Setting1 specified."
        #    errorsDict['showAlertText'] += errorsDict['setting1Value']
        #    return valuesDict, errorsDict
        #else:
            # need to validate
        #    sceneData.append(valuesDict['setting1Value'])

        #if not valuesDict['setting3Value']:
            # Remember the error.
        #    errorsDict['setting3Value'] =  u"No Setting3 specified."
        #    errorsDict['showAlertText'] += errorsDict['setting3Value']
        #    errorText = u"No Setting3 specified."
        #    self.errorLog(errorText)
        #    #self.lastErrorMessage = errorText
        #    return valuesDict, errorsDict

        self.debugLog(u"saveScene - starting Validation for Scene " + unicode(sceneId + 1) + u" (" + sceneName + u") .")
        returnVal = True
        if sceneType == 'match-colors' or sceneType == 'rotate-colors':
            # must have at least 1 color setting
            configStr = 'setting1Value'
            if not valuesDict[configStr]:
                errorsDict[configStr] =  u"No " + configStr + u" specified."
                errorsDict['showAlertText'] += errorsDict[configStr]
                errorText = u"No " + configStr + u" specified."
                self.errorLog(errorText)
                returnVal = False
            else:
                returnVal, valuesDict, errorsDict = self.validateRGBWConfig('setting1Value', valuesDict, errorsDict)

        else:
            # must have at least 1 color setting
            configStr = 'CircadianColorTempValues'
            if not valuesDict[configStr]:
                errorsDict[configStr] =  u"No " + configStr + u" specified."
                errorsDict['showAlertText'] += errorsDict[configStr]
                errorText = u"No " + configStr + u" specified."
                self.errorLog(errorText)
                returnVal = False
            configStr = 'CircadianBrightnessValues'
            if not valuesDict[configStr]:
                errorsDict[configStr] =  u"No " + configStr + u" specified."
                errorsDict['showAlertText'] += errorsDict[configStr]
                errorText = u"No " + configStr + u" specified."
                self.errorLog(errorText)
                returnVal = False

            if returnVal == True:
                returnVal, valuesDict, errorsDict = self.validateCircadianConfig('CircadianColorTempValues', valuesDict, errorsDict)
            if returnVal == True:
                returnVal, valuesDict, errorsDict = self.validateCircadianConfig('CircadianBrightnessValues', valuesDict, errorsDict)

        if returnVal is False:
            self.debugLog(u"saveScene - errors in validation Scene " + unicode(sceneId + 1) + u" (" + sceneName + u") ."
                          + unicode(str(errorsDict['showAlertText'])))
            return valuesDict, errorsDict

        self.debugLog(u"saveScene - finished Validation for Scene " + unicode(sceneId + 1) + u" (" + sceneName + u") .")

        if valuesDict['setting1Value']:
            sceneData.append(valuesDict['setting1Value'])
        if valuesDict['setting2Value']:
            sceneData.append(valuesDict['setting2Value'])
        if valuesDict['setting3Value']:
            sceneData.append(valuesDict['setting3Value'])
        if valuesDict['setting4Value']:
            sceneData.append(valuesDict['setting4Value'])
        if valuesDict['setting5Value']:
            sceneData.append(valuesDict['setting5Value'])

        circadianData = list()
        if valuesDict['CircadianColorTempValues']:
            circadianData.append(valuesDict['CircadianColorTempValues'])
        if valuesDict['CircadianBrightnessValues']:
            circadianData.append(valuesDict['CircadianBrightnessValues'])

        # Get the plugin prefs and populate them into a local array.
        scenes = list()
        for num in range(0,len(self.pluginPrefs['scenes'])):
            self.debugLog(u"Checking existing sceneData. sceneId:" + unicode(num)
                          +  ", data:" + unicode(self.pluginPrefs['scenes'][num]))
            tempSceneName = self.pluginPrefs['scenes'][num][0]
            tempSceneType = self.pluginPrefs['scenes'][num][1]
            tempSceneInterval = self.pluginPrefs['scenes'][num][2]
            if len(self.pluginPrefs['scenes'][num]) > 3:
                tempSceneData = self.pluginPrefs['scenes'][num][3]
            else:
                tempSceneData = ""
            if len(self.pluginPrefs['scenes'][num]) > 4:
                tempCircadianData = self.pluginPrefs['scenes'][num][4]
            else:
                tempCircadianData = ""
            self.debugLog(u"Checking existing sceneData. sceneId:" + unicode(num)
                          +  ", name:" + unicode(tempSceneName)
                          +  ", type:" + unicode(tempSceneType)
                          +  ", interval:" + unicode(tempSceneInterval)
                          +  ", sceneData:" + unicode(tempSceneData)
                          +  ", circadianData:" + unicode(tempCircadianData)
                          )
            scenes.append(list((tempSceneName, tempSceneType, tempSceneInterval, tempSceneData, tempCircadianData)))

        # If the submitted name is not blank, change the name in the prefs.
        if sceneName != "":
            # (Index 0 = scene name).
            scenes[sceneId][0] = sceneName
        else:
            # Submitted sceneName is blank. Use the current one for logging.
            sceneName = scenes[sceneId][0]

        # If the submitted type is not blank, change the one in the prefs.
        if sceneType != "":
            # (Index 1 = scene type).
            scenes[sceneId][1] = sceneType
        else:
            # Submitted type is blank. Use the current one for logging.
            sceneType = scenes[sceneId][1]

        # If the submitted interval is not blank, change the one in the prefs.
        if sceneInterval != "":
            # (Index 2 = scene interval).
            scenes[sceneId][2] = sceneInterval
        else:
            # Submitted sceneInterval is blank. Use the current one for logging.
            sceneInterval = scenes[sceneId][2]

        # If the submitted data is not blank, change the one in the prefs.
        if sceneData != "":
            # (Index 3 = scene data).
            scenes[sceneId][3] = sceneData
        else:
            # Submitted sceneData is blank. Use the current one for logging.
            sceneData = tempSceneData

        # If the submitted circadian data is not blank, change the one in the prefs.
        if circadianData != "":
            # (Index 4 = circadian data).
            scenes[sceneId][4] = circadianData
        else:
            # Submitted sceneData is blank. Use the current one for logging.
            circadianData = tempCircadianData


        # Save the device's states to the preset.
        self.pluginPrefs['scenes'] = scenes

        indigo.server.log(u"saveScene - states saved to Scene " + unicode(sceneId + 1) + u" (" + sceneName + u") .")


    def getMenuActionConfigUiValues(self, menuId):
        valuesDict = indigo.Dict()
        errorMsgDict = indigo.Dict()

        if menuId == "saveScene":
            scenes = self.pluginPrefs.get('scenes', None)
            self.debugLog(u"getMenuActionConfigUiValues: get initial value for saveScene dialog.")

            theScene = None

            if scenes != None:
                sceneNumber = 0

                for scene in scenes:
                    # Determine whether the Scene has saved data or not.
                    if len(scenes[sceneNumber][1]) > 0:
                        if sceneNumber is 0:
                            theScene = scene
                    sceneNumber += 1

            if theScene is not None:
                self.debugLog(u"...getMenuActionConfigUiValues: loading data for scene0:\n" + unicode(theScene))

                valuesDict['sceneName'] = theScene[0]
                valuesDict['sceneType'] = theScene[1]
                valuesDict['sceneInterval'] = theScene[2]
                sceneData = theScene[3]
                dataLen = len(sceneData)
                if dataLen >= 1:
                    valuesDict['setting1Value'] = sceneData[0]
                else:
                    valuesDict['setting1Value'] = ""
                if dataLen >= 2:
                    valuesDict['setting2Value'] = sceneData[1]
                else:
                    valuesDict['setting2Value'] = ""
                if dataLen >= 3:
                    valuesDict['setting3Value'] = sceneData[2]
                else:
                    valuesDict['setting3Value'] = ""
                if dataLen >= 4:
                    valuesDict['setting4Value'] = sceneData[3]
                else:
                    valuesDict['setting4Value'] = ""
                if dataLen >= 5:
                    valuesDict['setting5Value'] = sceneData[4]
                else:
                    valuesDict['setting5Value'] = ""

        return (valuesDict, errorMsgDict)

    ### Start the scene
    def startScene(self, action, device):
        self.debugLog(u"startScene: device.id: " + unicode(device.id) + u", action:\n" + unicode(action))
        indigoDevice = indigo.devices[action.deviceId]
        self.debugLog("...startScene - group device id: " + str(action.deviceId) + ", name: " + indigoDevice.name)
        theGroup = self.getLightifyGroup(indigoDevice)

        sceneId = int(action.props.get('sceneId', -1))
        scenes = self.pluginPrefs.get('scenes', None)

        if scenes is not None and sceneId != -1 and theGroup is not None:
            scene = scenes[sceneId-1]
            self.debugLog("...startScene - group: " + str(indigoDevice.name) + ", scene: " + str(scene))
            sceneName = scene[0]
            sceneType = scene[1]
            sceneInterval = int(scene[2])
            sceneData = scene[3]
            if sceneType == "circadian" and len(scene) > 4:
                circadianData = scene[4]

            indigo.server.log("startScene LightifyGroup: " + str(indigoDevice.name) + ", scene: " + str(sceneName) +
                          ", type:" + str(sceneType) + ", interval:" + str(sceneInterval))
            sceneArray = []
            if sceneType != "circadian":
                for num in range(0,len(sceneData)):
                    self.debugLog("...num=" + str(num) + ", data=" + str(sceneData[num]))

                    tempArray = sceneData[num].split(",")
                    redVal = int(tempArray[0])
                    greenVal = int(tempArray[1])
                    blueVal = int(tempArray[2])
                    colorTemp = int(tempArray[3])
                    brightness = int(tempArray[4])
                    transMilli = int(tempArray[5])
                    sceneArray.append([redVal, greenVal, blueVal, colorTemp, brightness, transMilli])
            else:
                if len(circadianData) == 2:
                    self.debugLog("...circadian temp=" + str(circadianData[0]))
                    self.debugLog("...circadian brightness=" + str(circadianData[1]))
                    sceneArray.append(circadianData[0])
                    sceneArray.append(circadianData[1])

            if theGroup is not None and len(sceneArray) != 0:
                lightArray = []
                theLight = None
                for curLight in theGroup.lights():
                    theLight = self.lightifyConn.lights()[curLight]
                    if theLight is not None:
                        self.debugLog('...theLight =' + str(theLight) + ', on=' + str(theLight.on()))
                        lightArray.append(theLight)

                self.stopSceneThread(indigoDevice)

                # create a new one with the correct scene
                self.debugLog("Creating a new scene thread: " + indigoDevice.name)
                deviceSceneThread = None
                if sceneType == "rotate-colors":
                    deviceSceneThread = RgbRotateSceneThread(indigoDevice, self.logger, sceneName, sceneInterval, self.lightifyConn,
                                                   theGroup, sceneArray, self.lightifyQueue)
                elif sceneType == "match-colors":
                    deviceSceneThread = RgbMatchSceneThread(indigoDevice, self.logger, sceneName, sceneInterval, self.lightifyConn,
                                                       theGroup, sceneArray, self.lightifyQueue)
                elif sceneType == "circadian":
                    deviceSceneThread = CircadianSceneThread(indigoDevice, self.logger, sceneName, sceneInterval, self.lightifyConn,
                                                            theGroup, sceneArray, self.lightifyQueue)

                indigoDevice.updateStateOnServer("activeScene", sceneName)
                self.updateUIForScene(indigoDevice)

                self.deviceThreads.append(deviceSceneThread)

        return

    ### stop the scene
    def stopScene(self, action, device):
        self.debugLog(u"stopScene: device.id: " + unicode(device.id) + u", action:\n" + unicode(action))
        indigoDevice = indigo.devices[action.deviceId]
        self.debugLog("...stopScene - group device id: " + str(action.deviceId) + ", name: " + indigoDevice.name)

        indigoDevice = indigo.devices[action.deviceId]
        indigoDevice.updateStateOnServer("activeScene", "None")
        self.updateUIForScene(indigoDevice)

        resetTemp = bool(action.props.get('resetTemp', False))

        indigo.server.log("stopScene LightifyGroup: " + indigoDevice.name + ", device id: " + str(indigoDevice.id))

        stoppedThread = self.stopSceneThread(indigoDevice)
        # check to see if we need to reset color/temp/etc if we found and stopped a thread
        if stoppedThread and resetTemp is True:
            # reset all the lights to be 2700
            self.debugLog("...stopScene resetting bulbs to 2700 : " + indigoDevice.name)
            #theGroup.set_temperature(2700, 25)
            # TODO check to see if we need to set the color temps - circadian mode shouldn't need this step
            lightifyAction = LightifyAction()
            # first do color temp
            lightifyAction.deviceId = indigoDevice.id
            lightifyAction.deviceAction = indigo.kDeviceAction.SetColorLevels
            lightifyAction.actionValue = { "redLevel": 255,
                                        "greenLevel": 255,
                                        "blueLevel": 255,
                                        "whiteLevel": 0,
                                        "whiteLevel2": 0,
                                        "whiteTemperature": 2700}
            self.actionControlDevice(lightifyAction, indigoDevice)
        else:
            self.debugLog("...stopScene skipping reset - no scene thread found : " + indigoDevice.name)

        return

    def stopSceneThread(self, device):
        indigoDevice = indigo.devices[device.id]
        deviceSceneThread = None
        stoppedThread = False
        for gThread in self.deviceThreads:
            self.debugLog("...stopSceneThread Found scene thread: " + str(gThread.indigoDevice.name))
            if gThread.indigoDevice.name == indigoDevice.name:
                deviceSceneThread = gThread
                self.debugLog("...stopSceneThread Found matching scene thread: " + indigoDevice.name)

        if deviceSceneThread is not None:
            self.debugLog("...stopSceneThread Stopping scene thread: " + indigoDevice.name)
            deviceSceneThread.stopDevConcurrentThread()
            self.deviceThreads.remove(deviceSceneThread)
            deviceSceneThread = None
            stoppedThread = True
            # any remaining scene workItems will be skipped if an activeScene Thread isn't found for the device

        # lets also output all of the threads in action
        sceneThreadCount = 0
        for curSceneThread in self.deviceThreads:
            sceneThreadCount = sceneThreadCount + 1
            self.debugLog("...stopSceneThread Found running scene thread - groupName=" + curSceneThread.indigoDevice.name +
                              ",thread=" +str(curSceneThread))
        self.debugLog("...stopSceneThread Total remaining scene threads - " + str(sceneThreadCount))
        return stoppedThread

    ########################################
    def getLightifyGroup(self, device):
        self.debugLog("getLightifyGroup device id: " + str(device.id) + ", name: " + device.name)
        # refresh info from the hub
        deviceGrpName = device.pluginProps["groupName"]
        # find the group that matches us and update accordingly
        theGroup = None
        for grpName in self.lightifyConn.groups():
            if grpName == deviceGrpName:
                theGroup = self.lightifyConn.groups()[grpName]
                self.debugLog('...found group name=' + str(grpName))
                self.debugLog('...details=' + str(theGroup))
        return theGroup

    ########################################
    def update(self, device):
        self.debugLog("Updating device id: " + str(device.id) + ", name: " + device.name)
        theGroup = self.getLightifyGroup(device)

        # refresh the states based on what is found on the first device
        if theGroup is not None:
            theLight = None
            for curLight in theGroup.lights():
                theLight = self.lightifyConn.lights()[curLight]
                if theLight.on() == 1:
                    break

            if theLight is not None:
                self.debugLog('...theLight =' + str(theLight) + ', on=' + str(theLight.on()))

    ########################################
    # UI Validate, Close, and Actions defined in Actions.xml:
    ########################################
    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        # hub = valuesDict['ipAddr'].encode('ascii','ignore').upper()
        # valuesDict['address'] = hub
        # can validate this is a valid ip addr:
        self.debugLog("Need to validate devId:" + str(devId))
        return (True, valuesDict)

    ########################################
    # Validate RGBW string
    ########################################
    def validateRGBWConfig(self, configStr, valuesDict, errorsDict):

        if not valuesDict[configStr]:
            errorsDict[configStr] =  u"No " + configStr + u" specified."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = u"No " + configStr + u" specified."
            self.errorLog(errorText)
            #return valuesDict, errorsDict
            return False, valuesDict, errorsDict

        tempArray = valuesDict[configStr].split(",")
        if len(tempArray) != 6:
            errorsDict[configStr] =  configStr + u" must have 6 values. R,G,B,Temp,Brightness,TransMilli"
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" must have 6 values. R,G,B,Temp,Brightness,TransMilli"
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        tempArray = valuesDict[configStr].split(",")
        redVal = int(tempArray[0])
        greenVal = int(tempArray[1])
        blueVal = int(tempArray[2])
        colorTemp = int(tempArray[3])
        brightness = int(tempArray[4])
        transMilli = int(tempArray[5])

        isTemp = False
        if colorTemp > 0:
            isTemp = True

        if isTemp == False and (redVal < 0 or redVal > 255 or greenVal < 0 or greenVal > 255 or blueVal < 0 or blueVal > 255):
            errorsDict[configStr] =  configStr + u" RGB values must be between 0 and 255."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" RGB values must be between 0 and 255."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        if isTemp == True and (redVal != 255 or greenVal != 255 or blueVal != 255):
            errorsDict[configStr] =  configStr + u" ColorTemp RGB values must be 255."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" ColorTemp RGB values must be 255."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        if isTemp == True and (colorTemp < 1500 or colorTemp > 6500):
            errorsDict[configStr] =  configStr + u" ColorTemp must be between 1500 and 2500."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" ColorTemp must be between 1500 and 2500."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        if brightness < 1 or brightness > 100:
            errorsDict[configStr] =  configStr + u" Brightness must be between 1 and 100."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" Brightness must be between 1 and 100."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        if transMilli < 10 or transMilli > 100000:
            errorsDict[configStr] =  configStr + u" transMilli must be between 10 and 100000."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" transMilli must be between 10 and 100000."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        return True, valuesDict, errorsDict

    ########################################
    # Validate Circadian Value
    ########################################
    def validateCircadianConfig(self, configStr, valuesDict, errorsDict):
        isTemp = (configStr == 'CircadianColorTempValues')

        # 1650,2400,3800,6400,6500,4500,2200
        # Late Night, Pre-Sunrise, Post-Sunrise, AM Peak, Max Temp, Pre-Sunset, Post-Sunset
        # Late Night&lt;Pre-Sunrise&lt;Post-Sunrise&lt;AM Peak&lt;Max, also Max&gt;Pre-Sunset&gt;Post-Sunset&gt;Late Night

        if not valuesDict[configStr]:
            errorsDict[configStr] =  u"No " + configStr + u" specified."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = u"No " + configStr + u" specified."
            self.errorLog(errorText)
            #return valuesDict, errorsDict
            return False, valuesDict, errorsDict

        tempArray = valuesDict[configStr].split(",")
        if len(tempArray) != 7:
            errorsDict[configStr] =  configStr + u" must have 7 values. Late Night,Pre-Sunrise,Post-Sunrise,AM Peak,Max Temp,Pre-Sunset,Post-Sunset."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" must have 7 values. Late Night,Pre-Sunrise,Post-Sunrise,AM Peak,Max Temp,Pre-Sunset,Post-Sunset."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        tempArray = valuesDict[configStr].split(",")
        lateNight = int(tempArray[0])
        preSunrise = int(tempArray[1])
        postSunrise = int(tempArray[2])
        amPeak = int(tempArray[3])
        maxVal= int(tempArray[4])
        preSunset = int(tempArray[5])
        postSunset = int(tempArray[6])

        if lateNight > preSunrise or preSunrise > postSunrise or postSunrise > amPeak or amPeak > maxVal:
            errorsDict[configStr] =  configStr + u" - invalid values: Ensure Late Night > Pre-Sunrise > Post-Sunrise > AM Peak > Max."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" - invalid values: Ensure Late Night > Pre-Sunrise > Post-Sunrise > AM Peak > Max."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        if maxVal < preSunset or preSunset < postSunset or postSunset < lateNight:
            errorsDict[configStr] =  configStr + u" Invalid values: Ensure Max > Pre-Sunset > Post-Sunset > Late Night."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" - invalid values: Ensure Max > Pre-Sunset > Post-Sunset > Late Night."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        if isTemp is True and (lateNight < 1500 or lateNight > 6500 or preSunrise < 1500 or preSunrise > 6500 \
                or postSunrise < 1500 or postSunrise > 6500 or amPeak < 1500 or amPeak > 6500 \
                or maxVal < 1500 or maxVal > 6500 or preSunset < 1500 or preSunset > 6500 \
                or postSunset < 1500 or postSunset > 6500):
            errorsDict[configStr] =  configStr + u" values must be between 1500 and 6500."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" values must be between 1500 and 6500."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        if isTemp is False and (lateNight < 1 or lateNight > 100 or preSunrise < 1 or preSunrise > 100 \
               or postSunrise < 1 or postSunrise > 100 or amPeak < 1 or amPeak > 100 \
               or maxVal < 1 or maxVal > 100 or preSunset < 1 or preSunset > 100 \
               or postSunset < 0 or postSunset > 100):
            errorsDict[configStr] =  configStr + u" values must be between 1 and 100."
            errorsDict['showAlertText'] += errorsDict[configStr]
            errorText = configStr + u" values must be between 1 and 100."
            self.errorLog(errorText)
            return False, valuesDict, errorsDict

        return True, valuesDict, errorsDict

    ######################################################################################
    # Validations for Plugin Prefs
    #def validatePrefsConfigUi(self, valuesDict):
    #    self.debugLog(u"Vaidating Plugin Configuration")
    #    errorsDict = indigo.Dict()
    #    # if valuesDict[u"rootZPIP"] == "":
    #    #        errorsDict[u"rootZPIP"] = u"Please enter a reference ZonePlayer IP Address."
    #    if len(errorsDict) > 0:
    #        self.errorLog(u"\t Validation Errors")
    #        return (False, valuesDict, errorsDict)
    #    else:
    #        self.debugLog(u"\t Validation Succesful")
    #        return (True, valuesDict)

    ########################################
    # Menu Methods
    ########################################
    def toggleDebugging(self):
        if self.debug:
            indigo.server.log("Turning off debug logging")
            self.pluginPrefs["showDebugInfo"] = False
        else:
            indigo.server.log("Turning on debug logging")
            self.pluginPrefs["showDebugInfo"] = True
        self.debug = not self.debug

    ########################################
    # helper method to update the UIValue to show a scene
    ########################################
    def updateUIForScene(self, dev):
        indigoDevice = indigo.devices[dev.id]
        brightness = indigoDevice.states['brightnessLevel']
        activeScene = indigoDevice.states['activeScene'].strip()
        self.debugLog("updateUIForScene device name=" + dev.name + ",activeScene=" + activeScene +
                          ",brightness=" + str(brightness))

        activeSceneType = None
        for num in range(0,len(self.pluginPrefs['scenes'])):
            sceneName = self.pluginPrefs['scenes'][num][0]
            sceneType = self.pluginPrefs['scenes'][num][1]
            if sceneName.strip() == activeScene:
                activeSceneType = sceneType
                break

        whiteTemp = "2700"
        redLevel = "0"
        greenLevel = "0"
        blueLevel = "0"
        if indigoDevice.supportsWhiteTemperature is True and 'whiteTemperature.ui' in indigoDevice.states.keys():
            whiteTemp = indigoDevice.states['whiteTemperature.ui']
        if indigoDevice.supportsRGB is True and 'redLevel.ui' in indigoDevice.states.keys() \
                and 'greenLevel.ui' in indigoDevice.states.keys() and 'blueLevel.ui' in indigoDevice.states.keys():
            redLevel = indigoDevice.states['redLevel.ui']
            greenLevel = indigoDevice.states['greenLevel.ui']
            blueLevel = indigoDevice.states['blueLevel.ui']

        if str(brightness) != "0" and whiteTemp != "0":
            stateStr = str(brightness) + "/" + str(whiteTemp) + "K"
            if activeScene is not None and activeScene != "None":
                indigoDevice.updateStateOnServer("brightnessLevel", value=brightness,
                                             uiValue=activeScene.ljust(5) + stateStr.rjust(10))
            else:
                indigoDevice.updateStateOnServer("brightnessLevel", value=brightness,
                                                 uiValue=stateStr)

        elif str(brightness) != "0" and (redLevel != "0" or greenLevel != "0" or blueLevel != "0"):
            #rgbStr = '#%02x%02x%02x' % (int(redLevel), int(greenLevel), int(blueLevel))
            #stateStr = str(brightness) + "/" + redLevel + "-" + greenLevel + "-" + blueLevel
            #stateStr = str(brightness) + "/" + rgbStr
            stateStr = str(brightness)
            if activeScene is not None and activeScene != "None":
                indigoDevice.updateStateOnServer("brightnessLevel", value=brightness,
                                                 uiValue=activeScene.ljust(5) + stateStr.rjust(10))
            else:
                indigoDevice.updateStateOnServer("brightnessLevel", value=brightness,
                                                 uiValue=stateStr)

        else:
            indigoDevice.updateStateOnServer("brightnessLevel", value=brightness,
                                             uiValue=str(brightness))


    ########################################
    # delegate method from the plugin - we don't have a lock
    ########################################
    def actionControlDevice(self, action, dev):
        self.actionControlDevice(action, dev, False)

    ########################################
    # Methods for the dimmer device
    ########################################
    def actionControlDevice(self, action, dev, gotLock=False):
        self.debugLog(u"...actionControlDevice - device=\"%s\", action=%s" % (dev.name, action.deviceAction))
        self.debugLog('...actionControlDevice action=' + str(action))
        ###### First get the lightify device group
        theGroup = self.getLightifyGroup(dev)
        if theGroup is None:
            sendSuccess = False  # Set to False if it failed.
            self.debugLog(u"...actionControlDevice - lightify group not found \"%s\"" % (dev.name), isError=True)
        else:
            try:
                if gotLock is not True:
                    self.lightifyLock.acquire()

                self.debugLog(u"...actionControlDevice - lightify group found \"%s\"" % (dev.name))
                ###### TURN ON ######
                if action.deviceAction == indigo.kDeviceAction.TurnOn:
                    # Command hardware module (dev) to turn ON here:
                    theGroup.set_onoff(1)
                    sendSuccess = True  # Set to False if it failed.

                    if sendSuccess:
                        # If success then log that the command was successfully sent.
                        indigo.server.log(u"\"%s\" %s" % (dev.name, "on"))

                        # And then tell the Indigo Server to update the state.
                        #dev.updateStateOnServer("onOffState", True)
                        dev.updateStateOnServer('onOffState', value=True, uiValue='on')
                        #self.updateUIForScene(dev)
                    else:
                        # Else log failure but do NOT update state on Indigo Server.
                        indigo.server.log(u"\"%s\" %s failed" % (dev.name, "on"), isError=True)

                ###### TURN OFF ######
                elif action.deviceAction == indigo.kDeviceAction.TurnOff:

                    activeScene = dev.states.get('activeScene', None)
                    self.debugLog(u"...actionControlDevice - activeScene= \"%s\"" % (activeScene))

                    if activeScene is not None:
                        self.stopSceneThread(dev)
                        dev.updateStateOnServer("activeScene", "None")
                        self.updateUIForScene(dev)


        # Command hardware module (dev) to turn OFF here:
                    theGroup.set_onoff(0)
                    sendSuccess = True  # Set to False if it failed.

                    if sendSuccess:
                        # If success then log that the command was successfully sent.
                        indigo.server.log(u"\"%s\" %s" % (dev.name, "off"))

                        # And then tell the Indigo Server to update the state:
                        dev.updateStateOnServer('onOffState', value=False, uiValue='off')
                        dev.updateStateOnServer("brightnessLevel", 0)
                    else:
                        # Else log failure but do NOT update state on Indigo Server.
                        indigo.server.log(u"\"%s\" %s failed" % (dev.name, "off"), isError=True)

                ###### TOGGLE ######
                elif action.deviceAction == indigo.kDeviceAction.Toggle:
                    # Command hardware module (dev) to toggle here:
                    # ** IMPLEMENT ME **
                    newOnState = not dev.onState
                    sendSuccess = True  # Set to False if it failed.

                    if sendSuccess:
                        # If success then log that the command was successfully sent.
                        indigo.server.log(u"\"%s\" %s" % (dev.name, "toggle"))

                        # And then tell the Indigo Server to update the state:
                        dev.updateStateOnServer("onOffState", newOnState)
                    else:
                        # Else log failure but do NOT update state on Indigo Server.
                        indigo.server.log(u"\"%s\" %s failed" % (dev.name, "toggle"), isError=True)

                ###### SET BRIGHTNESS ######
                elif action.deviceAction == indigo.kDeviceAction.SetBrightness:
                    # Command hardware module (dev) to set brightness here:
                    # ** IMPLEMENT ME **
                    newBrightness = action.actionValue
                    # delayAmount = action.delayAmount
                    delayAmount = 50
                    theGroup.set_luminance(newBrightness, delayAmount)
                    sendSuccess = True  # Set to False if it failed.

                    if sendSuccess:
                        # If success then log that the command was successfully sent.
                        indigo.server.log(u"\"%s\" %s to %d" % (dev.name, "set brightness", newBrightness))

                        # And then tell the Indigo Server to update the state:
                        dev.updateStateOnServer("brightnessLevel", newBrightness)
                        #self.updateUIForScene(dev)
                    else:
                        # Else log failure but do NOT update state on Indigo Server.
                        indigo.server.log(u"\"%s\" %s to %d failed" % (dev.name, "set brightness", newBrightness),
                                          isError=True)

                ###### BRIGHTEN BY ######
                elif action.deviceAction == indigo.kDeviceAction.BrightenBy:
                    # Command hardware module (dev) to do a relative brighten here:
                    # ** IMPLEMENT ME **
                    newBrightness = dev.brightness + action.actionValue
                    if newBrightness > 100:
                        newBrightness = 100
                    sendSuccess = True  # Set to False if it failed.

                    if sendSuccess:
                        # If success then log that the command was successfully sent.
                        indigo.server.log(u"\"%s\" %s to %d" % (dev.name, "brighten", newBrightness))

                        # And then tell the Indigo Server to update the state:
                        dev.updateStateOnServer("brightnessLevel", newBrightness)
                        #self.updateUIForScene(dev)
                    else:
                        # Else log failure but do NOT update state on Indigo Server.
                        indigo.server.log(u"\"%s\" %s to %d failed" % (dev.name, "brighten", newBrightness),
                                          isError=True)

                ###### DIM BY ######
                elif action.deviceAction == indigo.kDeviceAction.DimBy:
                    # Command hardware module (dev) to do a relative dim here:
                    # ** IMPLEMENT ME **
                    newBrightness = dev.brightness - action.actionValue
                    if newBrightness < 0:
                        newBrightness = 0
                    sendSuccess = True  # Set to False if it failed.

                    if sendSuccess:
                        # If success then log that the command was successfully sent.
                        indigo.server.log(u"\"%s\" %s to %d" % (dev.name, "dim", newBrightness))

                        # And then tell the Indigo Server to update the state:
                        dev.updateStateOnServer("brightnessLevel", newBrightness)
                        #self.updateUIForScene(dev)

                    else:
                        # Else log failure but do NOT update state on Indigo Server.
                        indigo.server.log(u"\"%s\" %s to %d failed" % (dev.name, "dim", newBrightness),
                                          isError=True)

                ###### SET COLOR LEVELS ######
                elif action.deviceAction == indigo.kDeviceAction.SetColorLevels:
                    # action.actionValue is a dict containing the color channel key/value
                    # pairs. All color channel keys (redLevel, greenLevel, etc.) are optional
                    # so plugin should handle cases where some color values are not specified
                    # in the action.
                    actionColorVals = action.actionValue

                    # Construct a list of channel keys that are possible for what this device
                    # supports. It may not support RGB or may not support white levels, for
                    # example, depending on how the device's properties (SupportsColor, SupportsRGB,
                    # SupportsWhite, SupportsTwoWhiteLevels, SupportsWhiteTemperature) have
                    # been specified.
                    channelKeys = []
                    usingWhiteChannels = False
                    if dev.supportsRGB:
                        channelKeys.extend(['redLevel', 'greenLevel', 'blueLevel'])
                    if dev.supportsWhite:
                        channelKeys.extend(['whiteLevel'])
                        usingWhiteChannels = True
                    if dev.supportsTwoWhiteLevels:
                        channelKeys.extend(['whiteLevel2'])
                    elif dev.supportsWhiteTemperature:
                        channelKeys.extend(['whiteTemperature'])
                    # Note having 2 white levels (cold and warm) takes precedence over
                    # the use of a white temperature value. You cannot have both, although
                    # you can have a single white level and a white temperature value.

                    # Next enumerate through the possible color channels and extract that
                    # value from the actionValue (actionColorVals).
                    keyValueList = []
                    resultVals = []
                    self.debugLog('channelKeys = ' + str(channelKeys))
                    red = 255
                    green = 255
                    blue = 255
                    temperature = 0
                    for channel in channelKeys:
                        self.debugLog('channel = ' + str(channel))
                        if channel in actionColorVals:
                            brightness = float(actionColorVals[channel])
                            brightnessByte = int(round(255.0 * (brightness / 100.0)))

                            if dev.supportsRGB == False and channel == 'whiteTemperature' and brightness > 0 and brightness < 2700:
                                indigo.server.log(u"\"%s\" is tunable-white - cannot set lower than 2700K (%s) " % (dev.name, actionColorVals[channel]))
                                # Lightify Tunable White bulbs cannot go lower than 2700K
                                brightness = float(2700)

                            # Command hardware module (dev) to change its color level here:
                            # ** IMPLEMENT ME **

                            if channel in dev.states:
                                keyValueList.append({'key': channel, 'value': brightness})
                            result = str(int(round(brightness)))
                            if channel == 'redLevel':
                                red = int(round(brightness))
                            elif channel == 'blueLevel':
                                blue = int(round(brightness))
                            elif channel == 'greenLevel':
                                green = int(round(brightness))
                            elif channel == 'whiteTemperature':
                                temperature = int(round(brightness))

                        elif channel in dev.states:
                            # If the action doesn't specify a level that is needed (say the
                            # hardware API requires a full RGB triplet to be specified, but
                            # the action only contains green level), then the plugin could
                            # extract the currently cached red and blue values from the
                            # dev.states[] dictionary:
                            cachedBrightness = float(dev.states[channel])
                            cachedBrightnessByte = int(round(255.0 * (cachedBrightness / 100.0)))
                            # Could show in the Event Log '--' to indicate this level wasn't
                            # passed in by the action:
                            result = '--'
                        # Or could show the current device state's cached level:
                        #	result = str(int(round(cachedBrightness)))

                        # Add a comma to separate the RGB values from the white values for logging.
                        if channel == 'blueLevel' and usingWhiteChannels:
                            result += ","
                        elif channel == 'whiteTemperature' and result != '--':
                            result += " K"
                        resultVals.append(result)
                    # def set_temperature(self, temp, time):
                    # def set_rgb(self, r, g, b, time):
                    if temperature > 0 and red == 255 and green == 255 and blue == 255:
                        self.debugLog(
                            u"...SetColor lightify set_temperature - for \"%s\" red=%s, green=%s, blue=%s, temp=%s" % (
                                dev.name, str(red), str(green), str(blue), str(temperature)))
                        theGroup.set_temperature(temperature, 50)
                    if red != 255 or green != 255 or blue != 255:
                        if temperature == 0:
                            self.debugLog(
                                u"...SetColor lightify set_rgb - for \"%s\" red=%s, green=%s, blue=%s, temp=%s" % (
                                    dev.name, str(red), str(green), str(blue), str(temperature)))
                            theGroup.set_rgb(red, green, blue, 50)
                    # Set to False if it failed.
                    sendSuccess = True

                    resultValsStr = ' '.join(resultVals)
                    if sendSuccess:
                        # If success then log that the command was successfully sent.
                        indigo.server.log(u"\"%s\" %s to %s" % (dev.name, "set color", resultValsStr))

                        # And then tell the Indigo Server to update the color level states:
                        if len(keyValueList) > 0:
                            dev.updateStatesOnServer(keyValueList)
                    else:
                        # Else log failure but do NOT update state on Indigo Server.
                        indigo.server.log(u"\"%s\" %s to %s failed" % (dev.name, "set color", resultValsStr),
                                          isError=True)
                else:
                    indigo.server.log(u"Unknown action for " + dev.name + ", action=" + action.deviceAction)

                self.updateUIForScene(dev)

            finally:
                if gotLock is not True:
                    self.logger.debug('...actionControlDevice RELEASING lightify lock')
                    self.lightifyLock.release()


# Base class for Scene Threads
class LightifySceneThread(threading.Thread):
    def __init__(self, indigoDevice, logger, sceneName, sceneSleep, lightifyConn, lightifyGroup, lightifyQueue):
        super(LightifySceneThread, self).__init__()
        self.indigoDevice = indigoDevice
        self.logger = logger
        self.stopThread = False
        self.lightifyConn = lightifyConn
        self.lightifyGroup = lightifyGroup
        self.sceneName = sceneName
        self.sceneSleep = sceneSleep
        self.lightifyQueue = lightifyQueue

    def startScene(self):
        # start the scene
        self.logger.debug(
            "...start Scene " + self.sceneName + " for group - " + str(self.indigoDevice.name) + ", thread-id=" + str(
                self.name))

    def stopScene(self):
        # stop the scene
        self.logger.debug(
            "...stop Scene " + self.sceneName + " for group - " + str(self.indigoDevice.name) + ", thread-id=" + str(
                self.name))

    def run(self):
        try:
            self.startScene()
            while not self.stopThread:
                try:
                    # do the scene stuff
                    self.logger.debug("...Scene " + self.sceneName + " group running - " + str(
                        self.indigoDevice.name) + ", thread-id=" + str(self.name))

                    # take a sleep based on the scene preferences
                    time.sleep(self.sceneSleep)
                except:  # Do my other non-socket reading stuff here
                    self.logger.debug(
                        "...Scene group exception - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
                    self.logger.debug(
                        "...Unexpected loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

        except:
            self.logger.debug(
                "...Scene exception hit, process exiting - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
            self.logger.debug("...Unexpected non-loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

        finally:  # Make sure you don't leave any open network connections
            self.stopScene()

    def stopDevConcurrentThread(self):
        self.logger.debug(
            "...stopping concurrent thread for group - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
        self.stopThread = True

# rotates each bulbs in the group thru the different RGBs in the scene - each bulb will take on a different color
class RgbRotateSceneThread(LightifySceneThread):
    def __init__(self, indigoDevice, logger, sceneName, sceneSleep, lightifyConn, lightifyGroup, sceneArray, lightifyQueue):
        super(RgbRotateSceneThread, self).__init__(indigoDevice, logger, sceneName, sceneSleep, lightifyConn,
                                                   lightifyGroup, lightifyQueue)
        self.sceneArray = sceneArray
        self.lightArray = []
        self.start()

    def startScene(self):
        # start the scene
        self.logger.debug(
            "...start Scene " + self.sceneName + " for group - " + str(self.indigoDevice.name) + ", thread-id=" + str(
                self.name))
        for curLight in self.lightifyGroup.lights():
            theLight = self.lightifyConn.lights()[curLight]
            if theLight is not None:
                self.logger.debug('...start Scene theLight =' + str(theLight) + ', on=' + str(theLight.on()))
                self.lightArray.append(theLight)

    def run(self):
        try:
            self.startScene()
            startIdx = 0
            maxNum = 0
            while not self.stopThread:
                try:
                    # do the scene stuff
                    self.logger.debug("...Scene " + self.sceneName + " group running - " + str(
                        self.indigoDevice.name) + ", thread-id=" + str(self.name))
                    theIdx = startIdx
                    for curLight in self.lightArray:
                        tArr = self.sceneArray[theIdx]
                        rgbArray = [tArr[0], tArr[1], tArr[2]]
                        cTemp = tArr[3]
                        brightness = tArr[4]
                        transMilli = tArr[5]
                        if cTemp != 0:
                            workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                    self.lightifyGroup, curLight,
                                                    False, WorkItemType.CTEMP,
                                                    [255,255,255], cTemp, 0, transMilli)
                        else:
                            workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                    self.lightifyGroup, curLight,
                                                    False, WorkItemType.RGB,
                                                    rgbArray, 0, 0, transMilli)

                        self.lightifyQueue.put(workItem)

                        brightDelta = self.indigoDevice.brightness - float(brightness)
                        if abs(brightDelta) > 1:
                            # next set the brightness
                            workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                        self.lightifyGroup, curLight,
                                                        True, WorkItemType.BRIGHTNESS,
                                                        None, 0, int(brightness), transMilli)
                            self.lightifyQueue.put(workItem)
                        else:
                            self.logger.debug("...RGBROTATE SCENE SKIPPING brightness set for Scene " + self.sceneName + " group running - " + str(
                                self.indigoDevice.name) + ", brightnessDelta=" + str(brightDelta) )

                        theIdx = theIdx + 1
                        if theIdx == len(self.sceneArray):
                            theIdx = 0
                    startIdx = startIdx + 1
                    if startIdx == len(self.sceneArray):
                        startIdx = 0
                    maxNum = maxNum + 1

                    # take a sleep based on the scene preferences
                    time.sleep(self.sceneSleep)
                except:  # Do my other non-socket reading stuff here
                    self.logger.debug(
                        "...Scene group exception - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
                    self.logger.debug(
                        "...Unexpected loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

        except:
            self.logger.debug(
                "...Scene exception hit, process exiting - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
            self.logger.debug("...Unexpected non-loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

        finally:  # Make sure you don't leave any open network connections
            self.stopScene()

# rotates each bulbs in the group thru the different RGBs in the scene - each bulb will will take on the same color
class RgbMatchSceneThread(LightifySceneThread):
    def __init__(self, indigoDevice, logger, sceneName, sceneSleep, lightifyConn, lightifyGroup, sceneArray, lightifyQueue):
        super(RgbMatchSceneThread, self).__init__(indigoDevice, logger, sceneName, sceneSleep, lightifyConn,
                                                  lightifyGroup, lightifyQueue)
        self.sceneArray = sceneArray
        self.lightArray = []
        self.start()

    def startScene(self):
        # start the scene
        self.logger.debug(
            "...start Scene " + self.sceneName + " for group - " + str(self.indigoDevice.name) + ", thread-id=" + str(
                self.name))
        for curLight in self.lightifyGroup.lights():
            theLight = self.lightifyConn.lights()[curLight]
            if theLight is not None:
                self.logger.debug('...start Scene theLight =' + str(theLight) + ', on=' + str(theLight.on()))
                self.lightArray.append(theLight)

    def run(self):
        try:
            self.startScene()
            startIdx = 0
#            maxNum = 0
            while not self.stopThread:
                try:
                    # do the scene stuff
                    theIdx = startIdx
                    tArr = self.sceneArray[theIdx]
                    rgbArray = [tArr[0], tArr[1], tArr[2]]
                    cTemp = tArr[3]
                    brightness = tArr[4]
                    transMilli = tArr[5]
                    self.logger.debug("...Scene " + self.sceneName + " group running - " + str(
                        self.indigoDevice.name) + ", thread-id=" + str(self.name))
                    if cTemp != 0:
                        workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                self.lightifyGroup, None,
                                                True, WorkItemType.CTEMP,
                                                [255,255,255], cTemp, 0, transMilli)
                    else:
                        workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                self.lightifyGroup, None,
                                                True, WorkItemType.RGB,
                                                rgbArray, 0, 0, transMilli)

                    self.lightifyQueue.put(workItem)

                    brightDelta = self.indigoDevice.brightness - float(brightness)
                    if abs(brightDelta) > 1:
                        # next set the brightness
                        workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                    self.lightifyGroup, None,
                                                    True, WorkItemType.BRIGHTNESS,
                                                    None, 0, int(brightness), transMilli)
                        self.lightifyQueue.put(workItem)
                    else:
                        self.logger.debug("...RGBMATCH SCENE SKIPPING brightness set for Scene " + self.sceneName + " group running - " + str(
                            self.indigoDevice.name) + ", brightnessDelta=" + str(brightDelta) )



                    startIdx = startIdx + 1
                    if startIdx == len(self.sceneArray):
                        startIdx = 0
#                    maxNum = maxNum + 1

                    # take a sleep based on the scene preferences
                    time.sleep(self.sceneSleep)
                except:  # Do my other non-socket reading stuff here
                    self.logger.debug(
                        "...Scene group exception - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
                    self.logger.debug(
                        "...Unexpected loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

        except:
            self.logger.debug(
                "...Scene exception hit, process exiting - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
            self.logger.debug("...Unexpected non-loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

        finally:  # Make sure you don't leave any open network connections
            self.stopScene()


class CircadianSceneThread(LightifySceneThread):
    def __init__(self, indigoDevice, logger, sceneName, sceneSleep, lightifyConn, lightifyGroup, sceneArray, lightifyQueue):
        super(CircadianSceneThread, self).__init__(indigoDevice, logger, sceneName, sceneSleep, lightifyConn,
                                                    lightifyGroup, lightifyQueue)
        self.sceneArray = sceneArray
        self.start()

    def run(self):
        try:
            self.startScene()
            while not self.stopThread:
                try:
                    # do the scene stuff
                    circadianVals = self.getCircadian()
                    # get an updated copy of the indigoDevice
                    newIndigoDevice = indigo.devices[self.indigoDevice.id]
                    if newIndigoDevice is not None:
                        self.indigoDevice = newIndigoDevice
                        self.logger.debug("...CIRCAUTO Scene " + self.sceneName + " group running - " +
                            str(self.indigoDevice.name) + ", thread-id=" + str(self.name) +
                            " - onState=" + str(self.indigoDevice.onState) + ", onOffState=" + str(self.indigoDevice.states['onOffState']) +
                            " - NEW/CUR brightness=" + str(circadianVals[0]) + "/" + str(self.indigoDevice.brightness) +
                            ", ctemp=" + str(circadianVals[1]) + "/" + str(self.indigoDevice.whiteTemperature))

                    if self.indigoDevice.onState is False:
                        self.logger.debug("...CIRCAUTO SKIPPING updates for Scene " + self.sceneName + " group running - " + str(
                            self.indigoDevice.name) + ", onState=False")
                    else:
                        tempDelta = self.indigoDevice.whiteTemperature - float(circadianVals[1])
                        if abs(tempDelta) > 25:
                            workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                        self.lightifyGroup, None,
                                                        True, WorkItemType.CTEMP,
                                                        None, int(circadianVals[1]), 0, 50)
                            self.lightifyQueue.put(workItem)
                        else:
                            self.logger.debug("...CIRCAUTO SKIPPING ctemp set for Scene " + self.sceneName + " group running - " + str(
                                self.indigoDevice.name) + ", tempDelta=" + str(tempDelta))

                        brightDelta = self.indigoDevice.brightness - float(circadianVals[0])
                        if abs(brightDelta) > 1:
                            # next set the brightness
                            workItem = LightifyWorkItem(self.sceneName, self.indigoDevice.name, self.indigoDevice,
                                                        self.lightifyGroup, None,
                                                        True, WorkItemType.BRIGHTNESS,
                                                        None, 0, int(circadianVals[0]), 50)
                            self.lightifyQueue.put(workItem)
                        else:
                            self.logger.debug("...CIRCAUTO SKIPPING brightness set for Scene " + self.sceneName + " group running - " + str(
                                self.indigoDevice.name) + ", brightnessDelta=" + str(brightDelta) )
                except:  # Do my other non-socket reading stuff here
                    self.logger.debug(
                        "...Scene group exception - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
                    self.logger.debug(
                        "...Unexpected loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

                finally:
                    # take a sleep based on the scene preferences
                    time.sleep(self.sceneSleep)

        except:
            self.logger.debug(
                "...Scene exception hit, process exiting - " + str(self.indigoDevice.name) + ", thread-id=" + str(self.name))
            self.logger.debug("...Unexpected non-loop error: - " + str(sys.exc_info()) + ", thread-id=" + str(self.name))

        finally:  # Make sure you don't leave any open network connections
            self.stopScene()

    def getCircadian(self):
        self.logger.debug("getCircadian indigoDevice name: " + self.indigoDevice.name)
        temperatureVals = self.sceneArray[0]
        brightnessVals = self.sceneArray[1]
        self.logger.debug("getCircadian device tempVals : " + str(temperatureVals))
        self.logger.debug("getCircadian device brightnessVals : " + str(brightnessVals))

        returnVals = [0.0, 0]

        gradientValue = self.getCircadianValue(brightnessVals)
        gradientBrightness = round(gradientValue)
        returnVals[0] = gradientBrightness

        gradientValue = self.getCircadianValue(temperatureVals)
        gradientTemp = round(gradientValue)
        returnVals[1] = gradientTemp

        self.logger.debug("...getCircadian brightness=" + str(gradientBrightness) + ", temperature=" + str(gradientTemp))

        return returnVals

    ########################################
    def getCircadianValue(self, gradientVals=None):
        rightNow = indigo.server.getTime().date()
        sunriseTime = indigo.server.calculateSunrise(rightNow)
        sunsetTime = indigo.server.calculateSunset(rightNow)
        self.logger.debug("getCircadian gradientVals : " + str(gradientVals))
        self.logger.debug("getCircadian sunrise : " + str(sunriseTime) + ", sunset : " + str(sunsetTime))

        sunriseHr = sunriseTime.hour
        if sunriseTime.minute > 30:
            sunriseHr = sunriseHr + 1
        sunsetHr = sunsetTime.hour
        if sunsetTime.minute > 30:
            sunsetHr = sunsetHr + 1
        peakHrs = round(abs(sunsetHr - sunriseHr) * 0.5)
        stopRiseHr = sunriseHr + round(peakHrs * 0.5) + 2
        fastRiseHr = sunriseHr + 1 + round((stopRiseHr - sunriseHr) * 0.75)
        startFallHr = sunsetHr - round(peakHrs * 0.5)
        if round(fastRiseHr) == round(stopRiseHr):
            fastRiseHr = stopRiseHr - 1

        self.logger.debug(
            "getCircadian sunriseHr : " + str(sunriseHr) + ", sunsetHr : " + str(sunsetHr) + ", peakHrs=" + str(
                peakHrs) + ", fastRiseHr=" + str(fastRiseHr) + ", stopRiseHr=" + str(
                stopRiseHr) + ", startFallHr=" + str(startFallHr))

        currentDate = datetime.datetime.now()
        hourOfDay = currentDate.hour
        minOfHour = currentDate.minute
        gradientValue = 0.0
        if gradientVals == None:
            gradientVals = '15,35,80,95,100,80,40'

        self.logger.debug("getCircadian gradientVals : " + str(gradientVals))
        tempArray = gradientVals.split(",")

        lateNightVal = int(tempArray[0])
        sunrisePreVal = int(tempArray[1])
        sunrisePeakVal = int(tempArray[2])
        amFastPeakVal = int(tempArray[3])
        maxVal = int(tempArray[4])
        pmDropVal = int(tempArray[5])
        sunsetFastDropVal = int(tempArray[6])

        if hourOfDay >= 0 and hourOfDay < (sunriseHr - 1):
            gradientValue = lateNightVal
        elif hourOfDay >= (sunriseHr - 1) and hourOfDay < sunriseHr:
            gradientValue = self.getGradientValue((sunriseHr - 1), sunriseHr, lateNightVal, sunrisePreVal, hourOfDay,
                                                  minOfHour)
        elif hourOfDay >= sunriseHr and hourOfDay < (sunriseHr + 1):
            gradientValue = self.getGradientValue(sunriseHr, (sunriseHr + 1), sunrisePreVal, sunrisePeakVal, hourOfDay,
                                                  minOfHour)
        elif hourOfDay >= (sunriseHr + 1) and hourOfDay < fastRiseHr:
            gradientValue = self.getGradientValue((sunriseHr + 1), fastRiseHr, sunrisePeakVal, amFastPeakVal, hourOfDay,
                                                  minOfHour)
        elif hourOfDay >= fastRiseHr and hourOfDay < stopRiseHr:
            gradientValue = self.getGradientValue(fastRiseHr, stopRiseHr, amFastPeakVal, maxVal, hourOfDay, minOfHour)
        elif hourOfDay >= stopRiseHr and hourOfDay < startFallHr:
            gradientValue = maxVal
        elif hourOfDay >= startFallHr and hourOfDay < (sunsetHr - 1):
            gradientValue = self.getGradientValue(startFallHr, (sunsetHr - 1), maxVal, pmDropVal, hourOfDay, minOfHour)
        elif hourOfDay >= (sunsetHr - 1) and hourOfDay < (sunsetHr + 1):
            gradientValue = self.getGradientValue((sunsetHr - 1), (sunsetHr + 1), pmDropVal, sunsetFastDropVal,
                                                  hourOfDay, minOfHour)
        elif hourOfDay >= (sunsetHr + 1) and hourOfDay < 24:
            gradientValue = self.getGradientValue((sunsetHr + 1), 24, sunsetFastDropVal, lateNightVal, hourOfDay,
                                                  minOfHour)

        return gradientValue

    ########################################
    def getGradientValue(self, startHr, stopHr, startVal, stopVal, curHr, curMin):

        gradientVal = startVal;
        self.logger.debug("...getGradientValue startHr=" + str(startHr) + ", stopHr=" + str(stopHr) + ", startVal=" + str(
            startVal) + ", stopVal=" + str(stopVal) + ", curHr=" + str(curHr) + ", curMin=" + str(curMin))

        totalMin = (stopHr - startHr) * 60
        self.logger.debug("...getGradientValue totalMin=" + str(totalMin))

        if curHr >= startHr and curHr < stopHr:
            minFromStart = ((curHr - startHr) * 60) + curMin
            curPercentage = float(minFromStart) / float(totalMin)

            self.logger.debug("...getGradientValue minFromStart=" + str(minFromStart) + ", totalMin=" + str(
                totalMin) + ", percentage of interval=" + str(curPercentage))

            if startVal < stopVal:
                # // gradientVal is rising
                gradientVal = round(startVal + (curPercentage * (stopVal - startVal)))
                self.logger.debug("...getGradientValue rising, new value=" + str(gradientVal))
            else:
                # // gradientVal is falling
                gradientVal = round(startVal - (curPercentage * (startVal - stopVal)))
                self.logger.debug("...getGradientValue falling, new value=" + str(gradientVal))

        return gradientVal


class LightifyWorkItem(object):
    def __init__(self, scene_name, group_name, the_device, the_group, the_light, is_group_work, work_item_type,
                 rgb_values, color_temp, brightness, transition_millis):
        self.sceneName = scene_name
        self.groupName = group_name
        self.indigoDevice = the_device
        self.theGroup = the_group
        self.theLight = the_light
        self.isGroupWork = is_group_work
        self.workItemType = work_item_type
        self.rgbValues = rgb_values
        self.colorTemp = color_temp
        self.brightness = brightness
        self.transitionMillis = transition_millis

class WorkItemType(enum.Enum):
    RGB = 1
    CTEMP = 2
    BRIGHTNESS = 3
    ONOFF = 4

class LightifyAction(object):
    def __init__(self):
        self.deviceAction = None
        self.actionValue = None
        self.delayAmount = 900
        self.deviceId = None
        self.configured = True
        self.textToSpeak = None

