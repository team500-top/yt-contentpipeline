// Utility functions
window.formatNumber = function(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
};

window.formatDate = function(date) {
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
};

window.formatDuration = function(duration) {
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
};

window.getEngagementClass = function(rate) {
    if (rate >= 10) return 'engagement-excellent';
    if (rate >= 5) return 'engagement-good';
    if (rate >= 2) return 'engagement-average';
    return 'engagement-poor';
};

window.getTaskTypeName = function(type) {
    const types = {
        'search': 'Поиск по ключевым словам',
        'channel_parse': 'Парсинг канала',
        'video_parse': 'Парсинг видео',
        'analysis': 'Анализ контента'
    };
    return types[type] || type;
};

window.getTaskStatusName = function(status) {
    const statuses = {
        'pending': 'Ожидание',
        'running': 'Выполняется',
        'paused': 'Приостановлено',
        'completed': 'Завершено',
        'failed': 'Ошибка',
        'cancelled': 'Отменено'
    };
    return statuses[status] || status;
};

window.getTaskStatusClass = function(status) {
    const classes = {
        'pending': 'bg-gray-100 text-gray-800',
        'running': 'bg-blue-100 text-blue-800',
        'paused': 'bg-yellow-100 text-yellow-800',
        'completed': 'bg-green-100 text-green-800',
        'failed': 'bg-red-100 text-red-800',
        'cancelled': 'bg-gray-100 text-gray-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
};
