// Videos Tab Component
Vue.component('videos-tab', {
    props: ['videos', 'videoFilters', 'viewMode', 'showFilters', 'showExportMenu'],
    emits: ['update:viewMode', 'update:showFilters', 'update:showExportMenu', 'update:videoFilters', 'exportVideos', 'viewVideo', 'toggleFilters', 'applyFilters', 'resetAllFilters'],
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
        }
    },
    template: `
        <div key="videos">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-900">Видео</h2>
                <div class="flex space-x-2">
                    <!-- View Mode Toggle -->
                    <div class="flex bg-gray-100 rounded-md p-1">
                        <button 
                            @click="$emit('update:viewMode', 'table')" 
                            :class="['px-3 py-1 rounded', viewMode === 'table' ? 'bg-white shadow-sm' : 'text-gray-600']"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                            </svg>
                        </button>
                        <button 
                            @click="$emit('update:viewMode', 'cards')" 
                            :class="['px-3 py-1 rounded', viewMode === 'cards' ? 'bg-white shadow-sm' : 'text-gray-600']"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Filters Button -->
                    <button 
                        @click="$emit('toggleFilters')" 
                        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 flex items-center relative"
                    >
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
                        </svg>
                        Фильтры
                        <span v-if="activeFiltersCount > 0" class="ml-2 px-2 py-0.5 text-xs bg-red-500 text-white rounded-full">
                            {{ activeFiltersCount }}
                        </span>
                    </button>
                    
                    <!-- Export Menu -->
                    <div class="relative">
                        <button 
                            @click="$emit('update:showExportMenu', !showExportMenu)" 
                            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center"
                        >
                            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            Экспорт
                        </button>
                        
                        <div v-if="showExportMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
                            <a @click="$emit('exportVideos', 'excel')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
                                📊 Excel (.xlsx)
                            </a>
                            <a @click="$emit('exportVideos', 'csv')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
                                📄 CSV (.csv)
                            </a>
                            <a @click="$emit('exportVideos', 'json')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
                                🔧 JSON (.json)
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Filters Panel -->
            <div v-if="showFilters" class="bg-white rounded-lg shadow p-6 mb-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900">Фильтры</h3>
                    <button @click="$emit('resetAllFilters')" class="text-sm text-red-600 hover:text-red-700">
                        Сбросить все
                    </button>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    <!-- Search -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Поиск</label>
                        <input 
                            :value="videoFilters.search"
                            @input="$emit('update:videoFilters', {...videoFilters, search: $event.target.value})"
                            type="text" 
                            placeholder="Название, канал..."
                            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                        >
                    </div>
                    
                    <!-- Video Type -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Тип видео</label>
                        <select 
                            :value="videoFilters.type"
                            @change="$emit('update:videoFilters', {...videoFilters, type: $event.target.value})"
                            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                        >
                            <option value="">Все</option>
                            <option value="shorts">Shorts</option>
                            <option value="long">Длинные</option>
                        </select>
                    </div>
                    
                    <!-- Views Range -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Просмотры</label>
                        <div class="flex space-x-2">
                            <input 
                                :value="videoFilters.viewsMin"
                                @input="$emit('update:videoFilters', {...videoFilters, viewsMin: $event.target.value ? Number($event.target.value) : null})"
                                type="number" 
                                placeholder="От"
                                class="w-1/2 px-2 py-2 border border-gray-300 rounded-md text-sm"
                            >
                            <input 
                                :value="videoFilters.viewsMax"
                                @input="$emit('update:videoFilters', {...videoFilters, viewsMax: $event.target.value ? Number($event.target.value) : null})"
                                type="number" 
                                placeholder="До"
                                class="w-1/2 px-2 py-2 border border-gray-300 rounded-md text-sm"
                            >
                        </div>
                    </div>
                    
                    <!-- Engagement Range -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Вовлеченность %</label>
                        <div class="flex space-x-2">
                            <input 
                                :value="videoFilters.engagementMin"
                                @input="$emit('update:videoFilters', {...videoFilters, engagementMin: $event.target.value ? Number($event.target.value) : null})"
                                type="number" 
                                step="0.1"
                                placeholder="От"
                                class="w-1/2 px-2 py-2 border border-gray-300 rounded-md text-sm"
                            >
                            <input 
                                :value="videoFilters.engagementMax"
                                @input="$emit('update:videoFilters', {...videoFilters, engagementMax: $event.target.value ? Number($event.target.value) : null})"
                                type="number" 
                                step="0.1"
                                placeholder="До"
                                class="w-1/2 px-2 py-2 border border-gray-300 rounded-md text-sm"
                            >
                        </div>
                    </div>
                    
                    <!-- Date Range -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Дата публикации</label>
                        <div class="flex space-x-2">
                            <input 
                                :value="videoFilters.dateFrom"
                                @input="$emit('update:videoFilters', {...videoFilters, dateFrom: $event.target.value})"
                                type="date" 
                                class="w-1/2 px-2 py-2 border border-gray-300 rounded-md text-sm"
                            >
                            <input 
                                :value="videoFilters.dateTo"
                                @input="$emit('update:videoFilters', {...videoFilters, dateTo: $event.target.value})"
                                type="date" 
                                class="w-1/2 px-2 py-2 border border-gray-300 rounded-md text-sm"
                            >
                        </div>
                    </div>
                    
                    <!-- Quality -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Качество</label>
                        <select 
                            :value="videoFilters.quality"
                            @change="$emit('update:videoFilters', {...videoFilters, quality: $event.target.value})"
                            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                        >
                            <option value="">Любое</option>
                            <option value="hd">HD</option>
                            <option value="4k">4K</option>
                            <option value="sd">SD</option>
                        </select>
                    </div>
                    
                    <!-- Sort -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Сортировка</label>
                        <select 
                            :value="videoFilters.sort"
                            @change="$emit('update:videoFilters', {...videoFilters, sort: $event.target.value})"
                            class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                        >
                            <option value="date">По дате</option>
                            <option value="views">По просмотрам</option>
                            <option value="likes">По лайкам</option>
                            <option value="comments">По комментариям</option>
                            <option value="engagement">По вовлеченности</option>
                        </select>
                    </div>
                </div>
                
                <!-- Boolean Filters -->
                <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
                    <label class="flex items-center">
                        <input 
                            type="checkbox" 
                            :checked="videoFilters.hasSubtitles"
                            @change="$emit('update:videoFilters', {...videoFilters, hasSubtitles: $event.target.checked})"
                            class="mr-2 text-red-600"
                        >
                        <span class="text-sm">С субтитрами</span>
                    </label>
                    
                    <label class="flex items-center">
                        <input 
                            type="checkbox" 
                            :checked="videoFilters.hasChapters"
                            @change="$emit('update:videoFilters', {...videoFilters, hasChapters: $event.target.checked})"
                            class="mr-2 text-red-600"
                        >
                        <span class="text-sm">С главами</span>
                    </label>
                    
                    <label class="flex items-center">
                        <input 
                            type="checkbox" 
                            :checked="videoFilters.hasEmoji"
                            @change="$emit('update:videoFilters', {...videoFilters, hasEmoji: $event.target.checked})"
                            class="mr-2 text-red-600"
                        >
                        <span class="text-sm">Эмодзи в заголовке</span>
                    </label>
                    
                    <label class="flex items-center">
                        <input 
                            type="checkbox" 
                            :checked="videoFilters.hasAnalysis"
                            @change="$emit('update:videoFilters', {...videoFilters, hasAnalysis: $event.target.checked})"
                            class="mr-2 text-red-600"
                        >
                        <span class="text-sm">С анализом</span>
                    </label>
                </div>
                
                <div class="mt-4 flex justify-end">
                    <button 
                        @click="$emit('applyFilters')" 
                        class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                        Применить ({{ filteredVideos.length }} видео)
                    </button>
                </div>
            </div>
            
            <!-- Table View -->
            <div v-if="viewMode === 'table' && filteredVideos.length > 0" class="overflow-hidden">
                <!-- Scroll sync container -->
                <div ref="topScroll" @scroll="syncScroll('top', $event)" class="overflow-x-auto mb-2">
                    <div :style="{width: tableWidth + 'px', height: '1px'}"></div>
                </div>
                
                <div ref="tableContainer" @scroll="syncScroll('bottom', $event)" class="overflow-x-auto">
                    <table class="min-w-full bg-white rounded-lg shadow" :style="{width: tableWidth + 'px'}">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Превью</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Название</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Канал</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Тип</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Просмотры</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Лайки</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Комменты</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Вовлеч. %</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Дата</th>
                                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Действия</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            <tr v-for="video in filteredVideos" :key="video.id" class="hover:bg-gray-50">
                                <td class="px-4 py-2 whitespace-nowrap">
                                    <img :src="video.thumbnail_url" :alt="video.title" class="w-20 h-12 object-cover rounded">
                                </td>
                                <td class="px-4 py-2">
                                    <div class="max-w-sm">
                                        <p class="text-sm font-medium text-gray-900 line-clamp-2">{{ video.title }}</p>
                                        <p v-if="video.top_5_keywords && video.top_5_keywords.length > 0" class="text-xs text-gray-500 mt-1">
                                            {{ video.top_5_keywords.slice(0, 3).join(', ') }}
                                        </p>
                                    </div>
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap">
                                    <p class="text-sm text-gray-900">{{ video.channel_name }}</p>
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap">
                                    <span v-if="video.is_short" class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">
                                        Shorts
                                    </span>
                                    <span v-else class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                                        Видео
                                    </span>
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                                    {{ window.formatNumber(video.views) }}
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                                    {{ window.formatNumber(video.likes) }}
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                                    {{ window.formatNumber(video.comments) }}
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap">
                                    <span :class="['px-2 py-1 text-xs font-medium rounded-full', window.getEngagementClass(video.engagement_rate)]">
                                        {{ video.engagement_rate }}%
                                    </span>
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                    {{ window.formatDate(video.publish_date) }}
                                </td>
                                <td class="px-4 py-2 whitespace-nowrap text-sm">
                                    <button @click="$emit('viewVideo', video)" class="text-red-600 hover:text-red-900">
                                        Детали
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Cards View -->
            <div v-else-if="viewMode === 'cards' && filteredVideos.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <div v-for="video in filteredVideos" :key="video.id" class="bg-white rounded-lg shadow hover-scale video-card cursor-pointer" @click="$emit('viewVideo', video)">
                    <div class="aspect-w-16 aspect-h-9">
                        <img :src="video.thumbnail_url" :alt="video.title" class="w-full h-48 object-cover rounded-t-lg">
                        <div v-if="video.is_short" class="absolute top-2 right-2 px-2 py-1 bg-purple-600 text-white text-xs rounded">
                            Shorts
                        </div>
                    </div>
                    <div class="p-4">
                        <h3 class="font-medium text-gray-900 line-clamp-2 mb-2">{{ video.title }}</h3>
                        <p class="text-sm text-gray-500 mb-3">{{ video.channel_name }}</p>
                        <div class="flex justify-between items-center text-sm text-gray-600">
                            <span>{{ window.formatNumber(video.views) }} просмотров</span>
                            <span :class="window.getEngagementClass(video.engagement_rate)">
                                {{ video.engagement_rate }}%
                            </span>
                        </div>
                        <p class="text-xs text-gray-500 mt-2">{{ window.formatDate(video.publish_date) }}</p>
                    </div>
                </div>
            </div>
            
            <!-- Empty State -->
            <div v-if="filteredVideos.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 16h4m10 0h4"></path>
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">Нет видео</h3>
                <p class="mt-1 text-sm text-gray-500">
                    {{ videos.length === 0 ? 'Начните парсинг для добавления видео' : 'Попробуйте изменить фильтры' }}
                </p>
            </div>
        </div>
    `,
    methods: {
        syncScroll(source, event) {
            const scrollLeft = event.target.scrollLeft;
            
            if (source === 'top' && this.$refs.tableContainer) {
                this.$refs.tableContainer.scrollLeft = scrollLeft;
            } else if (source === 'bottom' && this.$refs.topScroll) {
                this.$refs.topScroll.scrollLeft = scrollLeft;
            }
        }
    }
});