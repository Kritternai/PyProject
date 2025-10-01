document.addEventListener('DOMContentLoaded', function() {
    const syncMSTeamsBtn = document.getElementById('syncMSTeams');
    const syncKMITLStudyTableBtn = document.getElementById('syncKMITLStudyTable');
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

    syncKMITLStudyTableBtn.addEventListener('click', function() {
        showStatus('Syncing KMITL Study Table...');
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const activeTab = tabs[0];
            if (activeTab.url.includes('https://www.reg.kmitl.ac.th/u_student/report_studytable_show.php')) {
                chrome.scripting.executeScript({
                    target: { tabId: activeTab.id },
                    files: ['content_scripts/kmitl_studytable.js']
                }, () => {
                    showStatus('KMITL Study Table sync initiated.');
                });
            } else {
                showStatus('Please navigate to KMITL Study Table page.');
            }
        });
    });
});