/**
 * Pomodoro Statistics Manager
 * SPA Component for managing and displaying Pomodoro statistics
 */

class PomodoroStatisticsManager {
    constructor() {
        this.apiBase = '/api/pomodoro/statistics';
        this.currentView = 'summary';
        this.charts = {};
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
        
        this.init();
    }

    async init() {
        console.log('🍅 Initializing Pomodoro Statistics Manager...');
        
        try {
            // Check if user is logged in
            if (!this.isUserLoggedIn()) {
                this.showError('Please log in to view statistics');
                return;
            }

            // Initialize UI components
            this.initializeUI();
            
            // Load initial data
            await this.loadSummaryData();
            
            // Setup event listeners
            this.setupEventListeners();
            
            console.log('✅ Pomodoro Statistics Manager initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Statistics Manager:', error);
            this.showError('Failed to load statistics');
        }
    }

    isUserLoggedIn() {
        // Check for user session - adjust based on your auth system
        return document.cookie.includes('session') || localStorage.getItem('user_id');
    }

    initializeUI() {
        // Create main container if it doesn't exist
        if (!document.getElementById('pomodoro-statistics-container')) {
            const container = document.createElement('div');
            container.id = 'pomodoro-statistics-container';
            container.className = 'pomodoro-statistics-container';
            document.body.appendChild(container);
        }

        this.container = document.getElementById('pomodoro-statistics-container');
        this.renderInitialUI();
    }

