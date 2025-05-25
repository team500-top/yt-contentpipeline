const { createApp } = Vue;

createApp({
    data() {
        return {
            // Navigation
            activeTab: 'parsing',
            tabs: [
                { id: 'parsing', name: 'Парсинг' },
                { id: 'videos', name: 'Видео', badge: 0 },
                { id: 'tasks', name: 'Задачи', badge: 0 },
                { id: 'analytics', name: 'Аналитика' },
                { id: 'settings', name: 'Настройки' }
            ],
            
            // Search form
            searchForm: {
                type: 'keyword',
                query: '',
                videoType: 'all',
                sort: 'relevance',
                maxResults: 50
            },
            isSearching: false,
            
            // Videos
            videos: [],
            selectedVideo: null,
            viewMode: 'table',
            videoFilters: {
                search: '',
                type: '',
                sort: 'date'
            },
            
            // Tasks
            tasks: [],
            
            // Analytics
            stats: {
                totalVideos: 0,
                totalChannels: 0,
                avgEngagement: 0,
                topCategory: 'Не определено',
                videosThisWeek: 0
            },
            topVideos: [],
            
            // Settings
            settings: {
                youtubeApiKey: '',
                autoRetry: true,
                requestDelay: 3
            },
            
            // UI State
            notification: null,
            currentTime: '',
            recentQueries: [],
            
            // WebSocket
            ws: null,
            reconnectInterval: null
        };
    },
    
    computed: {
        filteredVideos() {
            let filtered = [...this.videos];
            
            // Search filter
            if (this.videoFilters.search) {
                const search = this.videoFilters.search.toLowerCase();
                filtered = filtered.filter(v => 
                    v.title.toLowerCase().includes(search) ||
                    v.channel_name?.toLowerCase().includes(search)
                );
            }
            
            // Type filter
            if (this.videoFilters.type === 'shorts') {
                filtered = filtered.filter(v => v.is_short);
            } else if (this.videoFilters.type === 'long') {
                filtered = filtered.filter(v => !v.is_short);
            }
            
            // Sorting
            filtered.sort((a, b) => {
                switch (this.videoFilters.sort) {
                    case 'views':
                        return b.views - a.views;
                    case 'engagement':
                        return b.engagement_rate - a.engagement_rate;
                    case 'date':
                    default:
                        return new Date(b.publish_date) - new Date(a.publish_date);
                }
            });
            
            return filtered;
        },
        
        activeTasks() {
            return this.tasks.filter(t => ['running', 'paused'].includes(t.status));
        }
    },
    
    mounted() {
        this.initializeApp();
        this.startClock();
        this.connectWebSocket();
        this.loadData();
        
        // Update badges
        this.updateBadges();
        
        // Auto-refresh tasks every 2 seconds if active tasks
        setInterval(() => {
            if (this.activeTab === 'tasks' && this.activeTasks.length > 0) {
                this.loadTasks();
            }
        }, 2000);
        
        // Auto-refresh videos every 5 seconds if on videos tab
        setInterval(() => {
            if (this.activeTab === 'videos') {
                this.loadVideos();
            }
        }, 5000);
    },
    
    beforeUnmount() {
        if (this.ws) {
            this.ws.close();
        }
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
        }
    },
    
    methods: {
        // Initialization
        async initializeApp() {
            try {
                const response = await axios.get('/api/settings');
                this.settings = response.data;
            } catch (error) {
                console.error('Failed to load settings:', error);
            }
        },
        
        // WebSocket connection
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                if (this.reconnectInterval) {
                    clearInterval(this.reconnectInterval);
                    this.reconnectInterval = null;
                }
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                // Reconnect after 5 seconds
                if (!this.reconnectInterval) {
                    this.reconnectInterval = setInterval(() => {
                        this.connectWebSocket();
                    }, 5000);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        },
        
        handleWebSocketMessage(data) {
            console.log('WebSocket message:', data);
            
            switch (data.type) {
                case 'task_update':
                    this.updateTask(data.task);
                    if (this.activeTab === 'parsing' || this.activeTab === 'tasks') {
                        this.showNotification({
                            type: 'info',
                            title: 'Прогресс задачи',
                            message: `Обработано ${data.task.processed_items} из ${data.task.total_items} видео`
                        });
                    }
                    break;
                    
                case 'video_added':
                    // Добавляем видео в начало списка
                    const existingIndex = this.videos.findIndex(v => v.id === data.video.id);
                    if (existingIndex === -1) {
                        this.videos.unshift(data.video);
                        this.updateBadges();
                        
                        if (this.activeTab === 'videos') {
                            this.showNotification({
                                type: 'success',
                                title: 'Новое видео',
                                message: `Добавлено: ${data.video.title}`
                            });
                        }
                    }
                    break;
                    
                case 'notification':
                    this.showNotification(data.notification);
                    break;
            }
        },
        
        // Clock
        startClock() {
            const updateTime = () => {
                const now = new Date();
                this.currentTime = now.toLocaleString('ru-RU', {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            };
            updateTime();
            setInterval(updateTime, 1000);
        },
        
        // Data loading
        async loadData() {
            await Promise.all([
                this.loadVideos(),
                this.loadTasks(),
                this.loadRecentQueries(),
                this.loadStats()
            ]);
        },
        
        async loadVideos() {
            try {
                const response = await axios.get('/api/videos');
                this.videos = response.data.videos || [];
                this.updateBadges();
            } catch (error) {
                console.error('Failed to load videos:', error);
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось загрузить видео'
                });
            }
        },
        
        async loadTasks() {
            try {
                const response = await axios.get('/api/tasks');
                this.tasks = response.data;
                this.updateBadges();
            } catch (error) {
                console.error('Failed to load tasks:', error);
            }
        },
        
        async loadRecentQueries() {
            try {
                const response = await axios.get('/api/search-queries?limit=5');
                this.recentQueries = response.data;
            } catch (error) {
                console.error('Failed to load recent queries:', error);
            }
        },
        
        async loadStats() {
            try {
                const response = await axios.get('/api/analytics/stats');
                this.stats = response.data.stats;
                this.topVideos = response.data.topVideos;
                
                // Update charts if on analytics tab
                if (this.activeTab === 'analytics') {
                    this.$nextTick(() => {
                        this.updateCharts();
                    });
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        },
        
        // Parsing
        async startParsing() {
            if (!this.searchForm.query) return;
            
            this.isSearching = true;
            
            try {
                const response = await axios.post('/api/parse', this.searchForm);
                const task = response.data;
                
                this.tasks.unshift(task);
                this.updateBadges();
                
                // Save to recent queries
                this.recentQueries.unshift({
                    id: Date.now(),
                    query: this.searchForm.query,
                    type: this.searchForm.type,
                    results: 0,
                    date: new Date()
                });
                
                this.showNotification({
                    type: 'success',
                    title: 'Парсинг запущен',
                    message: `Задача создана: ${this.searchForm.query}`
                });
                
                // Switch to tasks tab
                this.activeTab = 'tasks';
                
                // Clear form
                this.searchForm.query = '';
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: error.response?.data?.detail || 'Не удалось запустить парсинг'
                });
            } finally {
                this.isSearching = false;
            }
        },
        
        repeatSearch(query) {
            this.searchForm = {
                ...this.searchForm,
                type: query.type,
                query: query.query
            };
        },
        
        // Videos
        viewVideo(video) {
            this.selectedVideo = video;
        },
        
        async analyzeVideo(video) {
            try {
                const response = await axios.post(`/api/videos/${video.id}/analyze`);
                this.showNotification({
                    type: 'success',
                    title: 'Анализ запущен',
                    message: 'Результаты будут доступны через несколько минут'
                });
                this.selectedVideo = null;
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось запустить анализ'
                });
            }
        },
        
        async transcribeVideo(video) {
            if (!confirm(`Начать транскрибацию видео "${video.title}"?`)) return;
            
            try {
                const response = await axios.post(`/api/videos/${video.id}/transcribe`);
                this.showNotification({
                    type: 'success',
                    title: 'Транскрибация запущена',
                    message: 'Процесс может занять несколько минут'
                });
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось запустить транскрибацию'
                });
            }
        },
        
        async exportVideos() {
            try {
                const format = await this.selectExportFormat();
                if (!format) return;
                
                const response = await axios.get(`/api/videos/export?format=${format}`, {
                    responseType: 'blob'
                });
                
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                
                const extensions = {
                    'csv': 'csv',
                    'json': 'json',
                    'excel': 'xlsx'
                };
                
                link.setAttribute('download', `youtube_analysis_${new Date().toISOString().split('T')[0]}.${extensions[format]}`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                
                this.showNotification({
                    type: 'success',
                    title: 'Экспорт завершен',
                    message: 'Файл загружен'
                });
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось экспортировать данные'
                });
            }
        },
        
        async selectExportFormat() {
            // Простой диалог выбора формата
            const format = prompt('Выберите формат экспорта:\n1. Excel (рекомендуется)\n2. CSV\n3. JSON\n\nВведите номер (1-3):');
            const formats = {
                '1': 'excel',
                '2': 'csv',
                '3': 'json'
            };
            return formats[format] || null;
        },
        
        resetFilters() {
            this.videoFilters = {
                search: '',
                type: '',
                sort: 'date'
            };
        },
        
        // Tasks
        async pauseTask(taskId) {
            try {
                await axios.post(`/api/tasks/${taskId}/pause`);
                const task = this.tasks.find(t => t.id === taskId);
                if (task) task.status = 'paused';
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось приостановить задачу'
                });
            }
        },
        
        async resumeTask(taskId) {
            try {
                await axios.post(`/api/tasks/${taskId}/resume`);
                const task = this.tasks.find(t => t.id === taskId);
                if (task) task.status = 'running';
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось возобновить задачу'
                });
            }
        },
        
        async cancelTask(taskId) {
            if (!confirm('Вы уверены, что хотите отменить эту задачу?')) return;
            
            try {
                await axios.post(`/api/tasks/${taskId}/cancel`);
                this.tasks = this.tasks.filter(t => t.id !== taskId);
                this.updateBadges();
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось отменить задачу'
                });
            }
        },
        
        async pauseAllTasks() {
            try {
                await axios.post('/api/tasks/pause-all');
                this.tasks.forEach(task => {
                    if (task.status === 'running') {
                        task.status = 'paused';
                    }
                });
                this.showNotification({
                    type: 'success',
                    title: 'Задачи приостановлены',
                    message: 'Все активные задачи приостановлены'
                });
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось приостановить задачи'
                });
            }
        },
        
        async resumeAllTasks() {
            try {
                await axios.post('/api/tasks/resume-all');
                this.tasks.forEach(task => {
                    if (task.status === 'paused') {
                        task.status = 'running';
                    }
                });
                this.showNotification({
                    type: 'success',
                    title: 'Задачи возобновлены',
                    message: 'Все приостановленные задачи возобновлены'
                });
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось возобновить задачи'
                });
            }
        },
        
        async clearCompletedTasks() {
            try {
                await axios.delete('/api/tasks/completed');
                this.tasks = this.tasks.filter(t => !['completed', 'failed'].includes(t.status));
                this.updateBadges();
                this.showNotification({
                    type: 'success',
                    title: 'Очищено',
                    message: 'Завершенные задачи удалены'
                });
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось очистить задачи'
                });
            }
        },
        
        updateTask(updatedTask) {
            const index = this.tasks.findIndex(t => t.id === updatedTask.id);
            if (index !== -1) {
                // Обновляем существующую задачу
                Object.assign(this.tasks[index], updatedTask);
            } else {
                // Добавляем новую задачу
                this.tasks.unshift(updatedTask);
            }
            this.updateBadges();
        },
        
        // Settings
        async saveSettings() {
            try {
                await axios.post('/api/settings', this.settings);
                this.showNotification({
                    type: 'success',
                    title: 'Сохранено',
                    message: 'Настройки успешно сохранены'
                });
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось сохранить настройки'
                });
            }
        },
        
        async exportDatabase() {
            try {
                const response = await axios.get('/api/export/database', {
                    responseType: 'blob'
                });
                
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `youtube_analyzer_backup_${new Date().toISOString().split('T')[0]}.zip`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                
                this.showNotification({
                    type: 'success',
                    title: 'Экспорт завершен',
                    message: 'База данных экспортирована'
                });
            } catch (error) {
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка',
                    message: 'Не удалось экспортировать базу данных'
                });
            }
        },
        
        async importDatabase() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.zip';
            
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    await axios.post('/api/import/database', formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    });
                    
                    this.showNotification({
                        type: 'success',
                        title: 'Импорт завершен',
                        message: 'База данных импортирована. Перезагрузка...'
                    });
                    
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } catch (error) {
                    this.showNotification({
                        type: 'error',
                        title: 'Ошибка',
                        message: 'Не удалось импортировать базу данных'
                    });
                }
            };
            
            input.click();
        },
        
        // Charts
        updateCharts() {
            // Views trend chart
            const viewsCtx = document.getElementById('viewsChart');
            if (viewsCtx) {
                new Chart(viewsCtx, {
                    type: 'line',
                    data: {
                        labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                        datasets: [{
                            label: 'Просмотры',
                            data: [65000, 72000, 68000, 85000, 92000, 88000, 95000],
                            borderColor: 'rgb(239, 68, 68)',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
            
            // Type distribution chart
            const typeCtx = document.getElementById('typeChart');
            if (typeCtx) {
                const shortsCount = this.videos.filter(v => v.is_short).length;
                const longCount = this.videos.filter(v => !v.is_short).length;
                
                new Chart(typeCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Shorts', 'Длинные видео'],
                        datasets: [{
                            data: [shortsCount, longCount],
                            backgroundColor: [
                                'rgb(139, 92, 246)',
                                'rgb(239, 68, 68)'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        },
        
        // Helpers
        formatDuration(duration) {
            if (!duration) return '-';
            // Преобразование ISO 8601 в читаемый формат
            const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
            if (!match) return duration;
            
            const hours = match[1] || 0;
            const minutes = match[2] || 0;
            const seconds = match[3] || 0;
            
            if (hours > 0) {
                return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }
            return `${minutes}:${String(seconds).padStart(2, '0')}`;
        },
        
        getEngagementClass(rate) {
            if (rate >= 10) return 'text-green-600 font-bold';
            if (rate >= 5) return 'text-green-600';
            if (rate >= 2) return 'text-yellow-600';
            if (rate >= 1) return 'text-orange-600';
            return 'text-red-600';
        },
        
        // UI Helpers
        updateBadges() {
            this.tabs[1].badge = this.videos.length;
            this.tabs[2].badge = this.activeTasks.length;
        },
        
        showNotification(notification) {
            this.notification = notification;
            setTimeout(() => {
                this.notification = null;
            }, 5000);
        },
        
        formatNumber(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toString();
        },
        
        formatDate(date) {
            if (!date) return '';
            const d = new Date(date);
            const now = new Date();
            const diff = now - d;
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            
            if (days === 0) return 'Сегодня';
            if (days === 1) return 'Вчера';
            if (days < 7) return `${days} дней назад`;
            if (days < 30) return `${Math.floor(days / 7)} недель назад`;
            if (days < 365) return `${Math.floor(days / 30)} месяцев назад`;
            
            return d.toLocaleDateString('ru-RU');
        },
        
        getTaskTypeName(type) {
            const types = {
                'search': 'Поиск по ключевым словам',
                'channel_parse': 'Парсинг канала',
                'video_parse': 'Парсинг видео',
                'analysis': 'Анализ контента'
            };
            return types[type] || type;
        },
        
        getTaskStatusName(status) {
            const statuses = {
                'pending': 'Ожидание',
                'running': 'Выполняется',
                'paused': 'Приостановлено',
                'completed': 'Завершено',
                'failed': 'Ошибка'
            };
            return statuses[status] || status;
        },
        
        getTaskStatusClass(status) {
            const classes = {
                'pending': 'bg-gray-100 text-gray-800',
                'running': 'bg-blue-100 text-blue-800',
                'paused': 'bg-yellow-100 text-yellow-800',
                'completed': 'bg-green-100 text-green-800',
                'failed': 'bg-red-100 text-red-800'
            };
            return classes[status] || 'bg-gray-100 text-gray-800';
        }
    }
}).mount('#app');