export let toggleCheck = window.toggleCheck
export let $ = window.$;
export let getStateZip = window.getStateZip
export let init = window.init;
export let win = window;
export let openItemsBroadcastView = window.openItemsBroadcastView;
export let openMapBroadcastView = window.openMapBroadcastView;
export let closeAllTooltips = window.closeAllTooltips;
export let removeNodes = window.removeNodes;
export let drawNodes = window.drawNodes;
export let resetSession = window.resetSession;
export let saveQuickSettings = window.saveQuickSettings;
export let saveSettings = window.saveSettings;
export let resetColors = window.resetColors;
export let getFile = window.getFile;
export let importState = window.importState;
export let importLogicDiff = window.importLogicDiff;
export let openExportStateDialog = window.openExportStateDialog;
export let resetUndoRedo = window.resetUndoRedo;
export let fixArgs = window.fixArgs;
export let saveSettingsToStorage = window.saveSettingsToStorage;
export let applySettings = window.applySettings;
export let refreshItems = window.refreshItems;
export let broadcastArgs = window.broadcastArgs;
export let toggleSingleNodeCheck = window.toggleSingleNodeCheck;
export let openCheckLogicViewer = window.openCheckLogicViewer;
export let nodes = window.nodes;
export let setCheckContents = window.setCheckContents;
export let spoilLocation = window.spoilLocation;
export let itemsByLocation = window.itemsByLocation;
export let getPopperConfig = window.getPopperConfig;
export let startHouse = window.startHouse;
export let Entrance = window.Entrance;
export let setStartLocation = window.setStartLocation;
export let canBeStart = window.canBeStart;
export let startGraphicalConnection = window.startGraphicalConnection;
export let getInsideOutEntrance = window.getInsideOutEntrance;
export let connectEntrances = window.connectEntrances;
export let startIsSet = window.startIsSet;
export let openDeadEndDialog = window.openDeadEndDialog;
export let inOutEntrances = window.inOutEntrances;

export function initGlobals(data) {
    window.defaultArgs = data.args;
    window.defaultSettings = data.defaultSettings;
    window.settingsOverrides = data.jsonSettingsOverrides;
    window.argsOverrides = data.jsonArgsOverrides;
    window.diskSettings = data.diskSettings;

    window.iconStyles = $('link#iconsSheet')[0].sheet;
    window.themeStyles = $('link#themeSheet')[0].sheet;

    window.local = Boolean(data.local);
    window.allowAutotracking = Boolean(data.allowAutotracking);
    window.allowMap = Boolean(data.allowMap);
    window.refreshMap = data.refreshMap !== false;
    window.allowItems = Boolean(data.allowItems);
    window.keepQueryArgs = Boolean(data.keepQueryArgs);
    window.settingsPrefix = data.settingsPrefix;
    window.players = data.players;
    window.broadcastMode = data.broadcastMode;
    window.rootPrefix = import.meta.env.VITE_API_URL;
    itemsByLocation = window.itemsByLocation;
}