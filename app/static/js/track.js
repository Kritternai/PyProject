// app/static/js/track.js

(function() {
    if (!document.getElementById('total-pomodoros')) {
        return;
    }
    console.log('✅ Track page script is running!');
    async function loadTrackData() {
        console.log('🚀 กำลังดึงข้อมูล track...');
        try {
            const response = await fetch('/api/track/statistics');
            const data = await response.json();
            if (data.success) {
                console.log('✅ ดึงข้อมูลสำเร็จ:', data);
                updateTodayProgress(data.today);
                updateTotalStatistics(data.total);
            } else {
                console.error('❌ API Error:', data.error);
            }
        } catch (error) {
            console.error('❌ เกิดข้อผิดพลาดในการเชื่อมต่อ:', error);
        }
    }
    function updateTodayProgress(todayData) {
        console.log('📊 อัปเดต Today\'s Progress...');
        updateProgressBar('pomodoros', todayData.pomodoros.current, todayData.pomodoros.goal);
        updateProgressBar('study-time', todayData.study_time.current, todayData.study_time.goal);
        updateProgressBar('lessons', todayData.lessons.current, todayData.lessons.goal);
        updateProgressBar('notes', todayData.notes.current, todayData.notes.goal);
    }
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
    function updateTotalStatistics(totalData) {
        console.log('📈 อัปเดต Statistics Summary...');
        document.getElementById('total-pomodoros').textContent = totalData.pomodoros;
        const hours = Math.floor(totalData.study_time / 60);
        document.getElementById('total-study-time').textContent = `${hours}h`;
        document.getElementById('total-lessons').textContent = totalData.lessons;
        document.getElementById('total-notes').textContent = totalData.notes;
    }
    loadTrackData();
})();