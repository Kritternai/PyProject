chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'syncGoogleClassroom') {
        // Inject content script into the active tab if it's Google Classroom
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const activeTab = tabs[0];
            if (activeTab.url.includes('classroom.google.com')) {
                chrome.scripting.executeScript({
                    target: { tabId: activeTab.id },
                    files: ['content_scripts/google_classroom.js']
                }, () => {
                    sendResponse({ status: 'Google Classroom sync initiated.' });
                });
            } else {
                sendResponse({ status: 'Please navigate to Google Classroom.' });
            }
        });
        return true; // Indicates that sendResponse will be called asynchronously
    } else if (request.action === 'syncMSTeams') {
        // Inject content script into the active tab if it's MS Teams
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const activeTab = tabs[0];
            if (activeTab.url.includes('teams.microsoft.com')) {
                chrome.scripting.executeScript({
                    target: { tabId: activeTab.id },
                    files: ['content_scripts/ms_teams.js']
                }, () => {
                    sendResponse({ status: 'MS Teams sync initiated.' });
                });
            } else {
                sendResponse({ status: 'Please navigate to Microsoft Teams.' });
            }
        });
        return true; // Indicates that sendResponse will be called asynchronously
    } else if (request.action === 'sendDataToBackend') {
        // This is where the data from content scripts will be sent to your Flask backend
        const data = request.data;
        const platform = request.platform;
        const backendUrl = 'http://127.0.0.1:5000/api/import_data'; // Your Flask API endpoint

        fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
                // Add authentication headers here if needed (e.g., API Key)
            },
            body: JSON.stringify({ platform: platform, data: data })
        })
        .then(response => response.json())
        .then(result => {
            console.log('Data sent to backend:', result);
            sendResponse({ status: `Data sent to backend: ${result.message || 'Success'}` });
        })
        .catch(error => {
            console.error('Error sending data to backend:', error);
            sendResponse({ status: `Error sending data: ${error.message}` });
        });
        return true; // Indicates that sendResponse will be called asynchronously
    }
});
