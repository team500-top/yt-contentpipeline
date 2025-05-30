// Parsing Tab Component
Vue.component('parsing-tab', {
    props: ['searchForm', 'isSearching', 'recentQueries'],
    emits: ['startParsing', 'repeatSearch'],
    template: `
        <div key="parsing">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Парсинг YouTube</h2>
            
            <!-- Search Form -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Left Column -->
                    <div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Тип парсинга</label>
                            <select v-model="searchForm.type" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500">
                                <option value="keyword">По ключевым словам</option>
                                <option value="channel">По каналу</option>
                                <option value="playlist" disabled>По плейлисту (скоро)</option>
                                <option value="trending" disabled>Тренды (скоро)</option>
                            </select>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                {{ searchForm.type === 'channel' ? 'URL канала' : 'Поисковый запрос' }}
                            </label>
                            <input 
                                v-model="searchForm.query" 
                                type="text" 
                                :placeholder="searchForm.type === 'channel' ? '@username или URL канала' : 'Введите поисковый запрос'"
                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500"
                                @keyup.enter="$emit('startParsing')"
                            >
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Максимум результатов</label>
                            <input 
                                v-model.number="searchForm.maxResults" 
                                type="number" 
                                min="1" 
                                max="500"
                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500"
                            >
                        </div>
                    </div>
                    
                    <!-- Right Column -->
                    <div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Тип видео</label>
                            <select v-model="searchForm.videoType" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500">
                                <option value="all">Все видео</option>
                                <option value="shorts">Только Shorts</option>
                                <option value="long">Только длинные</option>
                            </select>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Сортировка</label>
                            <select v-model="searchForm.sort" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500">
                                <option value="relevance">По релевантности</option>
                                <option value="date">По дате загрузки</option>
                                <option value="viewCount">По просмотрам</option>
                                <option value="rating">По рейтингу</option>
                            </select>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Регион</label>
                            <select v-model="searchForm.regionCode" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500">
                                <option value="RU">Россия</option>
                                <option value="US">США</option>
                                <option value="GB">Великобритания</option>
                                <option value="DE">Германия</option>
                                <option value="FR">Франция</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Advanced Filters Toggle -->
                <details class="mt-4">
                    <summary class="cursor-pointer text-sm text-gray-600 hover:text-gray-900">
                        Расширенные фильтры
                    </summary>
                    <div class="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Длительность</label>
                            <select v-model="searchForm.duration" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500">
                                <option value="">Любая</option>
                                <option value="short">Короткие (&lt;4 мин)</option>
                                <option value="medium">Средние (4-20 мин)</option>
                                <option value="long">Длинные (&gt;20 мин)</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Качество видео</label>
                            <select v-model="searchForm.videoDefinition" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500">
                                <option value="">Любое</option>
                                <option value="hd">HD</option>
                                <option value="sd">SD</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Субтитры</label>
                            <select v-model="searchForm.videoCaption" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500">
                                <option value="">Не важно</option>
                                <option value="closedCaption">С субтитрами</option>
                                <option value="none">Без субтитров</option>
                            </select>
                        </div>
                    </div>
                </details>
                
                <!-- Submit Button -->
                <div class="mt-6">
                    <button 
                        @click="$emit('startParsing')" 
                        :disabled="!searchForm.query || isSearching"
                        class="w-full bg-red-600 text-white px-4 py-3 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                        <svg v-if="isSearching" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {{ isSearching ? 'Запуск парсинга...' : 'Начать парсинг' }}
                    </button>
                </div>
            </div>
            
            <!-- Recent Searches -->
            <div v-if="recentQueries.length > 0" class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Недавние запросы</h3>
                <div class="space-y-2">
                    <div v-for="query in recentQueries" :key="query.id" class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-md">
                        <div class="flex-1">
                            <p class="font-medium text-gray-900">{{ query.query }}</p>
                            <p class="text-sm text-gray-500">
                                {{ query.type === 'keyword' ? 'Поиск' : 'Канал' }} • 
                                {{ query.results }} результатов • 
                                {{ window.formatDate(query.date) }}
                            </p>
                        </div>
                        <button 
                            @click="$emit('repeatSearch', query)" 
                            class="ml-4 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                        >
                            Повторить
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Features Info -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center mb-4">
                        <div class="p-3 bg-red-100 rounded-lg">
                            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            </svg>
                        </div>
                        <h3 class="ml-3 text-lg font-medium text-gray-900">Умный поиск</h3>
                    </div>
                    <p class="text-gray-600">Находите видео по ключевым словам с фильтрацией по типу, длительности и качеству</p>
                </div>
                
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center mb-4">
                        <div class="p-3 bg-blue-100 rounded-lg">
                            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                            </svg>
                        </div>
                        <h3 class="ml-3 text-lg font-medium text-gray-900">Анализ каналов</h3>
                    </div>
                    <p class="text-gray-600">Парсинг всех видео канала для анализа стратегии конкурентов</p>
                </div>
                
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center mb-4">
                        <div class="p-3 bg-green-100 rounded-lg">
                            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                        </div>
                        <h3 class="ml-3 text-lg font-medium text-gray-900">40+ параметров</h3>
                    </div>
                    <p class="text-gray-600">Детальный анализ каждого видео с рекомендациями по улучшению</p>
                </div>
            </div>
        </div>
    `
});