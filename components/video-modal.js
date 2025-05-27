// Video Modal Component
Vue.component('video-modal', {
    props: ['video'],
    emits: ['close'],
    template: `
        <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-lg bg-white">
                <!-- Header -->
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-lg font-medium text-gray-900">Детали видео</h3>
                    <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <!-- Content -->
                <div class="space-y-6">
                    <!-- Video Info -->
                    <div class="flex space-x-4">
                        <img :src="video.thumbnail_url" :alt="video.title" class="w-48 h-28 object-cover rounded">
                        <div class="flex-1">
                            <h4 class="font-medium text-gray-900 mb-2">{{ video.title }}</h4>
                            <div class="text-sm text-gray-600 space-y-1">
                                <p>Канал: {{ video.channel_info?.title || video.channel_name }}</p>
                                <p>Опубликовано: {{ window.formatDate(video.publish_date) }}</p>
                                <p>Длительность: {{ window.formatDuration(video.duration) }}</p>
                                <div class="flex items-center space-x-4 mt-2">
                                    <span v-if="video.is_short" class="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">Shorts</span>
                                    <span v-if="video.has_cc" class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">CC</span>
                                    <span v-if="video.has_chapters" class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">Главы</span>
                                    <span v-if="video.video_quality" class="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">{{ video.video_quality.toUpperCase() }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Metrics -->
                    <div class="grid grid-cols-4 gap-4">
                        <div class="text-center p-4 bg-gray-50 rounded">
                            <p class="text-2xl font-semibold text-gray-900">{{ window.formatNumber(video.views) }}</p>
                            <p class="text-sm text-gray-500">Просмотры</p>
                        </div>
                        <div class="text-center p-4 bg-gray-50 rounded">
                            <p class="text-2xl font-semibold text-gray-900">{{ window.formatNumber(video.likes) }}</p>
                            <p class="text-sm text-gray-500">Лайки</p>
                        </div>
                        <div class="text-center p-4 bg-gray-50 rounded">
                            <p class="text-2xl font-semibold text-gray-900">{{ window.formatNumber(video.comments) }}</p>
                            <p class="text-sm text-gray-500">Комментарии</p>
                        </div>
                        <div class="text-center p-4 bg-gray-50 rounded">
                            <p class="text-2xl font-semibold" :class="window.getEngagementClass(video.engagement_rate)">
                                {{ video.engagement_rate }}%
                            </p>
                            <p class="text-sm text-gray-500">Вовлеченность</p>
                        </div>
                    </div>
                    
                    <!-- Keywords -->
                    <div v-if="video.keywords && video.keywords.length > 0">
                        <h5 class="font-medium text-gray-900 mb-2">Ключевые слова</h5>
                        <div class="flex flex-wrap gap-2">
                            <span v-for="keyword in video.top_5_keywords || video.keywords.slice(0, 10)" :key="keyword" 
                                class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                                {{ keyword }}
                            </span>
                        </div>
                    </div>
                    
                    <!-- AI Analysis -->
                    <div v-if="video.improvement_recommendations" class="bg-blue-50 rounded-lg p-4">
                        <h5 class="font-medium text-gray-900 mb-2">🤖 AI Рекомендации</h5>
                        <div class="text-sm text-gray-700 whitespace-pre-line">{{ video.improvement_recommendations }}</div>
                    </div>
                    
                    <div v-if="video.success_analysis" class="bg-green-50 rounded-lg p-4">
                        <h5 class="font-medium text-gray-900 mb-2">📊 Анализ успеха</h5>
                        <div class="text-sm text-gray-700 whitespace-pre-line">{{ video.success_analysis }}</div>
                    </div>
                    
                    <div v-if="video.content_strategy" class="bg-purple-50 rounded-lg p-4">
                        <h5 class="font-medium text-gray-900 mb-2">🎯 Контент-стратегия</h5>
                        <div class="text-sm text-gray-700 whitespace-pre-line">{{ video.content_strategy }}</div>
                    </div>
                    
                    <!-- Description -->
                    <div v-if="video.description">
                        <h5 class="font-medium text-gray-900 mb-2">Описание</h5>
                        <p class="text-sm text-gray-600 whitespace-pre-wrap max-h-40 overflow-y-auto">{{ video.description }}</p>
                    </div>
                    
                    <!-- Actions -->
                    <div class="flex justify-between items-center pt-4 border-t">
                        <a :href="video.video_url" target="_blank" class="text-red-600 hover:text-red-700 flex items-center">
                            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                            </svg>
                            Смотреть на YouTube
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