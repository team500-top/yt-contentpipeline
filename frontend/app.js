/**
 * YouTube Analyzer - Frontend Application
 * Современный JavaScript для управления интерфейсом
 */

// ============ CONFIGURATION ============
const CONFIG = {
    API_BASE: '/api',
    UPDATE_INTERVAL: 5000,
    PAGINATION_LIMIT: 50
};

// ============ GLOBAL STATE ============
const STATE = {
    currentTab: 'new-task',
    tasks: new Map(),
    videos: [],
    channels: [],
    config: {},
    stats: {},
    isLoading: false
};

// ============ API CLIENT ============
class ApiClient {
    constructor(baseUrl = CONFIG.API_BASE) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // Tasks API
    async getTasks() {
        return this.request('/tasks');
    }

    async createTask(taskData) {
        return this.request('/tasks', {
            method: 'POST',
            body: taskData
        });
    }

    async getTask(taskId) {
        return this.request(`/tasks/${taskId}`);
    }

    async pauseTask(taskId) {
        return this.request(`/tasks/${taskId}/pause`, { method: 'POST' });
    }

    async resumeTask(taskId) {
        return this.request(`/tasks/${taskId}/resume`, { method: 'POST' });
    }

    // Data API
    async getVideos(limit = 50, offset = 0) {
        return this.request(`/data/videos?limit=${limit}&offset=${offset}`);
    }

    async getVideoDetails(videoId) {
        return this.request(`/data/videos/${videoId}`);
    }

    async getChannels() {
        return this.request('/data/channels');
    }

    async getStats() {
        return this.request('/data/stats');
    }

    async exportData() {
        return this.request('/data/export');
    }

    async clearDatabase() {
        return this.request('/data/clear', { method: 'DELETE' });
    }

    // Config API
    async getConfig() {
        return this.request('/config');
    }

    async updateConfig(configData) {
        return this.request('/config', {
            method: 'POST',
            body: configData
        });
    }

    // YouTube API
    async searchVideos(query, maxResults = 10, order = 'relevance') {
        return this.request(`/youtube/search?query=${encodeURIComponent(query)}&max_results=${maxResults}&order=${order}`);
    }
}

