// This script runs on Microsoft Teams pages

(function() {
    console.log('MS Teams content script loaded.');

    const extractedData = {
        teams: []
    };

    // Function to extract team names
    function extractTeams() {
        // Selector for the button containing the team name, using data-testid for better stability
        const teamNameButtons = document.querySelectorAll('button[data-testid="team-name"]');

        teamNameButtons.forEach(buttonEl => {
            // The actual team name text is inside a span with specific classes
            const teamNameEl = buttonEl.querySelector('span[dir="auto"].fui-StyledText');
            
            if (teamNameEl) {
                const teamName = teamNameEl.textContent.trim();
                if (teamName) {
                    extractedData.teams.push({
                        name: teamName,
                        channels: [] // Channels are much harder to extract from this view
                    });
                }
            }
        });
    }

    // Run extraction function
    extractTeams();

    console.log('Extracted MS Teams data:', extractedData);

    // Send data back to the background script
    chrome.runtime.sendMessage({ 
        action: 'sendDataToBackend',
        platform: 'ms_teams',
        data: extractedData
    }, function(response) {
        console.log('Response from background script:', response.status);
    });
})();