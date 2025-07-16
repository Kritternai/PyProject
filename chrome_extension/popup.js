document.addEventListener('DOMContentLoaded', function() {
    const syncGoogleClassroomBtn = document.getElementById('syncGoogleClassroom');
    const syncMSTeamsBtn = document.getElementById('syncMSTeams');
    const statusDiv = document.getElementById('status');

    function showStatus(message) {
        statusDiv.textContent = message;
    }

    syncGoogleClassroomBtn.addEventListener('click', function() {
        showStatus('Syncing Google Classroom...');
        chrome.runtime.sendMessage({ action: 'syncGoogleClassroom' }, function(response) {
            showStatus(response.status);
        });
    });

    syncMSTeamsBtn.addEventListener('click', function() {
        showStatus('Syncing MS Teams...');
        chrome.runtime.sendMessage({ action: 'syncMSTeams' }, function(response) {
            showStatus(response.status);
        });
    });
});