// ============ UTILITIES ============
class Utils {
    static formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    static formatDate(dateStr, short = false) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        if (short) {
            return date.toLocaleDateString('ru-RU');
        }
        return date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }

    static formatDuration(duration) {
        if (!duration) return '-';
        const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
        if (!match) return duration;
        
        const hours = parseInt(match[1] || 0);
        const minutes = parseInt(match[2] || 0);
        const seconds = parseInt(match[3] || 0);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    static showAlert(message, type = 'info') {
        const alert = document.getElementById('alert');
        if (!alert) return;

        alert.classList.remove('hidden');
        
        const colors = {
            'success': 'bg-green-50 border-green-200 text-green-800',
            'error': 'bg-red-50 border-red-200 text-red-800',
            'info': 'bg-blue-50 border-blue-200 text-blue-800',
            'warning': 'bg-yellow-50 border-yellow-200 text-yellow-800'
        };
        
        const icons = {
            'success': 'check-circle',
            'error': 'x-circle',
            'info': 'info',
            'warning': 'alert-triangle'
        };
        
        alert.className = `fixed top-20 right-4 z-50 max-w-sm p-4 rounded-lg border ${colors[type]} shadow-lg`;
        alert.innerHTML = `
            <div class="flex items-start space-x-3">
                <i data-lucide="${icons[type]}" class="w-5 h-5 flex-shrink-0 mt-0.5"></i>
                <div class="flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.classList.add('hidden')" class="text-gray-400 hover:text-gray-600 flex-shrink-0">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        setTimeout(() => {
            alert.classList.add('hidden');
        }, 5000);
    }

    static showLoading(element, show = true) {
        if (show) {
            element.innerHTML = `
                <div class="flex items-center justify-center py-8">
                    <div class="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                    <span class="ml-3 text-gray-500">Загрузка...</span>
                </div>
            `;
        }
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// ============ TAB MANAGEMENT ============
class TabManager {
    constructor() {
        this.currentTab = 'new-task';
        this.initEventListeners();
    }

    initEventListeners() {
        document.addEventListener('click', (e) => {
            const tabButton = e.target.closest('.nav-tab');
            if (tabButton) {
                const tabName = tabButton.getAttribute('data-tab');
                if (tabName) {
                    this.showTab(tabName, e);
                }
            }
        });
    }

    showTab(tabName, event) {
        this.currentTab = tabName;
        
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        if (event && event.target) {
            event.target.closest('.nav-tab').classList.add('active');
        } else {
            const targetTab = document.querySelector(`[data-tab="${tabName}"]`);
            if (targetTab) targetTab.classList.add('active');
        }
        
        // Show/hide panels
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        const targetPanel = document.getElementById(tabName);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }
        
        // Load data for specific tabs
        this.loadTabData(tabName);
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'tasks':
                await taskManager.loadTasks();
                break;
            case 'videos':
                await videoManager.loadVideos();
                break;
            case 'channels':
                await channelManager.loadChannels();
                break;
            case 'config':
                await configManager.loadConfig();
                break;
            case 'stats':
                await statsManager.loadStats();
                break;
            case 'help':
                if (typeof initHelp === 'function') {
                    initHelp();
                }
                break;
        }
    }
}

// ============ TASK MANAGEMENT ============
class TaskManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.initEventListeners();
    }

    initEventListeners() {
        const taskForm = document.getElementById('task-form');
        if (taskForm) {
            taskForm.addEventListener('submit', this.handleTaskSubmit.bind(this));
        }
    }

    async handleTaskSubmit(e) {
        e.preventDefault();
        
        const keywords = document.getElementById('keywords').value
            .split('\n')
            .map(k => k.trim())
            .filter(k => k);
            
        const channels = document.getElementById('channels').value
            .split('\n')
            .map(c => c.trim())
            .filter(c => c);
            
        const orderBy = document.querySelector('input[name="order"]:checked').value;
        
        if (keywords.length === 0 && channels.length === 0) {
            Utils.showAlert('Введите хотя бы один ключевой запрос или канал', 'error');
            return;
        }
        
        const submitBtn = document.querySelector('#task-form button[type="submit"]');
        const submitText = document.getElementById('submit-text');
        const submitSpinner = document.getElementById('submit-spinner');
        
        submitBtn.disabled = true;
        if (submitText) submitText.style.display = 'none';
        if (submitSpinner) submitSpinner.classList.remove('hidden');
        
        try {
            const response = await this.api.createTask({
                keywords,
                channels,
                order_by: orderBy
            });
            
            Utils.showAlert('Задача успешно создана!', 'success');
            document.getElementById('task-form').reset();
            tabManager.showTab('tasks');
            
        } catch (error) {
            Utils.showAlert('Ошибка при создании задачи: ' + error.message, 'error');
        } finally {
            submitBtn.disabled = false;
            if (submitText) submitText.style.display = 'inline';
            if (submitSpinner) submitSpinner.classList.add('hidden');
        }
    }

    async loadTasks() {
        const taskList = document.getElementById('task-list');
        const emptyTasks = document.getElementById('empty-tasks');
        
        if (!taskList) return;
        
        Utils.showLoading(taskList);
        
        try {
            const tasks = await this.api.getTasks();
            
            if (tasks.length === 0) {
                taskList.classList.add('hidden');
                if (emptyTasks) emptyTasks.classList.remove('hidden');
                return;
            }
            
            taskList.classList.remove('hidden');
            if (emptyTasks) emptyTasks.classList.add('hidden');
            
            taskList.innerHTML = tasks.map(task => this.renderTaskCard(task)).join('');
            
        } catch (error) {
            Utils.showAlert('Ошибка при загрузке задач', 'error');
            taskList.innerHTML = '<div class="text-center py-8 text-red-500">Ошибка загрузки задач</div>';
        }
    }

    renderTaskCard(task) {
        const progressPercent = task.total_items > 0 
            ? Math.round((task.progress / task.total_items) * 100) 
            : 0;
        
        const statusColors = {
            'running': 'bg-green-500',
            'paused': 'bg-yellow-500',
            'completed': 'bg-blue-500',
            'error': 'bg-red-500',
            'created': 'bg-gray-500'
        };
        
        const statusIcons = {
            'running': 'play-circle',
            'paused': 'pause-circle',
            'completed': 'check-circle',
            'error': 'x-circle',
            'created': 'clock'
        };
        
        const actionButtons = this.getTaskActionButtons(task);
        
        return `
            <div class="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 mb-2">
                            Задача ${task.task_id.substring(0, 8)}
                        </h3>
                        <div class="flex items-center gap-3">
                            <span class="${statusColors[task.status]} px-3 py-1 rounded-full text-xs font-medium text-white flex items-center gap-1">
                                <i data-lucide="${statusIcons[task.status]}" class="w-3 h-3"></i>
                                ${this.getStatusText(task.status)}
                            </span>
                            <span class="text-gray-500 text-sm">
                                ${Utils.formatDate(task.created_at, true)}
                            </span>
                        </div>
                    </div>
                    <div class="flex gap-2">
                        ${actionButtons}
                    </div>
                </div>
                
                <div class="mb-4">
                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                        <span>${task.progress} / ${task.total_items} элементов</span>
                        <span>${progressPercent}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div class="h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500"
                             style="width: ${progressPercent}%"></div>
                    </div>
                </div>
                
                ${task.status === 'error' ? `
                    <div class="bg-red-50 border border-red-200 rounded-lg p-3 mt-4">
                        <p class="text-red-800 text-sm flex items-center">
                            <i data-lucide="alert-triangle" class="w-4 h-4 mr-2"></i>
                            ${task.error_message || 'Произошла ошибка при выполнении задачи'}
                        </p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    getTaskActionButtons(task) {
        switch (task.status) {
            case 'running':
                return `<button onclick="taskManager.pauseTask('${task.task_id}')" class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors">
                    <i data-lucide="pause" class="w-4 h-4"></i>
                </button>`;
            case 'paused':
                return `<button onclick="taskManager.resumeTask('${task.task_id}')" class="px-3 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors">
                    <i data-lucide="play" class="w-4 h-4"></i>
                </button>`;
            case 'completed':
                return `<button onclick="taskManager.downloadResults('${task.task_id}')" class="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
                    <i data-lucide="download" class="w-4 h-4"></i>
                </button>`;
            default:
                return '';
        }
    }

    getStatusText(status) {
        const statusMap = {
            'created': 'Создана',
            'running': 'Выполняется',
            'paused': 'На паузе',
            'completed': 'Завершена',
            'error': 'Ошибка'
        };
        return statusMap[status] || status;
    }

    async pauseTask(taskId) {
        try {
            await this.api.pauseTask(taskId);
            Utils.showAlert('Задача поставлена на паузу', 'info');
            await this.loadTasks();
        } catch (error) {
            Utils.showAlert('Ошибка при паузе задачи', 'error');
        }
    }

    async resumeTask(taskId) {
        try {
            await this.api.resumeTask(taskId);
            Utils.showAlert('Задача возобновлена', 'success');
            await this.loadTasks();
        } catch (error) {
            Utils.showAlert('Ошибка при возобновлении задачи', 'error');
        }
    }

    downloadResults(taskId) {
        // В реальном приложении здесь будет скачивание файла
        Utils.showAlert('Функция скачивания результатов в разработке', 'info');
    }
}

// ============ VIDEO MANAGEMENT ============
class VideoManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.videos = [];
        this.filteredVideos = [];
        this.initEventListeners();
    }

    initEventListeners() {
        const searchInput = document.getElementById('video-search');
        if (searchInput) {
            searchInput.addEventListener('keyup', Utils.debounce(this.filterVideos.bind(this), 300));
        }

        const typeFilter = document.getElementById('video-type-filter');
        if (typeFilter) {
            typeFilter.addEventListener('change', this.filterVideos.bind(this));
        }

        const sortSelect = document.getElementById('video-sort');
        if (sortSelect) {
            sortSelect.addEventListener('change', this.sortVideos.bind(this));
        }
    }

    async loadVideos() {
        const videosGrid = document.getElementById('videos-grid');
        const videosLoading = document.getElementById('videos-loading');
        
        if (!videosGrid) return;
        
        if (videosLoading) videosLoading.classList.remove('hidden');
        videosGrid.classList.add('hidden');
        
        try {
            this.videos = await this.api.getVideos();
            this.filteredVideos = [...this.videos];
            this.renderVideos();
            
            if (videosLoading) videosLoading.classList.add('hidden');
            videosGrid.classList.remove('hidden');
            
        } catch (error) {
            Utils.showAlert('Ошибка при загрузке видео', 'error');
            if (videosLoading) {
                videosLoading.innerHTML = '<div class="text-center py-8 text-red-500">Ошибка загрузки видео</div>';
            }
        }
    }

    renderVideos() {
        const videosGrid = document.getElementById('videos-grid');
        if (!videosGrid) return;

        if (this.filteredVideos.length === 0) {
            videosGrid.innerHTML = `
                <div class="col-span-full text-center py-16">
                    <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                        <i data-lucide="video-off" class="w-8 h-8 text-gray-400"></i>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Видео не найдены</h3>
                    <p class="text-gray-500">Попробуйте изменить фильтры или создать новую задачу</p>
                </div>
            `;
            return;
        }

        videosGrid.innerHTML = this.filteredVideos.map(video => this.renderVideoCard(video)).join('');
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    renderVideoCard(video) {
        const engagementClass = video.engagement_rate >= 5 ? 'text-green-600' : 
                               video.engagement_rate >= 2 ? 'text-yellow-600' : 'text-red-600';
        
        return `
            <div class="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                 onclick="videoManager.showVideoDetails('${video.video_id}')">
                <div class="aspect-video bg-gray-100 relative">
                    ${video.thumbnail_url ? `
                        <img src="${video.thumbnail_url}" alt="${video.title}" class="w-full h-full object-cover">
                    ` : `
                        <div class="w-full h-full flex items-center justify-center">
                            <i data-lucide="video" class="w-12 h-12 text-gray-400"></i>
                        </div>
                    `}
                    <div class="absolute bottom-2 right-2">
                        ${video.is_short ? `
                            <span class="bg-red-600 text-white px-2 py-1 rounded text-xs font-medium">SHORT</span>
                        ` : `
                            <span class="bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs">
                                ${Utils.formatDuration(video.duration)}
                            </span>
                        `}
                    </div>
                </div>
                
                <div class="p-4">
                    <h3 class="font-medium text-gray-900 mb-2 line-clamp-2" title="${video.title}">
                        ${video.title}
                    </h3>
                    
                    <p class="text-sm text-gray-600 mb-3">
                        ${video.channel_title || 'Неизвестный канал'}
                    </p>
                    
                    <div class="flex items-center justify-between text-sm text-gray-500 mb-3">
                        <span>${Utils.formatNumber(video.views)} просмотров</span>
                        <span>${Utils.formatDate(video.publish_date, true)}</span>
                    </div>
                    
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3 text-sm">
                            <span class="flex items-center">
                                <i data-lucide="thumbs-up" class="w-4 h-4 mr-1 text-gray-400"></i>
                                ${Utils.formatNumber(video.likes)}
                            </span>
                            <span class="flex items-center">
                                <i data-lucide="message-circle" class="w-4 h-4 mr-1 text-gray-400"></i>
                                ${Utils.formatNumber(video.comments)}
                            </span>
                        </div>
                        
                        <span class="text-sm font-medium ${engagementClass}">
                            ${video.engagement_rate ? video.engagement_rate.toFixed(1) + '%' : '0%'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    filterVideos() {
        const searchTerm = document.getElementById('video-search')?.value.toLowerCase() || '';
        const typeFilter = document.getElementById('video-type-filter')?.value || '';
        
        this.filteredVideos = this.videos.filter(video => {
            const matchesSearch = video.title.toLowerCase().includes(searchTerm) || 
                                video.channel_title.toLowerCase().includes(searchTerm);
            const matchesType = !typeFilter || 
                              (typeFilter === 'short' && video.is_short) || 
                              (typeFilter === 'long' && !video.is_short);
            return matchesSearch && matchesType;
        });
        
        this.renderVideos();
    }

    sortVideos() {
        const sortBy = document.getElementById('video-sort')?.value || 'date';
        
        this.filteredVideos.sort((a, b) => {
            switch(sortBy) {
                case 'views':
                    return b.views - a.views;
                case 'engagement':
                    return (b.engagement_rate || 0) - (a.engagement_rate || 0);
                case 'date':
                default:
                    return new Date(b.analyzed_at || b.created_at) - new Date(a.analyzed_at || a.created_at);
            }
        });
        
        this.renderVideos();
    }

    async showVideoDetails(videoId) {
        try {
            const video = await this.api.getVideoDetails(videoId);
            
            document.getElementById('modalTitle').textContent = video.title;
            document.getElementById('modalBody').innerHTML = this.renderVideoDetails(video);
            document.getElementById('videoModal').classList.remove('hidden');
            
            // Re-initialize Lucide icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            
        } catch (error) {
            Utils.showAlert('Ошибка при загрузке деталей видео', 'error');
        }
    }

    renderVideoDetails(video) {
        return `
            <div class="space-y-6">
                <!-- Basic Info -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Основная информация</h4>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <span class="text-gray-600">Канал:</span>
                                <span>${video.channel_title}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Тип:</span>
                                <span>${video.is_short ? 'SHORT' : 'Обычное видео'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Длительность:</span>
                                <span>${Utils.formatDuration(video.duration)}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Опубликовано:</span>
                                <span>${Utils.formatDate(video.publish_date)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Metrics -->
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Метрики</h4>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <span class="text-gray-600">Просмотры:</span>
                                <span>${Utils.formatNumber(video.views)}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Лайки:</span>
                                <span>${Utils.formatNumber(video.likes)} (${video.like_ratio?.toFixed(2) || 0}%)</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Комментарии:</span>
                                <span>${Utils.formatNumber(video.comments)} (${video.comment_ratio?.toFixed(2) || 0}%)</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Вовлеченность:</span>
                                <span class="font-medium">${video.engagement_rate?.toFixed(2) || 0}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Description -->
                ${video.description ? `
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Описание</h4>
                        <div class="bg-gray-50 rounded-lg p-4 max-h-40 overflow-y-auto">
                            <p class="text-sm text-gray-700 whitespace-pre-wrap">${video.description}</p>
                        </div>
                    </div>
                ` : ''}
                
                <!-- Keywords -->
                ${video.keywords && video.keywords.length > 0 ? `
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Ключевые слова</h4>
                        <div class="flex flex-wrap gap-2">
                            ${video.keywords.map(keyword => `
                                <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">${keyword}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Recommendations -->
                ${video.recommendations ? `
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Рекомендации</h4>
                        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <p class="text-sm text-yellow-800">${video.recommendations}</p>
                        </div>
                    </div>
                ` : ''}
                
                <!-- Analysis -->
                ${video.success_analysis ? `
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Анализ успеха</h4>
                        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                            <p class="text-sm text-green-800">${video.success_analysis}</p>
                        </div>
                    </div>
                ` : ''}
                
                <!-- Actions -->
                <div class="flex justify-between items-center pt-4 border-t border-gray-200">
                    <a href="https://youtube.com/watch?v=${video.video_id}" target="_blank" 
                       class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                        <i data-lucide="external-link" class="w-4 h-4 mr-2"></i>
                        Открыть на YouTube
                    </a>
                    <button onclick="closeModal()" 
                            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                        Закрыть
                    </button>
                </div>
            </div>
        `;
    }
}

// ============ CHANNEL MANAGEMENT ============
class ChannelManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.channels = [];
    }

    async loadChannels() {
        const channelsGrid = document.getElementById('channels-grid');
        if (!channelsGrid) return;
        
        Utils.showLoading(channelsGrid);
        
        try {
            this.channels = await this.api.getChannels();
            this.renderChannels();
        } catch (error) {
            Utils.showAlert('Ошибка при загрузке каналов', 'error');
            channelsGrid.innerHTML = '<div class="col-span-full text-center py-8 text-red-500">Ошибка загрузки каналов</div>';
        }
    }

    renderChannels() {
        const channelsGrid = document.getElementById('channels-grid');
        if (!channelsGrid) return;

        if (this.channels.length === 0) {
            channelsGrid.innerHTML = `
                <div class="col-span-full text-center py-16">
                    <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                        <i data-lucide="tv" class="w-8 h-8 text-gray-400"></i>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Нет проанализированных каналов</h3>
                    <p class="text-gray-500">Создайте задачу для анализа каналов</p>
                </div>
            `;
            return;
        }

        channelsGrid.innerHTML = this.channels.map(channel => this.renderChannelCard(channel)).join('');
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    renderChannelCard(channel) {
        return `
            <div class="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                <div class="flex items-center space-x-4 mb-4">
                    <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                        <i data-lucide="tv" class="w-6 h-6 text-red-600"></i>
                    </div>
                    <div class="flex-1">
                        <h3 class="font-semibold text-gray-900 mb-1">${channel.channel_title}</h3>
                        <p class="text-sm text-gray-500">${Utils.formatNumber(channel.subscriber_count)} подписчиков</p>
                    </div>
                </div>
                
                <div class="space-y-3 mb-4">
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-600">Видео:</span>
                        <span>${Utils.formatNumber(channel.video_count)}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-600">Просмотры:</span>
                        <span>${Utils.formatNumber(channel.view_count)}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-600">Проанализировано:</span>
                        <span class="font-medium">${channel.analyzed_videos}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-600">Средние просмотры:</span>
                        <span>${Utils.formatNumber(channel.avg_views || 0)}</span>
                    </div>
                </div>
                
                <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500">
                        Обновлено: ${Utils.formatDate(channel.last_updated, true)}
                    </span>
                    <a href="${channel.channel_url}" target="_blank" 
                       class="inline-flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm">
                        <i data-lucide="external-link" class="w-3 h-3 mr-1"></i>
                        Открыть
                    </a>
                </div>
            </div>
        `;
    }
}

// ============ CONFIG MANAGEMENT ============
class ConfigManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.initEventListeners();
    }

    initEventListeners() {
        const configForm = document.getElementById('config-form');
        if (configForm) {
            configForm.addEventListener('submit', this.handleConfigSubmit.bind(this));
        }
    }

    async loadConfig() {
        try {
            const config = await this.api.getConfig();
            this.populateConfigForm(config);
        } catch (error) {
            Utils.showAlert('Ошибка при загрузке конфигурации', 'error');
        }
    }

    populateConfigForm(config) {
        const form = document.getElementById('config-form');
        if (!form) return;

        // Заполнить поля формы
        Object.keys(config).forEach(key => {
            const input = form.querySelector(`#${key.toLowerCase().replace(/_/g, '-')}`);
            if (input) {
                if (key === 'YOUTUBE_API_KEY' && config[key] === '***') {
                    input.value = '';
                    input.placeholder = 'API ключ установлен';
                } else {
                    input.value = config[key];
                }
            }
        });
    }

    async handleConfigSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const config = {};
        
        for (const [key, value] of formData.entries()) {
            const configKey = key.replace(/-/g, '_');
            config[configKey] = value;
        }
        
        try {
            await this.api.updateConfig(config);
            Utils.showAlert('Конфигурация успешно обновлена', 'success');
        } catch (error) {
            Utils.showAlert('Ошибка при обновлении конфигурации: ' + error.message, 'error');
        }
    }
}

// ============ STATS MANAGEMENT ============
class StatsManager {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async loadStats() {
        try {
            const stats = await this.api.getStats();
            this.renderStats(stats);
        } catch (error) {
            Utils.showAlert('Ошибка при загрузке статистики', 'error');
        }
    }

    renderStats(stats) {
        // Обновить числовые значения с анимацией
        this.animateNumber('total-videos', stats.total_videos || 0);
        this.animateNumber('total-channels', stats.total_channels || 0);
        this.animateNumber('total-tasks', stats.completed_tasks || 0);
        
        // Обновить процент вовлеченности
        const avgEngagementEl = document.getElementById('avg-engagement');
        if (avgEngagementEl) {
            avgEngagementEl.textContent = `${stats.avg_engagement || 0}%`;
        }
        
        // Показать блок экспорта если есть данные
        const exportInfo = document.getElementById('export-info');
        if (exportInfo && stats.total_videos > 0) {
            exportInfo.style.display = 'block';
        }
    }

    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 секунда
        const increment = (targetValue - startValue) / (duration / 16);
        let currentValue = startValue;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if ((increment > 0 && currentValue >= targetValue) || 
                (increment < 0 && currentValue <= targetValue)) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            element.textContent = Math.round(currentValue);
        }, 16);
    }

    async downloadExport() {
        try {
            const response = await this.api.exportData();
            Utils.showAlert(`Экспорт завершен: ${response.filename}`, 'success');
        } catch (error) {
            Utils.showAlert('Ошибка при экспорте данных', 'error');
        }
    }

    async clearDatabase() {
        const confirmed = confirm(
            'Вы уверены, что хотите очистить базу данных?\n\n' +
            'Это действие удалит:\n' +
            '• Все проанализированные видео\n' +
            '• Информацию о каналах\n' +
            '• Историю задач\n\n' +
            'Это действие необратимо!'
        );
        
        if (confirmed) {
            try {
                await this.api.clearDatabase();
                Utils.showAlert('База данных успешно очищена', 'success');
                await this.loadStats();
            } catch (error) {
                Utils.showAlert('Ошибка при очистке базы данных', 'error');
            }
        }
    }
}

