/**
 * Background script for chrome extension
 */

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

    main();
});

chrome.webNavigation.onCompleted.addListener(() => {
    console.log("web navigation");
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    console.log("tab updated", changeInfo.url);
});

function main() {
    const ARDUINO_PORT_NAME = "/dev/cu.usbmodem14101";
    const serial = new SerialPort();

    console.log("Opening serial connection...");
    openSerialConnection();

    function openSerialConnection() {
        serial.open(ARDUINO_PORT_NAME);
    }

    function closeSerialConnection() {
        serial.close();
    }

    function bindSerialEventHandlers() {
        serial.on("connected", () => console.log("connected"));
        serial.on("open", () => {
            console.log("opened");
            serial.write(`website:foobar`)
        });
        serial.on("data", handleSerialData);
        serial.on("error", (err) => console.log("error", err));
        serial.on("close", () => console.log("closed"));
    }

    function handleSerialData() {
        const data = serial.readLine();
        console.log("Data....", data);
    }
}
