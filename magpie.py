import os
import base64
import argparse
import traceback
import jsonpickle
from flaskwebgui import FlaskUI
from flask import Flask, render_template, request
from jinja2 import Template
from datetime import datetime

from ladxrInterface import *

app = Flask(__name__)
app.jinja_options['trim_blocks'] = True
app.jinja_options['lstrip_blocks'] = True

local = False
width = 500
height = 500

class FakeLogic:
    pass

class Accessibility:
    def __init__(self, checks, entrances):
        self.checks = checks
        self.entrances = entrances

class LocalSettings:
    def __init__(self):
        self.checkSize = 32
        self.mapBrightness = 50
        self.showOutOfLogic = False
        self.animateChecks = True
        self.swapMouseButtons = False
        self.swapItemsAndMap = False
        self.hideChecked = False
        self.ignoreHigherLogic = False
        self.hideVanilla = False
        self.dungeonItemsTemplate = 'default.html'
        self.itemsTemplate = 'default.html'
        self.customDungeonItems = None
        self.customItems = None
        self.showDungeonItemCount = False
        self.showItemsOnly = False
        self.highlightItemsOnHover = True
        self.enableAutotracking = False
        self.autotrackItems = True
        self.autotrackChecks = True
        self.autotrackEntrances = True
        self.autotrackSettings = True
        self.autotrackSpoilers = True
        self.autotrackGraphicsPack = True
        self.autotrackerAddress = ''
        self.gps = True
        self.followMap = True
        self.linkFace = True
        self.spoilOnCollect = False
        self.showOwnedPickups = False
        self.graphicsPack = ''

        self.diff0Color = '#0066ff'
        self.diff0VColor = '#ffffff'
        self.diff1Color = '#ffff00'
        self.diff1VColor = '#ffffff'
        self.diff2Color = '#ff8800'
        self.diff2VColor = '#ffffff'
        self.diff3Color = '#ff0000'
        self.diff3VColor = '#ffffff'
        self.diff8Color = '#0066ff'
        self.diff8VColor = '#ffffff'
        self.diff9Color = '#444444'
        self.diff9VColor = '#aaaaaa'
        self.diffCheckedColor = '#00ff00'
        self.colorAssistMaps = False

@app.route("/")
def home():
    args = getArgs()
    defaultSettings = LocalSettings()

    flags = args.flags
    args.flags = []
    settingsOverrides = {}
    argsOverrides = {}

    if request.args.get('enable_autotracking'):
        settingsOverrides['enableAutotracking'] = True

    shortString = request.args.get('shortString') 
    if shortString:
        tempArgs = getArgsFromShortString(shortString)
        del tempArgs.flags
        argsOverrides = tempArgs.__dict__
    
    settingsPrefix = 'setting_'
    argsPrefix = 'flag_'
    for arg, value in request.args.items():
        if arg.startswith(settingsPrefix):
            settingsOverrides[arg[len(settingsPrefix):]] = value
        if arg.startswith(argsPrefix):
            argsOverrides[arg[len(argsPrefix):]] = value

    return render_template("index.html", flags=flags, args=args,
                                         defaultSettings=defaultSettings,
                                         jsonArgs=jsonpickle.encode(args),
                                         jsonSettings=jsonpickle.encode(defaultSettings),
                                         jsonSettingsOverrides=jsonpickle.encode(settingsOverrides),
                                         jsonArgsOverrides=jsonpickle.encode(argsOverrides),
                                         local=local,
                                         graphicsOptions=getGraphicsPacks(),
                                         version=getVersion(),
                                         )

