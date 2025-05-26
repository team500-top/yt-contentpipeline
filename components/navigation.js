// Navigation Component
Vue.component('app-navigation', {
    props: ['tabs', 'activeTab'],
    emits: ['update:activeTab'],
    template: `
        <nav class="bg-white border-b border-gray-200 flex-shrink-0">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex space-x-8">
                    <button
                        v-for="tab in tabs"
                        :key="tab.id"
                        @click="$emit('update:activeTab', tab.id)"
                        :class="[
                            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                            activeTab === tab.id
                                ? 'border-red-500 text-red-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        ]"
                    >
                        {{ tab.name }}
                        <span v-if="tab.badge" class="ml-2 px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-600">
                            {{ tab.badge }}
                        </span>
                    </button>
                </div>
            </div>
        </nav>
    `
});
