
(function() {
    // Function to extract text content, handling <br> tags and removing leading/trailing whitespace
    function getTextContent(element) {
        if (!element) return [];
        const parser = new DOMParser();
        const doc = parser.parseFromString(element.innerHTML, 'text/html');
        // Replace <br> with a newline character in the parsed document's body
        doc.body.querySelectorAll('br').forEach(br => br.replaceWith('\n'));
        // Get text content and split by newlines, then trim and filter empty strings
        return doc.body.textContent.split('\n').map(s => s.trim()).filter(s => s.length > 0);
    }

    function parseSchedule(scheduleStrings) {
        const schedules = [];
        scheduleStrings.forEach(str => {
            // Regex to capture day, time range, and optional type (ท/ป)
            const match = str.match(/^(.*?) (\d{2}:\d{2}-\d{2}:\d{2}) น\.(?:\((.)\))?$/);
            if (match) {
                schedules.push({
                    day: match[1].trim(),
                    time: match[2].trim(),
                    type: match[3] ? match[3].trim() : '' // Type is optional
                });
            } else {
                schedules.push({ raw: str }); // Fallback for unparseable strings
            }
        }); // Missing closing brace was here
        return schedules;
    }

    // Check if we are on the correct page
    if (window.location.href.includes('https://www.reg.kmitl.ac.th/u_student/report_studytable_show.php')) {
        const studyTable = document.querySelector('table[width="1258"]'); // Select the main table

        if (studyTable) {
            const rows = studyTable.querySelectorAll('tr');
            const extractedData = {
                institute: '',
                faculty: '',
                department: '',
                major: '',
                semester: '',
                academic_year: '',
                student_id: '',
                student_name: '',
                courses: []
            };

            // Extract header information
            // Assuming fixed row indices for header info based on provided HTML
            extractedData.institute = rows[1].querySelector('td').textContent.trim();
            extractedData.faculty = rows[3].querySelector('td').textContent.trim();

            const deptMajorRow = rows[5].querySelector('td').textContent.trim();
            const deptMatch = deptMajorRow.match(/ภาควิชา\s*(.*?)\s*สาขาวิชา\s*(.*)/);
            if (deptMatch) {
                extractedData.department = deptMatch[1].trim();
                extractedData.major = deptMatch[2].trim();
            }

            const semesterYearRow = rows[7].querySelector('td').textContent.trim();
            const semYearMatch = semesterYearRow.match(/ประจำภาคเรียนที่\s*(\d+)\s*ปีการศึกษา\s*(\d+)/);
            if (semYearMatch) {
                extractedData.semester = semYearMatch[1].trim();
                extractedData.academic_year = semYearMatch[2].trim();
            }

            const studentInfoRow = rows[9].querySelector('td').textContent.trim();
            const studentMatch = studentInfoRow.match(/รหัสนักศึกษา\s*(\d+)\s*ชื่อ\s*(.*)/);
            if (studentMatch) {
                extractedData.student_id = studentMatch[1].trim();
                extractedData.student_name = studentMatch[2].trim();
            }

            // Find the starting row for course data (after the header row with "ลำดับ", "รหัสวิชา", etc.)
            let courseDataStartIndex = -1;
            for (let i = 0; i < rows.length; i++) {
                const firstCell = rows[i].querySelector('td');
                if (firstCell && firstCell.textContent.includes('ลำดับ')) {
                    courseDataStartIndex = i + 2; // +2 to skip the header row and the empty row after it
                    break;
                }
            }

            if (courseDataStartIndex !== -1) {
                for (let i = courseDataStartIndex; i < rows.length; i++) {
                    const cells = rows[i].querySelectorAll('td');
                    // Skip empty rows or rows that are just separators
                    if (cells.length < 10 || (cells.length === 1 && cells[0].getAttribute('height') === '1')) {
                        continue;
                    }

                    const course = {}; // <<< ADDED THIS LINE

                    // Direct access to cells based on the observed HTML structure
                    // This is more brittle if the HTML structure changes, but simpler if it's stable.
                    // Given the previous attempts, this might be more reliable than complex helper functions.

                    course.order = parseInt(cells[0].textContent.trim());
                    course.course_code = cells[2].textContent.trim();
                    course.course_name = cells[4].textContent.trim();
                    course.credits = cells[6].textContent.trim();
                    course.theory_section = cells[8].textContent.trim();
                    course.practical_section = cells[10].textContent.trim().replace(/<font color="#FF6600">|<\/font>/g, '');
                    course.schedule_raw = getTextContent(cells[12]);
                    course.schedule = parseSchedule(course.schedule_raw);
                    course.room_raw = getTextContent(cells[14]);
                    course.building_raw = getTextContent(cells[16]);
                    course.remarks = cells[17].textContent.trim();

                    extractedData.courses.push(course);
                }
            }

            // Send the extracted data to the background script
            chrome.runtime.sendMessage({
                action: 'sendDataToBackend',
                platform: 'kmitl_studytable',
                data: extractedData
            }, function(response) {
                console.log('Response from background script:', response.status);
            });
        } else {
            console.warn('KMITL Study Table: Main table not found.');
        }
    }
})();