@app.route("/items", methods=['POST'])
def renderItems():
    try:
        args = parseArgs(request.form['args'])
        localSettings = parseLocalSettings(request.form['localSettings'])
        allItems = getItems(args)

        initChecks(args)

        if localSettings.showDungeonItemCount:
            dungeonItemCount = getDungeonItemCount(args)

            for item in dungeonItemCount:
                allItems[item] = dungeonItemCount[item]

        customItems = None
        customDungeonItems = None

        if localSettings.itemsTemplate == 'custom':
            if localSettings.customItems == None:
                localSettings.itemsTemplate = 'default.html'
            else:
                customItems = Template(localSettings.customItems)

        if localSettings.dungeonItemsTemplate == 'custom':
            if localSettings.customDungeonItems == None:
                localSettings.dungeonItemsTemplate = 'default.html'
            else:
                customDungeonItems = Template(localSettings.customDungeonItems)

        result = render_template('items.html', allItems=allItems,
                                               args=args,
                                               localSettings=localSettings,
                                               customItems=customItems,
                                               customDungeonItems=customDungeonItems,
                                               local=local,
                                               )

        return result
    except:
        return renderTraceback()

@app.route("/shortString", methods=['POST'])
def parseShortString():
    try:
        shortString = request.form['shortString']
        settings = getArgsFromShortString(shortString)

        return jsonpickle.encode(settings)
    except:
        return renderTraceback()

@app.route("/spoilerLog", methods=['POST'])
def getSpoilerLog():
    try:
        romData = base64.b64decode(request.form['romData'])
        return loadSpoilerLog(romData)
    except:
        return renderTraceback()

@app.route("/checkList", methods=['POST'])
def renderCheckList():
    try:
        argValues = parseArgs(request.form['args'])
        inventory = jsonpickle.decode(request.form['inventory'])
        entranceMap = jsonpickle.decode(request.form['entranceMap'])
        bossList = jsonpickle.decode(request.form['bossList'])
        minibossMap = jsonpickle.decode(request.form['minibossMap'])

        for key in list(minibossMap.keys()):
            if key.isnumeric():
                minibossMap[int(key)] = minibossMap[key]
                del minibossMap[key]

        args = getArgs(values=argValues)
        initChecks(args)

        addStartingItems(inventory, args)

        entrances = getEntrancePool(args)
        if args.randomstartlocation and args.entranceshuffle == 'none':
            entrances = entrances.union(set(getStartLocations(args)))

        cleanUpEntranceMap(entranceMap, entrances, args)

        entrances = list(entrances)
        allItems = getAllItems(args)
        logics = getLogics(args, entranceMap, bossList, minibossMap)
        allChecks = loadChecks(getLogicWithoutER(args), allItems)
        accessibility = getAccessibility(allChecks, entrances, logics, inventory)

        result = render_template("checklist.html", checkAccessibility=accessibility.checks,
                                                 entranceAccessibility=jsonpickle.encode(accessibility.entrances),
                                                 logics=logics,
                                                 checkCount=len(allChecks),
                                                 entrances=jsonpickle.encode(entrances),
                                                 startLocations=jsonpickle.encode(getStartLocations(args)),
                                                 )

        return result
    except:
        return renderTraceback()

@app.route("/mapCoords")
def mapCoords():
    return render_template("mapCoords.html")

@app.route("/suggestion", methods=['POST'])
def suggestion():
    from subprocess import Popen, PIPE
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText

    subject = 'New Magpie Suggestion'
    emailFrom = 'MagpieSuggestions'
    emailTo = 'root'

    try:
        email = request.form['email']
        body = request.form['body']
        state = request.form['state']

        if '<img' in body:
            subject += ' (with images)'

        html = MIMEText(f'<p>New Magpie suggestion from "{email}:"</p>' + body, 'html')
        alternative = MIMEMultipart('alternative')
        alternative.attach(html)

        attachment = MIMEText(state)
        attachment.add_header('Content-Disposition', 'attachment', filename=f'{datetime.now()}-magpie-state.json')

        htmlFile = MIMEText(body)
        htmlFile.add_header('Content-Disposition', 'attachment', filename=f'{datetime.now()}-magpie-suggestion.html')

        msg = MIMEMultipart('mixed')
        msg.attach(alternative)
        msg.attach(attachment)
        msg.attach(htmlFile)
        msg['Subject'] = subject
        msg['From'] = emailFrom
        msg['To'] = emailTo
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        p.communicate(msg.as_bytes())
    except:
        print(traceback.format_exc())

    response = app.response_class(
        response="thx",
        status=200,
        mimetype='application/json'
    )

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

