/**
 * Background script for chrome extension
 */

///<reference path="node_modules/@types/chrome/index.d.ts">

const ARDUINO_PORT_NAME = "/dev/cu.usbmodem14201";
// const ARDUINO_PORT_NAME = "/dev/cu.usbserial-1410";
let serial;
// SerialPort#isConnected() isn't very reliable, just track the state ourselves for now
let isConnected = false;
let synth;

// only stores tabs that have completed loading their URLs
const activeTab = {
    /** @type {Number} */
    id: undefined,
    /** @type {String} */
    urlOrigin: undefined,
    inSurveillanceNetwork: false,
};

/**
 * Keeps track of which domains are within the surveillance network
 * @type {Set.<string>}
 */
const surveillanceDomains = new Set();

/** @type {"punishment" | "reward" | undefined} */
let conditioningState;
let isPunishmentActive = false;
let punishmentStartedTime = 0;

chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.set({
        mute: false,
    });

    chrome.tabs.query({ active: true }, (tabs) => {
        if (tabs.length > 0) {
            updateActiveTab(tabs[0].id, tabs[0].url);
        }
    });
});

// report behavior to Arduino every second
let lastInSurveillanceNetwork = false;
setInterval(() => {
    const { inSurveillanceNetwork } = activeTab;

    if (lastInSurveillanceNetwork && !inSurveillanceNetwork) {
        // just left the network
        console.log("bad human! punishment is required");
        conditioningState = "punishment";
        openSerialConnection(() => serial.write(conditioningState));
    } else if (!lastInSurveillanceNetwork && inSurveillanceNetwork) {
        // back in network
        console.log("nice job, here's some candy");
        conditioningState = "reward";
        openSerialConnection(() => serial.write(conditioningState));
    }

    lastInSurveillanceNetwork = inSurveillanceNetwork;

    chrome.storage.local.get("mute", ({ mute }) => {
        if (!mute) {
            playStatusBeep();
        }
    });
}, 1000);

// typically used to block or redirect requests, but we use this event to inspect if the right resources
// (analytics and tracking pixels) are about to be requested for the active page
chrome.webRequest.onBeforeRequest.addListener(
    ({ initiator }) => {
        // got a tracking request, log this initiator as part of the surveillance network
        if (initiator !== undefined) {
            surveillanceDomains.add(initiator);
            if (initiator === activeTab.urlOrigin) {
                activeTab.inSurveillanceNetwork = true;
            }
        }
    },
    {
        urls: [
            "*://www.facebook.com/tr*",
        ],
        types: ["main_frame", "sub_frame", "script", "image", "xmlhttprequest"]
    },
);

// https://developer.chrome.com/extensions/tabs#event-onUpdated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (!tab.active) {
        return;
    }

    if (changeInfo.url !== undefined) {
        updateActiveTab(tabId, changeInfo.url);
    }
});

// https://developer.chrome.com/extensions/tabs#event-onActivated
chrome.tabs.onActivated.addListener(({ tabId }) => {
    chrome.tabs.get(tabId, (tab) => {
        updateActiveTab(tabId, tab.url);
    });
});

chrome.webNavigation.onCommitted.addListener(({ tabId, url, frameId }) => {
    // ignore subframes
    if (frameId > 0) {
        return;
    }

    // we only care about navigation in the active tab, since inactive tabs will have their urls queried
    // upon tabs.onActivated
    if (tabId === activeTab.id) {
        updateActiveTab(tabId, withoutTrailingSlash(url));
    }
});

function updateActiveTab(tabId,  url) {
    if (url === undefined || url.startsWith("chrome://") || url.startsWith("chrome-extension://")) {
        return;
    }

    const urlOrigin = getUrlOrigin(url);

    if (activeTab.id === tabId && activeTab.urlOrigin === urlOrigin) {
        return;
    }

    activeTab.id = tabId;
    activeTab.urlOrigin = urlOrigin;
    activeTab.inSurveillanceNetwork = surveillanceDomains.has(urlOrigin) || isFacebookDomain(urlOrigin);
    console.log("active tab updated", activeTab);
}

/** N.B. this is a pretty slow way to do this */
function getUrlOrigin(/** @type {String} */ url) {
    const tmpAnchor = document.createElement("a");
    tmpAnchor.href = url;
    return tmpAnchor.origin;
}

function playStatusBeep() {
    if (synth === undefined) {
        // @ts-ignore
        synth = new Tone.Synth().toMaster();
    }

    // 3000 hz is an annoying tone
    if (conditioningState === "punishment") {
        if (isPunishmentActive) {
            // continue
        } else {
            isPunishmentActive = true;
            punishmentStartedTime = Date.now();
            // -20db is pretty quiet
            Tone.Master.volume.value = -100;
            synth.triggerAttack(3000);
            // ramp to full volume over one minute
            Tone.Master.volume.linearRampToValueAtTime(0, 60);
        }
    } else {
        if (isPunishmentActive) {
            isPunishmentActive = false;
            synth.triggerRelease();
        }
    }
}

function isFacebookDomain(/** @type {String} */ url) {
    return url.startsWith("https://www.facebook")
        || url.startsWith("https://www.instagram")
        || url.startsWith("https://web.whatsapp");
}

function openSerialConnection(callback) {
    if (serial === undefined) {
        // @ts-ignore
        serial = new SerialPort();
        bindSerialEventHandlers();
    }

    if (isConnected) {
        callback();
    } else {
        console.log("Opening serial connection...");
        serial.open(ARDUINO_PORT_NAME);
        serial.on("open", () => callback());
    }
}

function closeSerialConnection() {
    serial.close();
}

function bindSerialEventHandlers() {
    serial.on("connected", () => {
        isConnected = true;
    });
    serial.on("open", () => {
        isConnected = true;
    });
    serial.on("data", handleSerialData);
    serial.on("error", (err) => {
        if (err === undefined || err === "Already open") {
            return;
        }
        console.log("error", err);
    });
    serial.on("close", () => {
        console.log("closed");
    });
}

function handleSerialData() {
    const data = serial.readLine();
    if (data !== undefined && data.trim() !== "") {
        console.log("Headset says:", data);
    }
}

function withoutTrailingSlash(/** @type {String} */ str) {
    if (str === undefined || str === "" || str[str.length - 1] !== "/") {
        return;
    }

    return str.substr(str.length - 1);
}
