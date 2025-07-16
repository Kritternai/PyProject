// This script runs on Google Classroom pages

(function() {
    console.log('Google Classroom content script loaded.');

    const extractedData = {
        courses: []
    };

    // Function to extract course data and associated assignments from the main Classroom dashboard
    function extractCoursesAndAssignments() {
        // Selector for individual course cards on the main classroom dashboard
        const courseCardElements = document.querySelectorAll('li.gHz6xd.Aopndd.rZXyy');

        courseCardElements.forEach(courseCardEl => {
            const course = {};

            // Extract Course ID from data-course-id attribute
            course.id = courseCardEl.dataset.courseId;

            // Extract Course Name
            const courseNameEl = courseCardEl.querySelector('.ScpeUc.Vu2fZd.z3vRcc-ZoZQ1');
            course.name = courseNameEl ? courseNameEl.textContent.trim() : 'Unknown Course';

            // Extract Course Section (e.g., "Sec 1", "2/2567")
            const courseSectionEl = courseCardEl.querySelector('.FWGURc.Vu2fZd');
            course.section = courseSectionEl ? courseSectionEl.textContent.trim() : '';

            // Extract Instructor Name
            const instructorNameEl = courseCardEl.querySelector('.z07MGc.Vu2fZd.jJIbcc');
            course.instructor = instructorNameEl ? instructorNameEl.textContent.trim() : 'Unknown Instructor';

            course.assignments = [];

            // Extract Assignment (if present within the course card on the dashboard)
            const assignmentContainerEl = courseCardEl.querySelector('.TQYOZc');
            if (assignmentContainerEl) {
                const assignmentTitleEl = assignmentContainerEl.querySelector('.onkcGd.ARTZne');
                const dueDateEl = assignmentContainerEl.querySelector('.COwiKd'); // "Due tomorrow" or "No work due soon"

                if (assignmentTitleEl) {
                    const assignmentTitle = assignmentTitleEl.textContent.trim();
                    let dueDateText = dueDateEl ? dueDateEl.textContent.trim() : '';
                    let dueDate = null;

                    // Basic parsing for due date
                    if (dueDateText.includes('Due')) {
                        dueDateText = dueDateText.replace('Due ', '').trim();
                        try {
                            // Attempt to parse date, might need more robust parsing for different locales/formats
                            // For "Due tomorrow", "Due today", etc., this will need more logic
                            if (dueDateText.toLowerCase() === 'tomorrow') {
                                const tomorrow = new Date();
                                tomorrow.setDate(tomorrow.getDate() + 1);
                                dueDate = tomorrow.toISOString().split('T')[0]; // Just date part
                            } else if (dueDateText.toLowerCase() === 'today') {
                                const today = new Date();
                                dueDate = today.toISOString().split('T')[0];
                            } else {
                                // For actual date strings
                                const parsedDate = new Date(dueDateText);
                                if (!isNaN(parsedDate)) {
                                    dueDate = parsedDate.toISOString().split('T')[0];
                                }
                            }
                        } catch (e) {
                            console.warn('Could not parse due date:', dueDateText, e);
                        }
                    }

                    course.assignments.push({
                        title: assignmentTitle,
                        dueDate: dueDate
                    });
                }
            }

            extractedData.courses.push(course);
        });
    }

    // Only run extraction if on the main Google Classroom dashboard
    if (window.location.href.includes('classroom.google.com/u/') && !window.location.href.includes('/c/')) {
        extractCoursesAndAssignments();
    } else {
        // If on a specific course page, you might want to implement different logic
        // For now, we'll just log a message
        console.log('Not on the main Google Classroom dashboard. Skipping detailed course/assignment extraction.');
    }

    console.log('Extracted Google Classroom data:', extractedData);

    // Send data back to the background script
    chrome.runtime.sendMessage({ 
        action: 'sendDataToBackend',
        platform: 'google_classroom',
        data: extractedData
    }, function(response) {
        console.log('Response from background script:', response.status);
    });
})();