def getVersion():
    try:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'version')
        with open(path, 'r') as reader:
            return reader.read()
    except:
        return 'unknown'

def parseArgs(argsString):
    args = jsonpickle.decode(argsString)

    if args.goal == 'egg':
        args.goal = '8'

    return args

def parseLocalSettings(settingsString):
    localSettings = jsonpickle.decode(settingsString)

    return localSettings

def getAccessibility(allChecks, allEntrances, logics, inventory):
    normalLogics = []
    trackerLogic = None

    for log in logics:
        if log.name == 'tracker':
            trackerLogic = log
        else:
            normalLogics.append(log)

    checkAccessibility = getCheckAccessibility(allChecks, normalLogics, trackerLogic, inventory)
    entranceAccessibility = getEntranceAccessibility(allEntrances, normalLogics, inventory)

    return Accessibility(checkAccessibility, entranceAccessibility)

def getCheckAccessibility(allChecks, logics, trackerLogic, inventory):
    accessibility = {}

    outOfLogic = set(allChecks)

    # Initialize each logic level with their full list of accessible Check objects
    for i in range(len(logics)):
        logic = logics[i]
        
        accessibility[logic] = set(loadChecks(logic, inventory))
        outOfLogic = outOfLogic.difference(accessibility[logic])

    accessibility[trackerLogic] = set(loadChecks(trackerLogic, inventory))
    outOfLogic = outOfLogic.difference(accessibility[trackerLogic])
    
    # Remove duplicate checks from higher logic levels
    for i in range(1, len(logics)):
        for j in range(i):
            accessibility[logics[i]] = accessibility[logics[i]].difference(accessibility[logics[j]])

    accessibility[trackerLogic] = accessibility[trackerLogic].difference(accessibility[logics[0]])
        
    inventory['KEY1'] = 9
    inventory['KEY2'] = 9
    inventory['KEY3'] = 9
    inventory['KEY4'] = 9
    inventory['KEY5'] = 9
    inventory['KEY6'] = 9
    inventory['KEY7'] = 9
    inventory['KEY8'] = 9
    inventory['KEY9'] = 9

    # Find more checks that are behind small keys
    alreadyInKeyLogic = set()
    for i in range(len(logics)):
        level = accessibility[logics[i]]
        checksBehindKeys = set(loadChecks(logics[i], inventory)).difference(level)

        for j in range(i):
            checksBehindKeys = checksBehindKeys.difference(accessibility[logics[j]])
        
        for check in checksBehindKeys:
            if check in alreadyInKeyLogic:
                continue

            alreadyInKeyLogic.add(check)
            level.add(check.cloneBehindKeys())

        # Assign difficulties to each logic level (not just key locked)
        logics[i].difficulty = i
        for check in level:
            check.difficulty = i

    for check in accessibility[trackerLogic]:
        check.difficulty = 8

    trackerLogic.difficulty = 8
    trackerLogic.friendlyName = 'In tracker logic'

    outOfLogic = outOfLogic.difference(alreadyInKeyLogic)
    outOfLogic = sorted(outOfLogic, key=lambda x: (x.area, x.name))

    accessibility[logics[0]] = sorted(accessibility[logics[0]], key=lambda x: (x.area, x.name))
    logics[0].friendlyName = 'In logic'

    for check in outOfLogic:
        check.difficulty = 9 

    for i in range(1, len(logics)):
        logics[i].friendlyName = f'In {logics[i].name} logic'

        accessibility[logics[i]] = sorted(accessibility[logics[i]], key=lambda x: (x.area, x.name))
    
    oolLogic = FakeLogic()
    oolLogic.friendlyName = 'Out of logic'
    oolLogic.difficulty = 9
    accessibility[oolLogic] = outOfLogic

    return accessibility

