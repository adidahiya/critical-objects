/**
 * Background script for chrome extension
 */

const ARDUINO_PORT_NAME = "/dev/cu.usbmodem14201";
// const ARDUINO_PORT_NAME = "/dev/cu.usbserial-1410";
let serial;
// SerialPort#isConnected() isn't very reliable, just track the state ourselves for now
let isConnected = false;
let synth;

// only stores tabs that have completed loading their URLs
let activeTab = {
    /** @type {Number} */
    id: undefined,
    /** @type {String} */
    url: undefined,
}

/** @type {String} good, ok, bad */
let humanBehaviorState = "good";

chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.set({
        mute: false,
    });
});

// report behavior to Arduino every second
setInterval(() => {
    openSerialConnection(() => {
        serial.write(`humanBehaviorState:${humanBehaviorState}`);
    });

    chrome.storage.local.get("mute", ({ mute }) => {
        if (!mute) {
            playStatusBeep();
        }
    });
}, 1000);

// typically used to block or redirect requests, but we use this event to inspect if the right resources
// (analytics and tracking pixels) are about to be requested for the active page
// chrome.webRequest.onBeforeRequest.addListener(() => {
// });

// https://developer.chrome.com/extensions/tabs#event-onUpdated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (!tab.active) {
        return;
    }

    if (changeInfo.url !== undefined && changeInfo.status === "complete") {
        console.log("active tab completed loading", changeInfo.url);
        updateActiveTab(tabId, changeInfo.url);

        if (isGoodWebsite()) {
            if (humanBehaviorState === "bad") {
                console.log("Nice job, keep browsing facebook");
            }
            humanBehaviorState = "good";
        } else {
            if (humanBehaviorState === "good") {
                console.log("Bad human!");
            }
            humanBehaviorState = "bad";
        }
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
        updateActiveTab(tabId, url);
    }
});

function updateActiveTab(tabId,  url) {
    if (activeTab.id === tabId && activeTab.url === url) {
        return;
    }

    if (url.startsWith("chrome://")) {
        return;
    }

    console.log("active tab updated", tabId, url);
    activeTab.id = tabId;
    activeTab.url = url
}

function playStatusBeep() {
    if (synth === undefined) {
        synth = new Tone.Synth().toMaster();
    }

    // TODO: sound torture
    if (humanBehaviorState !== "good") {
        synth.triggerAttackRelease("C4", "16n");
    }
}

function isGoodWebsite() {
    const { url } = activeTab;
    return url.startsWith("https://www.facebook")
        || url.startsWith("https://www.instagram")
        || url.startsWith("https://web.whatsapp");
}

function openSerialConnection(callback) {
    if (serial === undefined) {
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
        if (err === "Already open") {
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