    renderInitialUI() {
        this.container.innerHTML = `
            <div class="statistics-dashboard">
                <!-- Header -->
                <div class="statistics-header">
                    <h2><i class="fas fa-chart-bar"></i> Pomodoro Statistics</h2>
                    <div class="statistics-controls">
                        <button class="btn btn-primary" id="refresh-stats">
                            <i class="fas fa-sync"></i> Refresh
                        </button>
                        <button class="btn btn-secondary" id="recalculate-stats">
                            <i class="fas fa-calculator"></i> Recalculate
                        </button>
                    </div>
                </div>

                <!-- Navigation Tabs -->
                <div class="statistics-nav">
                    <button class="nav-btn active" data-view="summary">
                        <i class="fas fa-tachometer-alt"></i> Summary
                    </button>
                    <button class="nav-btn" data-view="daily">
                        <i class="fas fa-calendar-day"></i> Daily
                    </button>
                    <button class="nav-btn" data-view="weekly">
                        <i class="fas fa-calendar-week"></i> Weekly
                    </button>
                    <button class="nav-btn" data-view="trends">
                        <i class="fas fa-chart-line"></i> Trends
                    </button>
                </div>

                <!-- Content Area -->
                <div class="statistics-content">
                    <!-- Loading Spinner -->
                    <div class="loading-spinner" id="stats-loading">
                        <i class="fas fa-spinner fa-spin"></i>
                        <span>Loading statistics...</span>
                    </div>

                    <!-- Error Message -->
                    <div class="error-message" id="stats-error" style="display: none;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span id="error-text"></span>
                    </div>

                    <!-- Summary View -->
                    <div class="view-content" id="summary-view">
                        <div class="summary-cards">
                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-clock"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>Today's Focus Time</h3>
                                    <span class="stat-value" id="today-focus-time">--</span>
                                    <span class="stat-unit">minutes</span>
                                </div>
                            </div>

                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-fire"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>Today's Sessions</h3>
                                    <span class="stat-value" id="today-sessions">--</span>
                                    <span class="stat-unit">sessions</span>
                                </div>
                            </div>

                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-trophy"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>Productivity Score</h3>
                                    <span class="stat-value" id="productivity-score">--</span>
                                    <span class="stat-unit">/10</span>
                                </div>
                            </div>

                            <div class="stat-card">
                                <div class="stat-icon">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                                <div class="stat-content">
                                    <h3>Weekly Trend</h3>
                                    <span class="stat-value trend" id="weekly-trend">--</span>
                                </div>
                            </div>
                        </div>

                        <!-- Charts -->
                        <div class="charts-section">
                            <div class="chart-container">
                                <h4>Daily Focus Time</h4>
                                <canvas id="daily-chart"></canvas>
                            </div>
                            <div class="chart-container">
                                <h4>Productivity Trends</h4>
                                <canvas id="productivity-chart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Daily View -->
                    <div class="view-content" id="daily-view" style="display: none;">
                        <div class="daily-controls">
                            <input type="date" id="daily-date-picker" class="form-control">
                            <button class="btn btn-primary" id="load-daily">Load</button>
                        </div>
                        <div id="daily-statistics-content"></div>
                    </div>

                    <!-- Weekly View -->
                    <div class="view-content" id="weekly-view" style="display: none;">
                        <div class="weekly-controls">
                            <input type="week" id="weekly-picker" class="form-control">
                            <button class="btn btn-primary" id="load-weekly">Load</button>
                        </div>
                        <div id="weekly-statistics-content"></div>
                    </div>

                    <!-- Trends View -->
                    <div class="view-content" id="trends-view" style="display: none;">
                        <div class="trends-controls">
                            <select id="trends-period" class="form-control">
                                <option value="7">Last 7 days</option>
                                <option value="14">Last 14 days</option>
                                <option value="30">Last 30 days</option>
                            </select>
                            <button class="btn btn-primary" id="load-trends">Load</button>
                        </div>
                        <div id="trends-statistics-content"></div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        // Navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.switchView(view);
            });
        });

        // Refresh button
        document.getElementById('refresh-stats')?.addEventListener('click', () => {
            this.clearCache();
            this.loadCurrentView();
        });

        // Recalculate button
        document.getElementById('recalculate-stats')?.addEventListener('click', () => {
            this.recalculateStatistics();
        });

        // Daily view controls
        document.getElementById('load-daily')?.addEventListener('click', () => {
            const date = document.getElementById('daily-date-picker').value;
            this.loadDailyStatistics(date);
        });

        // Weekly view controls
        document.getElementById('load-weekly')?.addEventListener('click', () => {
            const week = document.getElementById('weekly-picker').value;
            this.loadWeeklyStatistics(week);
        });

        // Trends view controls
        document.getElementById('load-trends')?.addEventListener('click', () => {
            const period = document.getElementById('trends-period').value;
            this.loadTrendsStatistics(parseInt(period));
        });

        // Set default values
        this.setDefaultDates();
    }

    setDefaultDates() {
        // Set today's date for daily picker
        const today = new Date().toISOString().split('T')[0];
        const dailyPicker = document.getElementById('daily-date-picker');
        if (dailyPicker) {
            dailyPicker.value = today;
        }

        // Set current week for weekly picker
        const weekPicker = document.getElementById('weekly-picker');
        if (weekPicker) {
            const now = new Date();
            const year = now.getFullYear();
            const week = this.getWeekNumber(now);
            weekPicker.value = `${year}-W${week.toString().padStart(2, '0')}`;
        }
    }

    getWeekNumber(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }

    switchView(view) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');

        // Hide all views
        document.querySelectorAll('.view-content').forEach(content => {
            content.style.display = 'none';
        });

        // Show selected view
        document.getElementById(`${view}-view`).style.display = 'block';

        this.currentView = view;
        this.loadCurrentView();
    }

    async loadCurrentView() {
        switch (this.currentView) {
            case 'summary':
                await this.loadSummaryData();
                break;
            case 'daily':
                const date = document.getElementById('daily-date-picker').value;
                await this.loadDailyStatistics(date);
                break;
            case 'weekly':
                await this.loadWeeklyStatistics();
                break;
            case 'trends':
                const period = parseInt(document.getElementById('trends-period').value);
                await this.loadTrendsStatistics(period);
                break;
        }
    }

    async loadSummaryData() {
        try {
            this.showLoading();
            
            const data = await this.apiRequest('/summary');
            
            if (data.success) {
                this.renderSummaryData(data.data);
                await this.loadSummaryCharts();
            } else {
                this.showError(data.message || 'Failed to load summary');
            }
            
        } catch (error) {
            console.error('Error loading summary:', error);
            this.showError('Failed to load summary data');
        } finally {
            this.hideLoading();
        }
    }

    renderSummaryData(data) {
        const today = data.today || {};
        const trends = data.trends || {};

        // Update stat cards
        document.getElementById('today-focus-time').textContent = 
            today.total_focus_time || 0;
        
        document.getElementById('today-sessions').textContent = 
            today.total_sessions || 0;
        
        document.getElementById('productivity-score').textContent = 
            (today.productivity_score || 0).toFixed(1);
        
        const trendElement = document.getElementById('weekly-trend');
        const trendClass = trends.trend || 'neutral';
        trendElement.textContent = trendClass.charAt(0).toUpperCase() + trendClass.slice(1);
        trendElement.className = `stat-value trend ${trendClass}`;
    }

    async loadSummaryCharts() {
        try {
            // Load chart data
            const chartData = await this.apiRequest('/chart?type=weekly');
            
            if (chartData.success) {
                this.renderDailyChart(chartData.data);
            }

            // Load productivity trends
            const trendsData = await this.apiRequest('/trends?days=7');
            
            if (trendsData.success) {
                this.renderProductivityChart(trendsData.data);
            }
            
        } catch (error) {
            console.error('Error loading charts:', error);
        }
    }

    renderDailyChart(data) {
        const ctx = document.getElementById('daily-chart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts.daily) {
            this.charts.daily.destroy();
        }

        this.charts.daily = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Focus Time (minutes)',
                    data: data.focus_time || [],
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderProductivityChart(data) {
        const ctx = document.getElementById('productivity-chart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts.productivity) {
            this.charts.productivity.destroy();
        }

        this.charts.productivity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Productivity Score',
                    data: data.values || [],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10
                    }
                }
            }
        });
    }

    async loadDailyStatistics(date) {
        try {
            this.showLoading();
            
            const url = date ? `/daily?date=${date}` : '/daily';
            const data = await this.apiRequest(url);
            
            if (data.success) {
                this.renderDailyStatistics(data.data);
            } else {
                this.showError(data.message || 'Failed to load daily statistics');
            }
            
        } catch (error) {
            console.error('Error loading daily statistics:', error);
            this.showError('Failed to load daily statistics');
        } finally {
            this.hideLoading();
        }
    }

    renderDailyStatistics(data) {
        const container = document.getElementById('daily-statistics-content');
        if (!container) return;

        container.innerHTML = `
            <div class="daily-stats-grid">
                <div class="stat-item">
                    <h4>Total Sessions</h4>
                    <span class="value">${data.total_sessions || 0}</span>
                </div>
                <div class="stat-item">
                    <h4>Focus Time</h4>
                    <span class="value">${data.total_focus_time || 0} min</span>
                </div>
                <div class="stat-item">
                    <h4>Break Time</h4>
                    <span class="value">${data.total_break_time || 0} min</span>
                </div>
                <div class="stat-item">
                    <h4>Completed Sessions</h4>
                    <span class="value">${data.total_completed_sessions || 0}</span>
                </div>
                <div class="stat-item">
                    <h4>Productivity Score</h4>
                    <span class="value">${(data.productivity_score || 0).toFixed(1)}/10</span>
                </div>
                <div class="stat-item">
                    <h4>Tasks Completed</h4>
                    <span class="value">${data.total_tasks_completed || 0}</span>
                </div>
            </div>
        `;
    }

    async loadWeeklyStatistics(week) {
        try {
            this.showLoading();
            
            const url = week ? `/weekly?start_date=${this.weekToDate(week)}` : '/weekly';
            const data = await this.apiRequest(url);
            
            if (data.success) {
                this.renderWeeklyStatistics(data.data);
            } else {
                this.showError(data.message || 'Failed to load weekly statistics');
            }
            
        } catch (error) {
            console.error('Error loading weekly statistics:', error);
            this.showError('Failed to load weekly statistics');
        } finally {
            this.hideLoading();
        }
    }

    weekToDate(weekString) {
        // Convert "2023-W42" to "2023-10-16" (Monday of that week)
        const [year, week] = weekString.split('-W');
        const january4th = new Date(year, 0, 4);
        const monday = new Date(january4th.getTime() + (week - 1) * 7 * 24 * 60 * 60 * 1000);
        monday.setDate(monday.getDate() - january4th.getDay() + 1);
        return monday.toISOString().split('T')[0];
    }

    renderWeeklyStatistics(data) {
        const container = document.getElementById('weekly-statistics-content');
        if (!container) return;

        if (!data || data.length === 0) {
            container.innerHTML = '<p>No data available for this week.</p>';
            return;
        }

        const totalFocusTime = data.reduce((sum, day) => sum + (day.total_focus_time || 0), 0);
        const totalSessions = data.reduce((sum, day) => sum + (day.total_sessions || 0), 0);
        const avgProductivity = data.reduce((sum, day) => sum + (day.productivity_score || 0), 0) / data.length;

        container.innerHTML = `
            <div class="weekly-summary">
                <h4>Weekly Summary</h4>
                <div class="summary-stats">
                    <div class="summary-item">
                        <span class="label">Total Focus Time:</span>
                        <span class="value">${totalFocusTime} minutes</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Total Sessions:</span>
                        <span class="value">${totalSessions}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Average Productivity:</span>
                        <span class="value">${avgProductivity.toFixed(1)}/10</span>
                    </div>
                </div>
            </div>
            
            <div class="weekly-breakdown">
                <h4>Daily Breakdown</h4>
                <div class="days-grid">
                    ${data.map(day => `
                        <div class="day-item">
                            <div class="day-date">${new Date(day.date).toLocaleDateString()}</div>
                            <div class="day-stats">
                                <div>Focus: ${day.total_focus_time || 0}m</div>
                                <div>Sessions: ${day.total_sessions || 0}</div>
                                <div>Score: ${(day.productivity_score || 0).toFixed(1)}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    async loadTrendsStatistics(days) {
        try {
            this.showLoading();
            
            const data = await this.apiRequest(`/trends?days=${days}`);
            
            if (data.success) {
                this.renderTrendsStatistics(data.data);
            } else {
                this.showError(data.message || 'Failed to load trends');
            }
            
        } catch (error) {
            console.error('Error loading trends:', error);
            this.showError('Failed to load trends data');
        } finally {
            this.hideLoading();
        }
    }

    renderTrendsStatistics(data) {
        const container = document.getElementById('trends-statistics-content');
        if (!container) return;

        container.innerHTML = `
            <div class="trends-overview">
                <div class="trend-indicator ${data.trend}">
                    <h3>Trend: ${data.trend.charAt(0).toUpperCase() + data.trend.slice(1)}</h3>
                    <p>Your productivity is ${data.trend} over the selected period.</p>
                </div>
                
                <div class="trends-metrics">
                    <div class="metric">
                        <h4>Average Productivity</h4>
                        <span class="value">${data.average_productivity.toFixed(1)}/10</span>
                    </div>
                    <div class="metric">
                        <h4>Total Focus Time</h4>
                        <span class="value">${data.total_focus_time} minutes</span>
                    </div>
                    <div class="metric">
                        <h4>Completion Rate</h4>
                        <span class="value">${data.completion_rate.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
    }

    async recalculateStatistics() {
        try {
            this.showLoading();
            
            const data = await this.apiRequest('/recalculate', 'POST');
            
            if (data.success) {
                this.showSuccess('Statistics recalculated successfully');
                this.clearCache();
                this.loadCurrentView();
            } else {
                this.showError(data.message || 'Failed to recalculate statistics');
            }
            
        } catch (error) {
            console.error('Error recalculating statistics:', error);
            this.showError('Failed to recalculate statistics');
        } finally {
            this.hideLoading();
        }
    }

    async apiRequest(endpoint, method = 'GET', body = null) {
        const cacheKey = `${method}-${endpoint}`;
        
        // Check cache for GET requests
        if (method === 'GET' && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${this.apiBase}${endpoint}`, options);
        const data = await response.json();

        // Cache successful GET requests
        if (method === 'GET' && data.success) {
            this.cache.set(cacheKey, {
                data,
                timestamp: Date.now()
            });
        }

        return data;
    }

    clearCache() {
        this.cache.clear();
    }

    showLoading() {
        const loading = document.getElementById('stats-loading');
        if (loading) loading.style.display = 'flex';
    }

    hideLoading() {
        const loading = document.getElementById('stats-loading');
        if (loading) loading.style.display = 'none';
    }

    showError(message) {
        const errorEl = document.getElementById('stats-error');
        const errorText = document.getElementById('error-text');
        
        if (errorEl && errorText) {
            errorText.textContent = message;
            errorEl.style.display = 'block';
            
            // Hide after 5 seconds
            setTimeout(() => {
                errorEl.style.display = 'none';
            }, 5000);
        }
    }

    showSuccess(message) {
        // Create temporary success message
        const successEl = document.createElement('div');
        successEl.className = 'success-message';
        successEl.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        this.container.appendChild(successEl);
        
        setTimeout(() => {
            successEl.remove();
        }, 3000);
    }

    // Public method to destroy the instance
    destroy() {
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        // Clear cache
        this.clearCache();
        
        // Remove container
        if (this.container) {
            this.container.remove();
        }
    }
}

// Auto-initialize if Chart.js is available
if (typeof Chart !== 'undefined') {
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.pomodoroStats = new PomodoroStatisticsManager();
        });
    } else {
        window.pomodoroStats = new PomodoroStatisticsManager();
    }
} else {
    console.warn('Chart.js not found. Please include Chart.js library for statistics charts.');
}