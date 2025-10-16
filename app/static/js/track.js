// app/static/js/track.js

(function() {
    console.log('📊 Track script loaded');
    
    // ฟังก์ชันสำหรับตรวจสอบว่าอยู่ในหน้า track หรือไม่
    function isTrackPage() {
        return document.getElementById('total-pomodoros') !== null || 
               document.getElementById('progress-chart') !== null ||
               document.getElementById('time-chart') !== null;
    }
    
    // ฟังก์ชันสำหรับรอให้ DOM พร้อม
    function waitForTrackPage() {
        if (isTrackPage()) {
            console.log('✅ Track page detected, initializing...');
            initializeTrackPage();
        } else {
            // รอ 100ms แล้วลองใหม่
            setTimeout(waitForTrackPage, 100);
        }
    }
    
    // เริ่มตรวจสอบเมื่อ DOM พร้อม
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', waitForTrackPage);
    } else {
        waitForTrackPage();
    }
    
    // ฟังก์ชันหลักสำหรับเริ่มต้นหน้า track
    function initializeTrackPage() {
        console.log('🚀 Initializing track page...');
        console.log('📊 Chart.js available:', typeof Chart !== 'undefined');
        console.log('🎯 Progress chart element:', document.getElementById('progress-chart'));
        console.log('🎯 Time chart element:', document.getElementById('time-chart'));
        console.log('🎯 Total pomodoros element:', document.getElementById('total-pomodoros'));

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
                // ✅ แสดง mock achievements
                renderMockAchievements();
            } else {
                console.error('❌ API Error:', data.error);
                // แสดงข้อมูล mock เมื่อ API ไม่ทำงาน
                showMockData();
            }
        } catch (error) {
            console.error('❌ เกิดข้อผิดพลาดในการเชื่อมต่อ:', error);
            // แสดงข้อมูล mock เมื่อเกิดข้อผิดพลาด
            showMockData();
        }
    }

    /**
     * แสดงข้อมูล mock เมื่อ API ไม่ทำงาน
     */
    function showMockData() {
        console.log('📊 แสดงข้อมูล mock...');
        
        // Mock data for today's progress
        const mockToday = {
            pomodoros: { current: 5, goal: 8 },
            study_time: { current: 125, goal: 240 },
            lessons: { current: 2, goal: 3 },
            notes: { current: 3, goal: 5 }
        };
        
        // Mock data for total statistics
        const mockTotal = {
            pomodoros: 45,
            study_time: 1125,
            lessons: 12,
            notes: 28
        };
        
        updateTodayProgress(mockToday);
        updateTotalStatistics(mockTotal);
        renderWeeklyChart([]);
        renderTimeDistribution();
        renderMockAchievements();
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
        const valueElement = document.getElementById(`${id}-goal`);
        const barElement = document.getElementById(`${id}-progress`);
        if (valueElement && barElement) {
            const percentage = goal > 0 ? (current / goal) * 100 : 0;
            valueElement.textContent = `${current}/${goal}`;
            if (id === 'study-time') {
                valueElement.textContent += ' min';
            }
            barElement.style.width = `${percentage}%`;
            barElement.setAttribute('aria-valuenow', percentage);
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
        console.log('📈 Rendering weekly chart...');
        const ctx = document.getElementById('progress-chart');
        console.log('🎯 Progress chart context:', ctx);
        
        if (!ctx) {
            console.warn('❌ Canvas element progress-chart not found');
            return;
        }

        if (window.weeklyChart) {
            window.weeklyChart.destroy();
        }

        // Mock data for demonstration (จะถูกแทนที่ด้วยข้อมูลจริงจาก API ในอนาคต)
        const mockPomodoroData = [5, 7, 6, 8, 5, 3, 6];
        const mockStudyTimeData = [125, 175, 150, 200, 125, 75, 150];

        window.weeklyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['จ', 'อ', 'พ', 'พฤ', 'ศ', 'ส', 'อา'],
                datasets: [
                    {
                        label: 'Pomodoros',
                        data: mockPomodoroData,
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Study Time (min)',
                        data: mockStudyTimeData,
                        borderColor: 'rgb(14, 184, 166)',
                        backgroundColor: 'rgba(14, 184, 166, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    title: { 
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        console.log('📈 วาดกราฟรายสัปดาห์เสร็จ');
    }

    /**
     * วาดกราฟการกระจายเวลา
     */
    function renderTimeDistribution() {
        console.log('📊 Rendering time distribution chart...');
        const ctx = document.getElementById('time-chart');
        console.log('🎯 Time chart context:', ctx);
        
        if (!ctx) {
            console.warn('❌ Canvas element time-chart not found');
            return;
        }

        if (window.timeChart) {
            window.timeChart.destroy();
        }

        // Mock data for demonstration
        const timeData = [180, 45, 75]; // Study, Break, Note Taking (minutes)
        const labels = ['Study Time', 'Break Time', 'Note Taking'];
        const colors = [
            'rgba(59, 130, 246, 0.8)',   // Blue for Study
            'rgba(245, 158, 11, 0.8)',   // Orange for Break  
            'rgba(168, 85, 247, 0.8)'    // Purple for Note Taking
        ];

        window.timeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: timeData,
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace('0.8', '1')),
                    borderWidth: 2,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { 
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} min (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
        console.log('📊 วาดกราฟการกระจายเวลาเสร็จ');
    }

    /**
     * ✅ แสดง Mock-up Achievements
     */
    function renderMockAchievements() {
        const container = document.getElementById('achievements-list');
        if (!container) return;

        const achievements = [
            { icon: '🏆', title: 'Focus Master', desc: 'Completed 8 Pomodoros in one day' },
            { icon: '📘', title: 'Knowledge Seeker', desc: 'Finished 10 lessons' },
            { icon: '📝', title: 'Note Expert', desc: 'Created 20 notes' }
        ];

        container.innerHTML = achievements.map(a => `
            <div class="achievement-item mb-3 d-flex align-items-center">
                <div class="achievement-icon me-3">${a.icon}</div>
                <div>
                    <div class="fw-bold">${a.title}</div>
                    <div class="text-secondary small">${a.desc}</div>
                </div>
            </div>
        `).join('');
    }

        // เริ่มทำงานเมื่อโหลดหน้า
        // รอให้ Chart.js โหลดเสร็จก่อน
        if (typeof Chart !== 'undefined') {
            console.log('✅ Chart.js is loaded, initializing track data...');
            loadTrackDataAndRender();
        } else {
            console.warn('⚠️ Chart.js not loaded, retrying in 100ms...');
            setTimeout(() => {
                if (typeof Chart !== 'undefined') {
                    loadTrackDataAndRender();
                } else {
                    console.error('❌ Chart.js failed to load');
                    showMockData();
                }
            }, 100);
        }

        // Export functions for global access
        window.TrackPage = {
            loadTrackDataAndRender,
            showMockData,
            renderWeeklyChart,
            renderTimeDistribution
        };
    }

})();
