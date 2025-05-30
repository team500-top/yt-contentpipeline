// Help Tab Component
Vue.component('help-tab', {
    template: `
        <div key="help" class="max-w-4xl">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Справка</h2>
            
            <!-- Quick Links -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Быстрые ссылки</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <a href="/help.html" target="_blank" class="flex items-center p-4 border rounded-lg hover:bg-gray-50">
                        <svg class="w-8 h-8 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                        </svg>
                        <div>
                            <h4 class="font-medium text-gray-900">Полная документация</h4>
                            <p class="text-sm text-gray-500">Детальное руководство по всем функциям</p>
                        </div>
                    </a>
                    
                    <a href="/docs" target="_blank" class="flex items-center p-4 border rounded-lg hover:bg-gray-50">
                        <svg class="w-8 h-8 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
                        </svg>
                        <div>
                            <h4 class="font-medium text-gray-900">API документация</h4>
                            <p class="text-sm text-gray-500">Swagger/OpenAPI интерфейс</p>
                        </div>
                    </a>
                </div>
            </div>
            
            <!-- FAQ -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Часто задаваемые вопросы</h3>
                <div class="space-y-4">
                    <details class="border-b pb-4">
                        <summary class="cursor-pointer font-medium text-gray-900 hover:text-red-600">
                            Как начать парсинг?
                        </summary>
                        <div class="mt-2 text-gray-600">
                            <ol class="list-decimal list-inside space-y-1">
                                <li>Перейдите на вкладку "Парсинг"</li>
                                <li>Выберите тип парсинга (по ключевым словам или каналу)</li>
                                <li>Введите поисковый запрос или URL канала</li>
                                <li>Настройте фильтры (тип видео, количество результатов)</li>
                                <li>Нажмите "Начать парсинг"</li>
                            </ol>
                        </div>
                    </details>
                    
                    <details class="border-b pb-4">
                        <summary class="cursor-pointer font-medium text-gray-900 hover:text-red-600">
                            Что такое глубокий анализ?
                        </summary>
                        <div class="mt-2 text-gray-600">
                            Глубокий анализ использует AI алгоритмы для:
                            <ul class="list-disc list-inside mt-2 space-y-1">
                                <li>Извлечения ключевых слов (TF-IDF)</li>
                                <li>Анализа факторов успеха видео</li>
                                <li>Генерации персонализированных рекомендаций</li>
                                <li>Создания контент-стратегии</li>
                                <li>Оценки вирусного потенциала</li>
                            </ul>
                        </div>
                    </details>
                    
                    <details class="border-b pb-4">
                        <summary class="cursor-pointer font-medium text-gray-900 hover:text-red-600">
                            Как экспортировать данные?
                        </summary>
                        <div class="mt-2 text-gray-600">
                            <ol class="list-decimal list-inside space-y-1">
                                <li>Перейдите на вкладку "Видео" или "Каналы"</li>
                                <li>Примените нужные фильтры</li>
                                <li>Нажмите кнопку "Экспорт"</li>
                                <li>Выберите формат: Excel, CSV или JSON</li>
                                <li>Файл автоматически загрузится</li>
                            </ol>
                        </div>
                    </details>
                    
                    <details class="border-b pb-4">
                        <summary class="cursor-pointer font-medium text-gray-900 hover:text-red-600">
                            Какие лимиты у YouTube API?
                        </summary>
                        <div class="mt-2 text-gray-600">
                            YouTube API имеет дневной лимит в 10,000 единиц. Расход:
                            <ul class="list-disc list-inside mt-2 space-y-1">
                                <li>Поиск видео: ~100 единиц за запрос</li>
                                <li>Детали видео: ~3 единицы за видео</li>
                                <li>Информация о канале: ~3 единицы</li>
                                <li>Примерно 100 поисков или 3000 видео в день</li>
                            </ul>
                        </div>
                    </details>
                </div>
            </div>
            
            <!-- Shortcuts -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Горячие клавиши</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h4 class="font-medium text-gray-700 mb-2">Навигация</h4>
                        <table class="text-sm">
                            <tr>
                                <td class="pr-4 py-1"><kbd class="px-2 py-1 bg-gray-100 rounded">Alt + 1</kbd></td>
                                <td>Парсинг</td>
                            </tr>
                            <tr>
                                <td class="pr-4 py-1"><kbd class="px-2 py-1 bg-gray-100 rounded">Alt + 2</kbd></td>
                                <td>Видео</td>
                            </tr>
                            <tr>
                                <td class="pr-4 py-1"><kbd class="px-2 py-1 bg-gray-100 rounded">Alt + 3</kbd></td>
                                <td>Задачи</td>
                            </tr>
                            <tr>
                                <td class="pr-4 py-1"><kbd class="px-2 py-1 bg-gray-100 rounded">F5</kbd></td>
                                <td>Обновить</td>
                            </tr>
                        </table>
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-700 mb-2">Действия</h4>
                        <table class="text-sm">
                            <tr>
                                <td class="pr-4 py-1"><kbd class="px-2 py-1 bg-gray-100 rounded">Enter</kbd></td>
                                <td>Начать парсинг</td>
                            </tr>
                            <tr>
                                <td class="pr-4 py-1"><kbd class="px-2 py-1 bg-gray-100 rounded">Esc</kbd></td>
                                <td>Закрыть модальное окно</td>
                            </tr>
                            <tr>
                                <td class="pr-4 py-1"><kbd class="px-2 py-1 bg-gray-100 rounded">Ctrl + E</kbd></td>
                                <td>Экспорт данных</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Support -->
            <div class="mt-6 bg-gray-50 rounded-lg p-6">
                <h4 class="font-medium text-gray-900 mb-2">Нужна помощь?</h4>
                <p class="text-gray-600 mb-4">
                    Если у вас остались вопросы, обратитесь к полной документации или создайте issue на GitHub.
                </p>
                <div class="flex space-x-4">
                    <a href="https://github.com/team500-top/yt-contentpipeline" target="_blank" class="text-red-600 hover:text-red-700">
                        GitHub Repository
                    </a>
                    <span class="text-gray-400">•</span>
                    <a href="https://github.com/team500-top/yt-contentpipeline/issues" target="_blank" class="text-red-600 hover:text-red-700">
                        Сообщить о проблеме
                    </a>
                </div>
            </div>
        </div>
    `
});