// ============ GLOBAL FUNCTIONS ============
function closeModal() {
    const modal = document.getElementById('videoModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('api-key');
    const toggle = document.getElementById('api-key-toggle');
    
    if (input && toggle) {
        if (input.type === 'password') {
            input.type = 'text';
            toggle.setAttribute('data-lucide', 'eye-off');
        } else {
            input.type = 'password';
            toggle.setAttribute('data-lucide', 'eye');
        }
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

function resetConfig() {
    const confirmed = confirm('Вы уверены, что хотите сбросить настройки к значениям по умолчанию?');
    if (confirmed) {
        const form = document.getElementById('config-form');
        if (form) {
            form.reset();
            // Установить значения по умолчанию
            const defaults = {
                'max-long-channel': 5,
                'max-long-search': 5,
                'max-shorts-channel': 5,
                'max-shorts-search': 5,
                'whisper-model': 'base',
                'max-transcript': 50000
            };
            
            Object.keys(defaults).forEach(key => {
                const input = form.querySelector(`#${key}`);
                if (input) {
                    input.value = defaults[key];
                }
            });
            
            Utils.showAlert('Настройки сброшены к значениям по умолчанию', 'info');
        }
    }
}

// ============ INITIALIZATION ============
let apiClient;
let tabManager;
let taskManager;
let videoManager;
let channelManager;
let configManager;
let statsManager;

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize API client
    apiClient = new ApiClient();
    
    // Initialize managers
    tabManager = new TabManager();
    taskManager = new TaskManager(apiClient);
    videoManager = new VideoManager(apiClient);
    channelManager = new ChannelManager(apiClient);
    configManager = new ConfigManager(apiClient);
    statsManager = new StatsManager(apiClient);
    
    // Load initial configuration
    try {
        const config = await apiClient.getConfig();
        STATE.config = config;
    } catch (error) {
        console.error('Error loading initial config:', error);
    }
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Set up auto-update for tasks
    setInterval(async () => {
        if (STATE.currentTab === 'tasks') {
            await taskManager.loadTasks();
        }
    }, CONFIG.UPDATE_INTERVAL);
    
    // Handle modal clicks
    document.addEventListener('click', (e) => {
        const modal = document.getElementById('videoModal');
        if (modal && e.target === modal) {
            closeModal();
        }
    });
    
    console.log('✅ YouTube Analyzer Frontend загружен успешно');
});

// Export for global access
window.taskManager = taskManager;
window.videoManager = videoManager;
window.channelManager = channelManager;
window.configManager = configManager;
window.statsManager = statsManager;
window.closeModal = closeModal;
window.toggleApiKeyVisibility = toggleApiKeyVisibility;
window.resetConfig = resetConfig;