def getEntranceAccessibility(allEntrances, logics, inventory):
    accessibility = {}
    entrances = {}

    outOfLogic = set(allEntrances)

    # Initialize each logic level with their full list of accessible entrance IDs
    for i in range(len(logics)):
        logic = logics[i]
        
        accessibility[logic] = set(loadEntrances(logic, inventory))
        outOfLogic = outOfLogic.difference(accessibility[logics[i]])
    
    # Remove duplicate entrances from higher logic levels
    for i in range(1, len(logics)):
        for j in range(i):
            accessibility[logics[i]] = accessibility[logics[i]].difference(accessibility[logics[j]])
    
    # Convert the entrance IDs to Entrance objects
    for i in range(len(logics)):
        for name in accessibility[logics[i]]:
            entrance = Entrance(name, i)
            entrances[name] = entrance

    for name in outOfLogic:
        entrances[name] = Entrance(name, 9)

    return entrances

def addStartingItems(inventory, args):
    inventory['RUPEES_500'] = 10

    if args.bowwow != 'normal':
        inventory['SWORD'] = inventory['SWORD'] + 1

    if args.dungeon_items == 'keysy':
        for i in range(9):
            for amount, item_name in ((9, "KEY"), (1, "NIGHTMARE_KEY")):
                item_name = f"{item_name}{i + 1}"
                inventory[item_name] = amount
    
    if args.owlstatues not in ['both', 'dungeon'] and args.goal not in ['bingo', 'bingo-full']:
        for i in range(9):
            inventory[f"STONE_BEAK{i + 1}"] = 1

def renderTraceback():
    return f"<pre>{traceback.format_exc()}</pre>"

def cleanUpEntranceMap(entranceMap, entrances, args):
    for source, dest in entranceMap.items():
        if dest in {'landfill', 'bk_shop'}:
            entranceMap[source] = 'rooster_house'

    for entrance in list(entranceMap.keys()):
        if entrance not in entrances:
            del entranceMap[entrance]

    if entranceMap == {} and args.randomstartlocation:
        entranceMap['start_house'] = 'rooster_house'

    if not args.randomstartlocation: 
        reverseMap = {value: key for (key, value) in entranceMap.items()}
        if 'start_house' in entranceMap:
            del entranceMap['start_house']
        if 'start_house' in reverseMap:
            del entranceMap[reverseMap['start_house']]

def getGraphicsPacks():
    return ["Subrosian", "Mario", "Rooster", "Rosa", "Kirby", "Martha", "Meme", "Bunny", "Matty_LA", "Bowwow", "Luigi", "Tarin", "AgesGirl", "Marin", "GrandmaUlrira", "Richard", "NESLink", "MarinAlpha"]
    # gfxPath = 'LADXR/gfx/'

    # options = []

    # with os.scandir(gfxPath) as ls:
    #     for entry in ls:
    #         if entry.name.endswith('.bin') and entry.is_file():
    #             options.append(entry.name[:-4])
    
    # return options

if sys.platform.lower().startswith('win'):
    import ctypes

    def hideConsole():
        """
        Hides the console window in GUI mode. Necessary for frozen application, because
        this application support both, command line processing AND GUI mode and theirfor
        cannot be run via pythonw.exe.
        """

        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            # if you wanted to close the handles...
            #ctypes.windll.kernel32.CloseHandle(whnd)

    def showConsole():
        """Unhides console window"""
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', dest='local', action='store_true', help='Start as a local application')
    parser.add_argument('--width', dest='width', action='store', default=500, type=int, help='Local application starting window width')
    parser.add_argument('--height', dest='height', action='store', default=500, type=int, help='Local application starting window height')
    args = parser.parse_args()

    local = args.local

    if args.local:
        # hide console window, but only under Windows and only if app is frozen
        if sys.platform.lower().startswith('win'):
            if getattr(sys, 'frozen', False):
                hideConsole()

        chromePaths = ['%ProgramFiles%\Google\Chrome\Application\chrome.exe',
                       '%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe',
                       '%LocalAppData%\Google\Chrome\Application\chrome.exe']
        
        browserPath = None
        
        for path in chromePaths:
            expanded = os.path.expandvars(path)
            if os.path.exists(expanded):
                browserPath = expanded
                break
        
        ui = FlaskUI(app, port=16114, width=args.width, height=args.height, browser_path=browserPath)
        ui.run()

        if sys.platform.lower().startswith('win'):
            if getattr(sys, 'frozen', False):
                showConsole()
    else:
        app.run()