// Channels Tab Component
Vue.component('channels-tab', {
    props: ['channels', 'channelFilters', 'channelViewMode', 'showChannelExportMenu'],
    emits: ['update:channelViewMode', 'update:showChannelExportMenu', 'update:channelFilters', 'exportChannels', 'viewChannel'],
    computed: {
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
        }
    },
    template: `
        <div key="channels">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-900">Каналы</h2>
                <div class="flex space-x-2">
                    <!-- View Mode Toggle -->
                    <div class="flex bg-gray-100 rounded-md p-1">
                        <button 
                            @click="$emit('update:channelViewMode', 'table')" 
                            :class="['px-3 py-1 rounded', channelViewMode === 'table' ? 'bg-white shadow-sm' : 'text-gray-600']"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                            </svg>
                        </button>
                        <button 
                            @click="$emit('update:channelViewMode', 'cards')" 
                            :class="['px-3 py-1 rounded', channelViewMode === 'cards' ? 'bg-white shadow-sm' : 'text-gray-600']"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Export Menu -->
                    <div class="relative">
                        <button 
                            @click="$emit('update:showChannelExportMenu', !showChannelExportMenu)" 
                            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 flex items-center"
                        >
                            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            Экспорт
                        </button>
                        
                        <div v-if="showChannelExportMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
                            <a @click="$emit('exportChannels', 'excel')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
                                📊 Excel (.xlsx)
                            </a>
                            <a @click="$emit('exportChannels', 'csv')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
                                📄 CSV (.csv)
                            </a>
                            <a @click="$emit('exportChannels', 'json')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
                                🔧 JSON (.json)
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Filters -->
            <div class="bg-white rounded-lg shadow p-4 mb-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Поиск</label>
                        <input 
                            :value="channelFilters.search"
                            @input="$emit('update:channelFilters', {...channelFilters, search: $event.target.value})"
                            type="text" 
                            placeholder="Название канала..."
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Сортировка</label>
                        <select 
                            :value="channelFilters.sort"
                            @change="$emit('update:channelFilters', {...channelFilters, sort: $event.target.value})"
                            class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="subscribers">По подписчикам</option>
                            <option value="videos">По количеству видео</option>
                            <option value="views">По просмотрам</option>
                            <option value="date">По дате создания</option>
                        </select>
                    </div>
                    <div class="flex items-end">
                        <div class="text-sm text-gray-600">
                            Найдено: {{ filteredChannels.length }} каналов
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Table View -->
            <div v-if="channelViewMode === 'table' && filteredChannels.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
                <table class="min-w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Канал</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Подписчики</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Видео</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Просмотры</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ср. просмотры</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Страна</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Создан</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        <tr v-for="channel in filteredChannels" :key="channel.id" class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <img :src="channel.thumbnail_url" :alt="channel.title" class="w-10 h-10 rounded-full mr-3">
                                    <div>
                                        <p class="text-sm font-medium text-gray-900">{{ channel.title }}</p>
                                        <p class="text-xs text-gray-500">{{ channel.channel_id }}</p>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ window.formatNumber(channel.subscriber_count) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ channel.video_count }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ window.formatNumber(channel.view_count) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ window.formatNumber(channel.avg_views) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{ channel.country || '-' }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{ window.formatDate(channel.created_date) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm">
                                <button @click="$emit('viewChannel', channel)" class="text-red-600 hover:text-red-900">
                                    Детали
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Cards View -->
            <div v-else-if="channelViewMode === 'cards' && filteredChannels.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <div v-for="channel in filteredChannels" :key="channel.id" class="bg-white rounded-lg shadow hover-scale cursor-pointer" @click="$emit('viewChannel', channel)">
                    <div class="p-6">
                        <div class="flex items-center mb-4">
                            <img :src="channel.thumbnail_url" :alt="channel.title" class="w-16 h-16 rounded-full mr-4">
                            <div class="flex-1">
                                <h3 class="font-medium text-gray-900">{{ channel.title }}</h3>
                                <p class="text-sm text-gray-500">{{ window.formatNumber(channel.subscriber_count) }} подписчиков</p>
                            </div>
                        </div>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <span class="text-gray-500">Видео:</span>
                                <span class="font-medium">{{ channel.video_count }}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-500">Просмотры:</span>
                                <span class="font-medium">{{ window.formatNumber(channel.view_count) }}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-500">Ср. просмотры:</span>
                                <span class="font-medium">{{ window.formatNumber(channel.avg_views) }}</span>
                            </div>
                        </div>
                        <div class="mt-4 pt-4 border-t text-xs text-gray-500">
                            Создан: {{ window.formatDate(channel.created_date) }}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Empty State -->
            <div v-if="filteredChannels.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">Нет каналов</h3>
                <p class="mt-1 text-sm text-gray-500">
                    {{ channels.length === 0 ? 'Каналы появятся после парсинга' : 'Попробуйте изменить параметры поиска' }}
                </p>
            </div>
        </div>
    `
});