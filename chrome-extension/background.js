/**
 * Background script for chrome extension
 */

const ARDUINO_PORT_NAME = "/dev/cu.usbmodem14101";
let serial;
// SerialPort#isConnected() isn't very reliable, just track the state ourselves for now
let isConnected = false;

// other random state, should be better encapsulated

/** @type {String} */
let lastTabNavigation;

/** @type {String} good, ok, bad */
let humanBehaviorState = "good";

chrome.runtime.onInstalled.addListener(() => {
    chrome.declarativeContent.onPageChanged.removeRules(undefined, function () {
        chrome.declarativeContent.onPageChanged.addRules([
            // on developer.chrome.com pages, show the extension's icon in the chrome menu bar in the top right
            {
                conditions: [
                    new chrome.declarativeContent.PageStateMatcher({
                        pageUrl: {
                            hostEquals: 'developer.chrome.com'
                        },
                    }),
                ],
                actions: [
                    new chrome.declarativeContent.ShowPageAction(),
                ],
            },
        ]);
    });
});

// report behavior to Arduino every second
setInterval(() => {
    openSerialConnection(() => {
        serial.write(`humanBehaviorState:${humanBehaviorState}`);
    });
}, 1000);

chrome.webNavigation.onCompleted.addListener(() => {
    console.log("web navigation");
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url !== undefined) {
        console.log("tab updated", changeInfo.url);
        lastTabNavigation = changeInfo.url;

        if (isGoodWebsite()) {
            humanBehaviorState = "good";
        } else {
            humanBehaviorState = "bad";
        }
    }
});

function isGoodWebsite() {
    const s = lastTabNavigation;
    return s.startsWith("https://www.facebook")
        || s.startsWith("https://www.instagram")
        || s.startsWith("https://web.whatsapp");
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
        console.log("connected");
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
