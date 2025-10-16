// Simple chart test to verify Chart.js is working
console.log('🧪 Chart test script loaded');

function testChart() {
    console.log('🧪 Testing Chart.js...');
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js is not loaded');
        return false;
    }
    
    console.log('✅ Chart.js is available');
    
    // Test if we can create a simple chart
    const testCanvas = document.createElement('canvas');
    testCanvas.id = 'test-chart';
    testCanvas.width = 200;
    testCanvas.height = 100;
    
    try {
        const ctx = testCanvas.getContext('2d');
        const testChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['A', 'B', 'C'],
                datasets: [{
                    label: 'Test',
                    data: [1, 2, 3],
                    borderColor: 'rgb(75, 192, 192)'
                }]
            },
            options: {
                responsive: false
            }
        });
        
        console.log('✅ Chart creation successful:', testChart);
        testChart.destroy();
        return true;
    } catch (error) {
        console.error('❌ Chart creation failed:', error);
        return false;
    }
}

// Export for global access
window.testChart = testChart;

// Auto-test when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', testChart);
} else {
    testChart();
}
