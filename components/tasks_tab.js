// Tasks Tab Component
Vue.component('tasks-tab', {
    props: ['tasks', 'activeTasks', 'pausedTasks', 'completedTasks'],
    emits: ['pauseTask', 'resumeTask', 'cancelTask', 'pauseAllTasks', 'resumeAllTasks', 'clearCompletedTasks'],
    template: `
        <div key="tasks">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Задачи</h2>
            
            <!-- Tasks Controls -->
            <div class="bg-white rounded-lg shadow p-4 mb-6">
                <div class="flex justify-between items-center">
                    <div class="flex space-x-4">
                        <button 
                            @click="$emit('pauseAllTasks')" 
                            :disabled="activeTasks.length === 0" 
                            class="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Приостановить все
                        </button>
                        <button 
                            @click="$emit('resumeAllTasks')" 
                            :disabled="pausedTasks.length === 0" 
                            class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Возобновить все
                        </button>
                    </div>
                    <button 
                        @click="$emit('clearCompletedTasks')" 
                        :disabled="completedTasks.length === 0" 
                        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Очистить завершенные
                    </button>
                </div>
            </div>

            <!-- Active Tasks -->
            <div class="space-y-4">
                <div v-for="task in tasks" :key="task.id" class="bg-white rounded-lg shadow p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="font-medium text-gray-900">{{ window.getTaskTypeName(task.task_type) }}</h3>
                            <p class="text-sm text-gray-500">{{ task.parameters.query || task.parameters.channel || 'Нет данных' }}</p>
                        </div>
                        <span :class="['px-3 py-1 text-xs font-medium rounded-full', window.getTaskStatusClass(task.status)]">
                            {{ window.getTaskStatusName(task.status) }}
                        </span>
                    </div>
                    
                    <!-- Progress Bar -->
                    <div class="mb-4">
                        <div class="flex justify-between text-sm text-gray-600 mb-1">
                            <span>Прогресс: {{ task.processed_items || 0 }} / {{ task.total_items || 0 }}</span>
                            <span>{{ (task.progress || 0).toFixed(0) }}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                            <div :style="{width: (task.progress || 0) + '%'}" class="bg-red-600 h-2 rounded-full transition-all duration-300 relative">
                                <div v-if="task.status === 'running'" class="absolute inset-0 bg-white opacity-25 animate-pulse"></div>
                            </div>
                        </div>
                        
                        <!-- Детали задачи -->
                        <div v-if="task.status === 'running' && task.parameters" class="mt-2 text-xs text-gray-500">
                            <p v-if="task.parameters.query">Запрос: {{ task.parameters.query }}</p>
                            <p v-if="task.parameters.type">Тип: {{ task.parameters.type === 'keyword' ? 'Поиск' : 'Канал' }}</p>
                            <p v-if="task.parameters.maxResults">Максимум: {{ task.parameters.maxResults }} видео</p>
                        </div>
                        
                        <!-- Сообщение об ошибке -->
                        <div v-if="task.error_message" class="mt-2 text-sm text-red-600">
                            Ошибка: {{ task.error_message }}
                        </div>
                    </div>
                    
                    <!-- Task Actions -->
                    <div class="flex justify-between items-center">
                        <p class="text-sm text-gray-500">
                            Создана: {{ window.formatDate(task.created_at) }}
                        </p>
                        <div class="flex space-x-2">
                            <button 
                                v-if="task.status === 'running'" 
                                @click="$emit('pauseTask', task.id)" 
                                class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
                            >
                                Пауза
                            </button>
                            <button 
                                v-else-if="task.status === 'paused'" 
                                @click="$emit('resumeTask', task.id)" 
                                class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                            >
                                Продолжить
                            </button>
                            <button 
                                v-if="['running', 'paused', 'pending'].includes(task.status)" 
                                @click="$emit('cancelTask', task.id)" 
                                class="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                            >
                                Отменить
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="tasks.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">Нет активных задач</h3>
                <p class="mt-1 text-sm text-gray-500">Начните парсинг, чтобы создать новые задачи.</p>
            </div>
        </div>
    `
});
