// Settings Tab Component
Vue.component('settings-tab', {
    props: ['settings'],
    emits: ['update:settings', 'saveSettings', 'exportDatabase', 'importDatabase'],
    template: `
        <div key="settings">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Настройки</h2>
            
            <!-- API Settings -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">API Настройки</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">YouTube API Key</label>
                        <input 
                            :value="settings.youtubeApiKey"
                            @input="$emit('update:settings', {...settings, youtubeApiKey: $event.target.value})"
                            type="password" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                            placeholder="AIzaSy..."
                        >
                        <p class="mt-1 text-sm text-gray-500">
                            Получите ключ в <a href="https://console.cloud.google.com" target="_blank" class="text-red-600 hover:text-red-700">Google Cloud Console</a>
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Server Settings -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Настройки сервера</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Host</label>
                        <input 
                            :value="settings.host"
                            @input="$emit('update:settings', {...settings, host: $event.target.value})"
                            type="text" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Port</label>
                        <input 
                            :value="settings.port"
                            @input="$emit('update:settings', {...settings, port: Number($event.target.value)})"
                            type="number" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">База данных</label>
                        <input 
                            :value="settings.databasePath"
                            @input="$emit('update:settings', {...settings, databasePath: $event.target.value})"
                            type="text" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                            readonly
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Redis URL</label>
                        <input 
                            :value="settings.redisUrl"
                            @input="$emit('update:settings', {...settings, redisUrl: $event.target.value})"
                            type="text" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                    </div>
                </div>
            </div>
            
            <!-- Parsing Settings -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Настройки парсинга</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Макс. результатов за поиск</label>
                        <input 
                            :value="settings.maxResultsPerSearch"
                            @input="$emit('update:settings', {...settings, maxResultsPerSearch: Number($event.target.value)})"
                            type="number" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Задержка между запросами (сек)</label>
                        <input 
                            :value="settings.apiRequestDelay"
                            @input="$emit('update:settings', {...settings, apiRequestDelay: Number($event.target.value)})"
                            type="number" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                    </div>
                </div>
                
                <div class="mt-4 space-y-2">
                    <label class="flex items-center">
                        <input 
                            type="checkbox" 
                            :checked="settings.enableDeepAnalysis"
                            @change="$emit('update:settings', {...settings, enableDeepAnalysis: $event.target.checked})"
                            class="mr-2 text-red-600"
                        >
                        <span class="text-sm">Включить глубокий анализ (AI рекомендации)</span>
                    </label>
                    <label class="flex items-center">
                        <input 
                            type="checkbox" 
                            :checked="settings.enableWebsocket"
                            @change="$emit('update:settings', {...settings, enableWebsocket: $event.target.checked})"
                            class="mr-2 text-red-600"
                        >
                        <span class="text-sm">Включить WebSocket обновления</span>
                    </label>
                    <label class="flex items-center">
                        <input 
                            type="checkbox" 
                            :checked="settings.enableAutoRetry"
                            @change="$emit('update:settings', {...settings, enableAutoRetry: $event.target.checked})"
                            class="mr-2 text-red-600"
                        >
                        <span class="text-sm">Автоматический повтор при ошибках</span>
                    </label>
                </div>
            </div>
            
            <!-- Actions -->
            <div class="flex justify-between">
                <div class="space-x-4">
                    <button 
                        @click="$emit('exportDatabase')" 
                        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                    >
                        📥 Экспорт БД
                    </button>
                    <button 
                        @click="$emit('importDatabase')" 
                        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                    >
                        📤 Импорт БД
                    </button>
                </div>
                <button 
                    @click="$emit('saveSettings')" 
                    class="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                    Сохранить настройки
                </button>
            </div>
            
            <!-- Info -->
            <div class="mt-8 bg-blue-50 rounded-lg p-6">
                <h4 class="font-medium text-gray-900 mb-2">Системная информация</h4>
                <div class="space-y-1 text-sm text-gray-600">
                    <p>Версия: 1.0.0</p>
                    <p>Python: 3.11+</p>
                    <p>База данных: SQLite</p>
                    <p>Очередь задач: Celery + Redis</p>
                    <p>Документация API: <a href="/docs" target="_blank" class="text-red-600 hover:text-red-700">/docs</a></p>
                </div>
            </div>
        </div>
    `
});