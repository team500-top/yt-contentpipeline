// Channel Modal Component
Vue.component('channel-modal', {
    props: ['channel'],
    emits: ['close'],
    template: `
        <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-lg bg-white">
                <!-- Header -->
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-lg font-medium text-gray-900">Информация о канале</h3>
                    <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <!-- Content -->
                <div class="space-y-6">
                    <!-- Channel Info -->
                    <div class="flex items-start space-x-4">
                        <img :src="channel.thumbnail_url" :alt="channel.title" class="w-24 h-24 rounded-full">
                        <div class="flex-1">
                            <h4 class="text-xl font-semibold text-gray-900">{{ channel.title }}</h4>
                            <p class="text-sm text-gray-500 mb-2">{{ channel.channel_id }}</p>
                            <div class="flex items-center space-x-4 text-sm">
                                <span v-if="channel.country" class="flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                    </svg>
                                    {{ channel.country }}
                                </span>
                                <span class="flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                    </svg>
                                    Создан: {{ window.formatDate(channel.created_date) }}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Stats -->
                    <div class="grid grid-cols-3 gap-4">
                        <div class="text-center p-4 bg-gray-50 rounded">
                            <p class="text-2xl font-semibold text-gray-900">{{ window.formatNumber(channel.subscriber_count) }}</p>
                            <p class="text-sm text-gray-500">Подписчики</p>
                        </div>
                        <div class="text-center p-4 bg-gray-50 rounded">
                            <p class="text-2xl font-semibold text-gray-900">{{ channel.video_count }}</p>
                            <p class="text-sm text-gray-500">Видео</p>
                        </div>
                        <div class="text-center p-4 bg-gray-50 rounded">
                            <p class="text-2xl font-semibold text-gray-900">{{ window.formatNumber(channel.view_count) }}</p>
                            <p class="text-sm text-gray-500">Просмотры</p>
                        </div>
                    </div>
                    
                    <!-- Average Stats -->
                    <div>
                        <h5 class="font-medium text-gray-900 mb-3">Средние показатели</h5>
                        <div class="grid grid-cols-3 gap-4">
                            <div class="p-3 border rounded">
                                <p class="text-lg font-semibold text-gray-900">{{ window.formatNumber(channel.avg_views) }}</p>
                                <p class="text-sm text-gray-500">Просмотры/видео</p>
                            </div>
                            <div class="p-3 border rounded">
                                <p class="text-lg font-semibold text-gray-900">{{ window.formatNumber(channel.avg_likes) }}</p>
                                <p class="text-sm text-gray-500">Лайки/видео</p>
                            </div>
                            <div class="p-3 border rounded">
                                <p class="text-lg font-semibold text-gray-900">{{ window.formatNumber(channel.avg_comments) }}</p>
                                <p class="text-sm text-gray-500">Комментарии/видео</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Upload Frequency -->
                    <div v-if="channel.upload_frequency">
                        <h5 class="font-medium text-gray-900 mb-2">Частота публикаций</h5>
                        <p class="text-gray-600">
                            Новое видео каждые <span class="font-semibold">{{ Math.round(channel.upload_frequency) }}</span> дней
                        </p>
                    </div>
                    
                    <!-- Keywords -->
                    <div v-if="channel.keywords && channel.keywords.length > 0">
                        <h5 class="font-medium text-gray-900 mb-2">Ключевые слова канала</h5>
                        <div class="flex flex-wrap gap-2">
                            <span v-for="keyword in channel.keywords.slice(0, 10)" :key="keyword" 
                                class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                                {{ keyword }}
                            </span>
                        </div>
                    </div>
                    
                    <!-- Description -->
                    <div v-if="channel.description">
                        <h5 class="font-medium text-gray-900 mb-2">Описание канала</h5>
                        <p class="text-sm text-gray-600 whitespace-pre-wrap max-h-40 overflow-y-auto">{{ channel.description }}</p>
                    </div>
                    
                    <!-- Recent Videos -->
                    <div v-if="channel.recent_videos && channel.recent_videos.length > 0">
                        <h5 class="font-medium text-gray-900 mb-3">Последние видео</h5>
                        <div class="space-y-2 max-h-60 overflow-y-auto">
                            <div v-for="video in channel.recent_videos" :key="video.id" 
                                class="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded">
                                <img :src="video.thumbnail_url" :alt="video.title" class="w-20 h-12 object-cover rounded">
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-900 line-clamp-1">{{ video.title }}</p>
                                    <p class="text-xs text-gray-500">
                                        {{ window.formatNumber(video.views) }} просмотров • {{ window.formatDate(video.publish_date) }}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Actions -->
                    <div class="flex justify-between items-center pt-4 border-t">
                        <a :href="channel.channel_url" target="_blank" class="text-red-600 hover:text-red-700 flex items-center">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                            </svg>
                            Открыть на YouTube
                        </a>
                        <button @click="$emit('close')" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200">
                            Закрыть
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `
});