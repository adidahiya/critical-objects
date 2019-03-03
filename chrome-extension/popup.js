/**
 * Popup script
 */

let reloadButton = document.getElementById('reload');
reloadButton.onclick = () => {
    chrome.runtime.reload();
};

let muteButton = document.getElementById("mute");
muteButton.onclick = () => {
    const { mute } = chrome.storage.local.get("mute");
    muteButton.textContent = mute ? "unmute" : "mute";
    chrome.storage.local.set({
        mute: !mute,
    });
};
