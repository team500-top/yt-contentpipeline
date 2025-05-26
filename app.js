const { createApp } = Vue;

createApp({
    data() {
        return {
            // Navigation
            activeTab: 'parsing',
            tabs: [
                { id: 'parsing', name: 'Парсинг' },
                { id: 'videos', name: 'Видео', badge: 0 },
                { id: 'channels', name: 'Каналы', badge: 0 },
                { id: 'tasks', name: 'Задачи', badge: 0 },
                { id: 'analytics', name: 'Аналитика' },
                { id: 'settings', name: 'Настройки' },
                { id: 'help', name: 'Справка' }
            ],
            
            // Search form с расширенными параметрами
            searchForm: {
                type: 'keyword',
                query: '',
                videoType: 'all',
                sort: 'relevance',
                maxResults: 50,
                // Новые параметры фильтрации
                duration: '', // short, medium, long
                publishedAfter: '', // дата
                videoDefinition: '', // hd, sd
                videoDimension: '', // 2d, 3d
                videoCaption: '', // closedCaption, none
                regionCode: 'RU',
                relevanceLanguage: 'ru'
            },
            isSearching: false,
            
            // Videos
            videos: [],
            selectedVideo: null,
            viewMode: 'table',
            showFilters: false,
            
            // Расширенные фильтры для видео
            videoFilters: {
                // Основные
                search: '',
                type: '',
                category: '',
                sort: 'date',
                
                // Метрики
                viewsMin: null,
                viewsMax: null,
                engagementMin: null,
                engagementMax: null,
                dateFrom: '',
                dateTo: '',
                
                // Контент
                hasSubtitles: false,
                hasChapters: false,
                hasEmoji: false,
                hasBranding: false,
                hasPinnedComment: false,
                hasIntro: false,
                hasOutro: false,
                hasAnalysis: false,
                
                // Канал
                channelAvgViewsMin: null,
                channelAvgViewsMax: null,
                channelFrequencyMin: null,
                channelFrequencyMax: null,
                quality: ''
            },
            
            // Channels
            channels: [],
            selectedChannel: null,
            channelViewMode: 'table',
            channelFilters: {
                search: '',
                sort: 'subscribers'
            },
            
            // Table scroll sync
            tableWidth: 2000,
            scrollPositions: {
                top: 0,
                bottom: 0
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
            
            // Settings - расширенные настройки из .env
            settings: {
                // API Keys
                youtubeApiKey: '',
                
                // Database
                databasePath: '',
                
                // Server
                host: '127.0.0.1',
                port: 8000,
                debug: true,
                
                // Directories
                tempDir: 'temp',
                exportDir: 'exports',
                logsDir: 'logs',
                
                // Redis
                redisUrl: '',
                celeryBrokerUrl: '',
                celeryResultBackend: '',
                
                // API Limits
                maxResultsPerSearch: 500,
                apiRequestDelay: 3,
                
                // Export
                exportPageSize: 1000,
                maxExportRows: 50000,
                
                // Features
                enableDeepAnalysis: true,
                enableWebsocket: true,
                enableAutoRetry: true,
                
                // Security
                secretKey: '',
                jwtAlgorithm: 'HS256',
                accessTokenExpireMinutes: 30
            },
            
            // UI State
            notification: null,
            currentTime: '',
            recentQueries: [],
            showExportMenu: false,
            showChannelExportMenu: false,
            
            // WebSocket
            ws: null,
            reconnectInterval: null
        };
    },
    
    computed: {
        filteredVideos() {
            let filtered = [...this.videos];
            
            // Основные фильтры
            if (this.videoFilters.search) {
                const search = this.videoFilters.search.toLowerCase();
                filtered = filtered.filter(v => 
                    v.title.toLowerCase().includes(search) ||
                    v.channel_name?.toLowerCase().includes(search) ||
                    v.description?.toLowerCase().includes(search)
                );
            }
            
            // Тип видео
            if (this.videoFilters.type === 'shorts') {
                filtered = filtered.filter(v => v.is_short);
            } else if (this.videoFilters.type === 'long') {
                filtered = filtered.filter(v => !v.is_short);
            }
            
            // Категория
            if (this.videoFilters.category) {
                filtered = filtered.filter(v => v.video_category === this.videoFilters.category);
            }
            
            // Метрики - Просмотры
            if (this.videoFilters.viewsMin !== null && this.videoFilters.viewsMin !== '') {
                filtered = filtered.filter(v => v.views >= this.videoFilters.viewsMin);
            }
            if (this.videoFilters.viewsMax !== null && this.videoFilters.viewsMax !== '') {
                filtered = filtered.filter(v => v.views <= this.videoFilters.viewsMax);
            }
            
            // Метрики - Вовлеченность
            if (this.videoFilters.engagementMin !== null && this.videoFilters.engagementMin !== '') {
                filtered = filtered.filter(v => v.engagement_rate >= this.videoFilters.engagementMin);
            }
            if (this.videoFilters.engagementMax !== null && this.videoFilters.engagementMax !== '') {
                filtered = filtered.filter(v => v.engagement_rate <= this.videoFilters.engagementMax);
            }
            
            // Даты
            if (this.videoFilters.dateFrom) {
                const dateFrom = new Date(this.videoFilters.dateFrom);
                filtered = filtered.filter(v => new Date(v.publish_date) >= dateFrom);
            }
            if (this.videoFilters.dateTo) {
                const dateTo = new Date(this.videoFilters.dateTo);
                filtered = filtered.filter(v => new Date(v.publish_date) <= dateTo);
            }
            
            // Контент фильтры
            if (this.videoFilters.hasSubtitles) {
                filtered = filtered.filter(v => v.has_cc);
            }
            if (this.videoFilters.hasChapters) {
                filtered = filtered.filter(v => v.has_chapters);
            }
            if (this.videoFilters.hasEmoji) {
                filtered = filtered.filter(v => v.emoji_in_title);
            }
            if (this.videoFilters.hasBranding) {
                filtered = filtered.filter(v => v.has_branding);
            }
            if (this.videoFilters.hasPinnedComment) {
                filtered = filtered.filter(v => v.has_pinned_comment);
            }
            if (this.videoFilters.hasIntro) {
                filtered = filtered.filter(v => v.has_intro);
            }
            if (this.videoFilters.hasOutro) {
                filtered = filtered.filter(v => v.has_outro);
            }
            if (this.videoFilters.hasAnalysis) {
                filtered = filtered.filter(v => v.improvement_recommendations && v.improvement_recommendations.length > 0);
            }
            
            // Канал фильтры
            if (this.videoFilters.channelAvgViewsMin !== null && this.videoFilters.channelAvgViewsMin !== '') {
                filtered = filtered.filter(v => (v.channel_avg_views || 0) >= this.videoFilters.channelAvgViewsMin);
            }
            if (this.videoFilters.channelAvgViewsMax !== null && this.videoFilters.channelAvgViewsMax !== '') {
                filtered = filtered.filter(v => (v.channel_avg_views || 0) <= this.videoFilters.channelAvgViewsMax);
            }
            if (this.videoFilters.channelFrequencyMin !== null && this.videoFilters.channelFrequencyMin !== '') {
                filtered = filtered.filter(v => (v.channel_frequency || 0) >= this.videoFilters.channelFrequencyMin);
            }
            if (this.videoFilters.channelFrequencyMax !== null && this.videoFilters.channelFrequencyMax !== '') {
                filtered = filtered.filter(v => (v.channel_frequency || 0) <= this.videoFilters.channelFrequencyMax);
            }
            
            // Качество
            if (this.videoFilters.quality) {
                filtered = filtered.filter(v => v.video_quality === this.videoFilters.quality);
            }
            
            // Сортировка
            filtered.sort((a, b) => {
                switch (this.videoFilters.sort) {
                    case 'views':
                        return b.views - a.views;
                    case 'likes':
                        return b.likes - a.likes;
                    case 'comments':
                        return b.comments - a.comments;
                    case 'engagement':
                        return b.engagement_rate - a.engagement_rate;
                    case 'date':
                    default:
                        return new Date(b.publish_date) - new Date(a.publish_date);
                }
            });
            
            return filtered;
        },
        
        filteredChannels() {
            let filtered = [...this.channels];
            
            // Поиск
            if (this.channelFilters.search) {
                const search = this.channelFilters.search.toLowerCase();
                filtered = filtered.filter(c => 
                    c.title.toLowerCase().includes(search) ||
                    c.description?.toLowerCase().includes(search)
                );
            }
            
            // Сортировка
            filtered.sort((a, b) => {
                switch (this.channelFilters.sort) {
                    case 'subscribers':
                        return b.subscriber_count - a.subscriber_count;
                    case 'videos':
                        return b.video_count - a.video_count;
                    case 'views':
                        return b.view_count - a.view_count;
                    case 'date':
                    default:
                        return new Date(b.created_date || 0) - new Date(a.created_date || 0);
                }
            });
            
            return filtered;
        },
        
        // Количество активных фильтров
        activeFiltersCount() {
            let count = 0;
            const filters = this.videoFilters;
            
            if (filters.search) count++;
            if (filters.type) count++;
            if (filters.category) count++;
            if (filters.viewsMin || filters.viewsMax) count++;
            if (filters.engagementMin || filters.engagementMax) count++;
            if (filters.dateFrom || filters.dateTo) count++;
            if (filters.quality) count++;
            if (filters.channelAvgViewsMin || filters.channelAvgViewsMax) count++;
            if (filters.channelFrequencyMin || filters.channelFrequencyMax) count++;
            
            // Boolean filters
            const booleanFilters = [
                'hasSubtitles', 'hasChapters', 'hasEmoji', 'hasBranding',
                'hasPinnedComment', 'hasIntro', 'hasOutro', 'hasAnalysis'
            ];
            booleanFilters.forEach(filter => {
                if (filters[filter]) count++;
            });
            
            return count;
        },
        
        // Computed properties for tasks
        activeTasks() {
            return this.tasks.filter(t => t.status === 'running');
        },
        
        pausedTasks() {
            return this.tasks.filter(t => t.status === 'paused');
        },
        
        completedTasks() {
            return this.tasks.filter(t => ['completed', 'failed', 'cancelled'].includes(t.status));
        }
    },
    
    mounted() {
        this.initializeApp();
        this.startClock();
        this.connectWebSocket();
        this.loadData();
        
        // Update badges
        this.updateBadges();
        
        // Auto-refresh tasks
        setInterval(() => {
            if (this.activeTab === 'tasks' && this.activeTasks.length > 0) {
                this.loadTasks();
            }
        }, 2000);
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
            switch (data.type) {
                case 'task_update':
                    this.updateTask(data.task);
                    break;
                case 'video_added':
                    this.videos.unshift(data.video);
                    this.updateBadges();
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
                this.loadChannels(),
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
        
        async loadChannels() {
            try {
                const response = await axios.get('/api/channels');
                this.channels = response.data.channels || [];
                this.updateBadges();
            } catch (error) {
                console.error('Failed to load channels:', error);
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
        
        viewChannel(channel) {
            this.selectedChannel = channel;
        },
        
        // ИСПРАВЛЕННЫЙ экспорт видео
        async exportVideos(format = 'excel') {
            try {
                // Получаем отфильтрованные видео
                const videosToExport = this.filteredVideos;
                
                if (videosToExport.length === 0) {
                    this.showNotification({
                        type: 'warning',
                        title: 'Нет данных',
                        message: 'Нет видео для экспорта с текущими фильтрами'
                    });
                    return;
                }
                
                // Формируем параметры запроса с ID отфильтрованных видео
                const videoIds = videosToExport.map(v => v.id).join(',');
                const url = `/api/videos/export?format=${format}&ids=${videoIds}`;
                
                // Создаем ссылку для скачивания
                const link = document.createElement('a');
                link.href = url;
                
                // Имя файла с датой и количеством записей
                const date = new Date().toISOString().split('T')[0];
                let extension = 'xlsx';
                if (format === 'csv') extension = 'csv';
                else if (format === 'json') extension = 'json';
                
                const filename = `youtube_analysis_${date}_${videosToExport.length}_videos.${extension}`;
                link.setAttribute('download', filename);
                
                document.body.appendChild(link);
                link.click();
                link.remove();
                
                this.showNotification({
                    type: 'success',
                    title: 'Экспорт запущен',
                    message: `Экспортируется ${videosToExport.length} видео в формате ${format.toUpperCase()}`
                });
            } catch (error) {
                console.error('Export error:', error);
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка экспорта',
                    message: 'Не удалось экспортировать данные. Проверьте консоль для деталей.'
                });
            }
        },
        
        // Экспорт каналов
        async exportChannels(format = 'excel') {
            try {
                const url = `/api/channels/export?format=${format}`;
                
                const link = document.createElement('a');
                link.href = url;
                
                const date = new Date().toISOString().split('T')[0];
                let extension = 'xlsx';
                if (format === 'csv') extension = 'csv';
                else if (format === 'json') extension = 'json';
                
                const filename = `youtube_channels_${date}.${extension}`;
                link.setAttribute('download', filename);
                
                document.body.appendChild(link);
                link.click();
                link.remove();
                
                this.showNotification({
                    type: 'success',
                    title: 'Экспорт запущен',
                    message: `Экспортируются каналы в формате ${format.toUpperCase()}`
                });
            } catch (error) {
                console.error('Export error:', error);
                this.showNotification({
                    type: 'error',
                    title: 'Ошибка экспорта',
                    message: 'Не удалось экспортировать каналы'
                });
            }
        },
        
        // Фильтры
        toggleFilters() {
            this.showFilters = !this.showFilters;
        },
        
        applyFilters() {
            // Фильтры применяются автоматически через computed property
            this.showNotification({
                type: 'success',
                title: 'Фильтры применены',
                message: `Найдено ${this.filteredVideos.length} видео`
            });
        },
        
        resetAllFilters() {
            this.videoFilters = {
                search: '',
                type: '',
                category: '',
                sort: 'date',
                viewsMin: null,
                viewsMax: null,
                engagementMin: null,
                engagementMax: null,
                dateFrom: '',
                dateTo: '',
                hasSubtitles: false,
                hasChapters: false,
                hasEmoji: false,
                hasBranding: false,
                hasPinnedComment: false,
                hasIntro: false,
                hasOutro: false,
                hasAnalysis: false,
                channelAvgViewsMin: null,
                channelAvgViewsMax: null,
                channelFrequencyMin: null,
                channelFrequencyMax: null,
                quality: ''
            };
            
            this.showNotification({
                type: 'info',
                title: 'Фильтры сброшены',
                message: 'Все фильтры удалены'
            });
        },
        
        resetFilters() {
            // Старый метод для совместимости
            this.resetAllFilters();
        },
        
        // Table scroll sync
        syncScroll(source, event) {
            const scrollLeft = event.target.scrollLeft;
            
            if (source === 'top' && this.$refs.tableContainer) {
                this.$refs.tableContainer.scrollLeft = scrollLeft;
            } else if (source === 'bottom' && this.$refs.topScroll) {
                this.$refs.topScroll.scrollLeft = scrollLeft;
            }
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
                const response = await axios.post('/api/tasks/pause-all');
                const pausedCount = response.data.paused_count;
                
                // Обновляем локальное состояние задач
                this.tasks.forEach(task => {
                    if (task.status === 'running') {
                        task.status = 'paused';
                    }
                });
                
                this.showNotification({
                    type: 'success',
                    title: 'Задачи приостановлены',
                    message: `Приостановлено задач: ${pausedCount}`
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
                const response = await axios.post('/api/tasks/resume-all');
                const resumedCount = response.data.resumed_count;
                
                // Обновляем локальное состояние задач
                this.tasks.forEach(task => {
                    if (task.status === 'paused') {
                        task.status = 'running';
                    }
                });
                
                this.showNotification({
                    type: 'success',
                    title: 'Задачи возобновлены',
                    message: `Возобновлено задач: ${resumedCount}`
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
                this.tasks = this.tasks.filter(t => !['completed', 'failed', 'cancelled'].includes(t.status));
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
                this.tasks[index] = updatedTask;
            }
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
        
        // UI Helpers
        updateBadges() {
            this.tabs[1].badge = this.videos.length;
            this.tabs[2].badge = this.channels.length;
            this.tabs[3].badge = this.activeTasks.length;
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
        
        formatDuration(duration) {
            if (!duration) return '';
            // Парсинг ISO 8601 duration (PT15M43S)
            const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
            if (!match) return duration;
            
            const hours = parseInt(match[1] || 0);
            const minutes = parseInt(match[2] || 0);
            const seconds = parseInt(match[3] || 0);
            
            if (hours > 0) {
                return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        },
        
        getEngagementClass(rate) {
            if (rate >= 10) return 'engagement-excellent';
            if (rate >= 5) return 'engagement-good';
            if (rate >= 2) return 'engagement-average';
            return 'engagement-poor';
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
                'failed': 'Ошибка',
                'cancelled': 'Отменено'
            };
            return statuses[status] || status;
        },
        
        getTaskStatusClass(status) {
            const classes = {
                'pending': 'bg-gray-100 text-gray-800',
                'running': 'bg-blue-100 text-blue-800',
                'paused': 'bg-yellow-100 text-yellow-800',
                'completed': 'bg-green-100 text-green-800',
                'failed': 'bg-red-100 text-red-800',
                'cancelled': 'bg-gray-100 text-gray-800'
            };
            return classes[status] || 'bg-gray-100 text-gray-800';
        }
    }
}).mount('#app');
