/**
 * Popup script
 */

let reloadButton = document.getElementById('reload');
reloadButton.onclick = () => {
    chrome.runtime.reload();
};
