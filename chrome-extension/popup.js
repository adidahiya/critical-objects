/**
 * Popup script
 */

let changeColorButton = document.getElementById('changeColor');

chrome.storage.sync.get('color', (data) => {
    changeColorButton.style.backgroundColor = data.color;
    changeColorButton.setAttribute('value', data.color);
});

changeColorButton.onclick = (element) => {
    let color = element.target.value;
    chrome.tabs.query({
        active: true,
        currentWindow: true
    }, (tabs) => {
        chrome.tabs.executeScript(
            tabs[0].id,
            {
                code: `document.body.style.backgroundColor = '${color}';`
            },
        );
    });
};

let reloadButton = document.getElementById('reload');
reloadButton.onclick = () => {
    chrome.runtime.reload();
};
