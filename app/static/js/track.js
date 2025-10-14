// app/static/js/track.js

(function() {
    // ตรวจสอบว่าอยู่ในหน้า track หรือไม่
    if (!document.getElementById('total-pomodoros')) {
        return;
    }
    console.log('✅ Track page script is running!');

    /**
     * ฟังก์ชันหลักสำหรับดึงข้อมูลสถิติและอัปเดต UI ทั้งหมด
     */
    async function loadTrackDataAndRender() {
        console.log('🚀 กำลังดึงข้อมูล track...');
        try {
            const response = await fetch('/api/track/statistics');
            const data = await response.json();

            if (data.success) {
                console.log('✅ ดึงข้อมูลสำเร็จ:', data);
                // อัปเดตการ์ดข้อมูล
                updateTodayProgress(data.today);
                updateTotalStatistics(data.total);
                // วาดกราฟ
                renderWeeklyChart(data.weekly);
                renderTimeDistribution();
            } else {
                console.error('❌ API Error:', data.error);
            }
        } catch (error) {
            console.error('❌ เกิดข้อผิดพลาดในการเชื่อมต่อ:', error);
        }
    }

    /**
     * อัปเดตข้อมูลในส่วน "Today's Progress"
     */
    function updateTodayProgress(todayData) {
        console.log('📊 อัปเดต Today\'s Progress...');
        updateProgressBar('pomodoros', todayData.pomodoros.current, todayData.pomodoros.goal);
        updateProgressBar('study-time', todayData.study_time.current, todayData.study_time.goal);
        updateProgressBar('lessons', todayData.lessons.current, todayData.lessons.goal);
        updateProgressBar('notes', todayData.notes.current, todayData.notes.goal);
    }

    /**
     * อัปเดตแถบความคืบหน้า (Progress Bar) แต่ละรายการ
     */
    function updateProgressBar(id, current, goal) {
        const valueElement = document.getElementById(`today-${id}-value`);
        const barElement = document.getElementById(`today-${id}-bar`);
        if (valueElement && barElement) {
            const percentage = goal > 0 ? (current / goal) * 100 : 0;
            valueElement.textContent = `${current}/${goal}`;
            if (id === 'study-time') {
                valueElement.textContent += ' min';
            }
            barElement.style.width = `${percentage}%`;
        }
    }

    /**
     * อัปเดตข้อมูลในส่วน "Statistics Summary"
     */
    function updateTotalStatistics(totalData) {
        console.log('📈 อัปเดต Statistics Summary...');
        document.getElementById('total-pomodoros').textContent = totalData.pomodoros;
        const hours = Math.floor(totalData.study_time / 60);
        document.getElementById('total-study-time').textContent = `${hours}h`;
        document.getElementById('total-lessons').textContent = totalData.lessons;
        document.getElementById('total-notes').textContent = totalData.notes;
    }

    /**
     * วาดกราฟรายสัปดาห์
     */
    function renderWeeklyChart(weeklyData) {
        const ctx = document.getElementById('progress-chart');
        if (!ctx) return;

        if (window.weeklyChart) {
            window.weeklyChart.destroy();
        }

        // TODO: แทนที่ mock data ด้วย weeklyData จาก API
        const mockPomodoroData = [5, 7, 6, 8, 5, 3, 6];
        const mockNoteData = [3, 5, 4, 6, 3, 2, 4];

        window.weeklyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['จ', 'อ', 'พ', 'พฤ', 'ศ', 'ส', 'อา'],
                datasets: [{
                    label: 'Pomodoros',
                    data: mockPomodoroData, // ใช้ mock data ไปก่อน
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }, {
                    label: 'Notes',
                    data: mockNoteData, // ใช้ mock data ไปก่อน
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: false }
                }
            }
        });
        console.log('📈 วาดกราฟรายสัปดาห์เสร็จ');
    }

    /**
     * วาดกราฟการกระจายเวลา
     */
    function renderTimeDistribution() {
        const ctx = document.getElementById('time-chart');
        if (!ctx) return;

        if (window.timeChart) {
            window.timeChart.destroy();
        }

        window.timeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Study', 'Break', 'Note Taking'],
                datasets: [{
                    label: 'Time Distribution',
                    data: [120, 30, 45], // mock data
                    backgroundColor: [
                        'rgb(54, 162, 235)',
                        'rgb(255, 205, 86)',
                        'rgb(255, 99, 132)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });
        console.log('📊 วาดกราฟการกระจายเวลาเสร็จ');
    }

    // เริ่มทำงานเมื่อโหลดหน้า
    loadTrackDataAndRender();

})();