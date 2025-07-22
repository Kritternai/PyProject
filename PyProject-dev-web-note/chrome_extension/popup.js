document.addEventListener('DOMContentLoaded', function() {
    const syncMSTeamsBtn = document.getElementById('syncMSTeams');
    const statusDiv = document.getElementById('status');

    function showStatus(message) {
        statusDiv.textContent = message;
    }

    syncMSTeamsBtn.addEventListener('click', function() {
        showStatus('Syncing MS Teams...');
        chrome.runtime.sendMessage({ action: 'syncMSTeams' }, function(response) {
            showStatus(response.status);
        });
    });
});