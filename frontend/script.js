// API URL
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : '';

// DOM Elements
const taskForm = document.getElementById('task-form');
const taskTitle = document.getElementById('task-title');
const taskPriority = document.getElementById('task-priority');
const taskDate = document.getElementById('task-date');
const tasksList = document.getElementById('tasks-list');
const filterTabs = document.querySelectorAll('.tab-btn');
const toast = document.getElementById('toast');

// Language Switcher
const langButtons = document.querySelectorAll('.lang-btn');

const translations = {
    tr: {
        appTitle: '📋 Görev Yöneticisi Agent',
        appSubtitle: 'Yapay zeka destekli akıllı görev takip asistanınız',
        addTaskTitle: '➕ Yeni Görev Ekle',
        taskTitleLabel: 'Görev Başlığı',
        taskTitlePlaceholder: 'Örn: Proje sunumu hazırla',
        priorityLabel: 'Öncelik',
        priorityLow: '🟢 Düşük',
        priorityMedium: '🟡 Orta',
        priorityHigh: '🔴 Yüksek',
        dueDateLabel: 'Son Tarih',
        addTaskButton: 'Görev Ekle',
        dailyReportTitle: '📊 Günlük Rapor',
        totalTasks: 'Toplam Görev',
        completedTasks: 'Tamamlanan',
        pendingTasks: 'Bekleyen',
        today: 'Bugün',
        agentRecommendationsTitle: '🤖 Agent Önerileri',
        recommendationsLoading: 'Öneriler analiz ediliyor...',
        myTasksTitle: '📋 Görevlerim',
        filterAll: 'Tümü',
        filterPending: 'Bekleyen',
        filterCompleted: 'Tamamlanan',
        filterHigh: '🔴 Yüksek Öncelik',
        emptyTasks: 'Henüz görev eklenmemiş',
        emptyTasksHint: 'Yukarıdan yeni görev ekleyerek başlayın!',
        footerText: 'Powered by AI Agent • Medium Yazısından Öğrendiniz 🚀'
    },
    en: {
        appTitle: '📋 Task Manager Agent',
        appSubtitle: 'Your AI-powered smart task tracking assistant',
        addTaskTitle: '➕ Add New Task',
        taskTitleLabel: 'Task Title',
        taskTitlePlaceholder: 'Example: Prepare project presentation',
        priorityLabel: 'Priority',
        priorityLow: '🟢 Low',
        priorityMedium: '🟡 Medium',
        priorityHigh: '🔴 High',
        dueDateLabel: 'Due Date',
        addTaskButton: 'Add Task',
        dailyReportTitle: '📊 Daily Report',
        totalTasks: 'Total Tasks',
        completedTasks: 'Completed',
        pendingTasks: 'Pending',
        today: 'Today',
        agentRecommendationsTitle: '🤖 Agent Recommendations',
        recommendationsLoading: 'Analyzing recommendations...',
        myTasksTitle: '📋 My Tasks',
        filterAll: 'All',
        filterPending: 'Pending',
        filterCompleted: 'Completed',
        filterHigh: '🔴 High Priority',
        emptyTasks: 'No tasks added yet',
        emptyTasksHint: 'Start by adding a new task above!',
        footerText: 'Powered by AI Agent • Built from the Medium tutorial 🚀'
    }
};

let currentLang = localStorage.getItem('appLanguage') || 'tr';

// Stats
const statTotal = document.getElementById('stat-total');
const statCompleted = document.getElementById('stat-completed');
const statPending = document.getElementById('stat-pending');
const currentDate = document.getElementById('current-date');

// Recommendations
const recommendationsContent = document.getElementById('recommendations-content');

// Global state
let currentFilter = 'all';
let tasks = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setDefaultDate();
    loadTasks();
    loadReport();
    loadRecommendations();
    setupEventListeners();
    applyLanguage();
});

// Set default date to today
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    taskDate.value = today;
    currentDate.textContent = new Date().toLocaleDateString('tr-TR', { 
        day: 'numeric', 
        month: 'short' 
    });
}

// Setup event listeners
function setupEventListeners() {
    taskForm.addEventListener('submit', handleAddTask);
    
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentFilter = tab.dataset.filter;
            renderTasks();
        });
    });

    langButtons.forEach(button => {
        button.addEventListener('click', () => {
            currentLang = button.dataset.lang;
            localStorage.setItem('appLanguage', currentLang);
            applyLanguage();
        });
    });
}

// Add new task
async function handleAddTask(e) {
    e.preventDefault();
    
    const taskData = {
        baslik: taskTitle.value.trim(),
        oncelik: taskPriority.value,
        tarih: taskDate.value
    };
    
    try {
        const response = await fetch(`${API_URL}/api/gorevler`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Görev başarıyla eklendi!', 'success');
            taskForm.reset();
            setDefaultDate();
            loadTasks();
            loadReport();
            loadRecommendations();
        } else {
            showToast(data.error || 'Görev eklenirken hata oluştu', 'error');
        }
    } catch (error) {
        showToast('Bağlantı hatası: ' + error.message, 'error');
    }
}

// Load tasks
async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/api/gorevler`);
        const data = await response.json();
        
        if (data.success) {
            tasks = data.gorevler;
            renderTasks();
        }
    } catch (error) {
        console.error('Görevler yüklenirken hata:', error);
    }
}

// Render tasks
function renderTasks() {
    let filteredTasks = [...tasks];
    
    // Apply filters
    if (currentFilter === 'pending') {
        filteredTasks = tasks.filter(t => !t.tamamlandi);
    } else if (currentFilter === 'completed') {
        filteredTasks = tasks.filter(t => t.tamamlandi);
    } else if (currentFilter === 'yüksek') {
        filteredTasks = tasks.filter(t => t.oncelik === 'yüksek' && !t.tamamlandi);
    }
    
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>Bu kategoride görev yok</p>
                <small>Farklı bir filtre deneyin veya yeni görev ekleyin!</small>
            </div>
        `;
        return;
    }
    
    // Sort by priority and date
    const priorityOrder = { 'yüksek': 1, 'orta': 2, 'düşük': 3 };
    filteredTasks.sort((a, b) => {
        if (a.tamamlandi !== b.tamamlandi) {
            return a.tamamlandi ? 1 : -1;
        }

        const priorityDiff = priorityOrder[a.oncelik] - priorityOrder[b.oncelik];

        if (priorityDiff !== 0) {
            return priorityDiff;
        }

        return new Date(a.tarih) - new Date(b.tarih);
    });
    
    tasksList.innerHTML = filteredTasks.map(task => createTaskHTML(task)).join('');
    
    // Attach event listeners
    document.querySelectorAll('.btn-calendar').forEach(btn => {
        btn.addEventListener('click', () => addToGoogleCalendar(parseInt(btn.dataset.id)));
    });

    document.querySelectorAll('.btn-complete').forEach(btn => {
        btn.addEventListener('click', () => completeTask(parseInt(btn.dataset.id)));
    });
    
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', () => deleteTask(parseInt(btn.dataset.id)));
    });
}

// Create task HTML
function createTaskHTML(task) {
    const dateInfo = getDateInfo(task.tarih);
    const priorityEmoji = {
        'yüksek': '🔴',
        'orta': '🟡',
        'düşük': '🟢'
    };

    const priorityText = getPriorityText(task.oncelik);
    const completedText = currentLang === 'en' ? 'Completed' : 'Tamamlandı';
    
    return `
        <div class="task-item ${task.tamamlandi ? 'completed' : ''} priority-${task.oncelik}">
            <div class="task-content">
                <div class="task-header">
                    <div class="task-title ${task.tamamlandi ? 'completed' : ''}">
                        ${escapeHTML(task.baslik)}
                    </div>
                    <span class="task-priority ${task.oncelik}">
                        ${priorityEmoji[task.oncelik]} ${priorityText}
                    </span>
                </div>
                <div class="task-meta">
                    <span class="task-date ${dateInfo.class}">
                        📅 ${formatDate(task.tarih)} ${dateInfo.label}
                    </span>
                    ${task.tamamlandi ? `<span>✅ ${completedText}</span>` : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="btn-icon-only btn-calendar" data-id="${task.id}" title="${currentLang === 'en' ? 'Add to Google Calendar' : 'Google Takvim’e Ekle'}">
                    📅
                </button>
                
                ${!task.tamamlandi ? `
                    <button class="btn-icon-only btn-complete" data-id="${task.id}" title="${currentLang === 'en' ? 'Complete' : 'Tamamla'}">
                        ✓
                    </button>
                ` : ''}
                
                <button class="btn-icon-only btn-delete" data-id="${task.id}" title="${currentLang === 'en' ? 'Delete' : 'Sil'}">
                    🗑️
                </button>
            </div>
        </div>
    `;
}

// Get date info
function getDateInfo(dateStr) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const taskDate = new Date(dateStr);
    taskDate.setHours(0, 0, 0, 0);
    
    const diffDays = Math.floor((taskDate - today) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
        return {
            class: 'overdue',
            label: currentLang === 'en'
                ? `(${Math.abs(diffDays)} day${Math.abs(diffDays) > 1 ? 's' : ''} overdue)`
                : `(${Math.abs(diffDays)} gün gecikti)`
        };
    }

    if (diffDays === 0) {
        return {
            class: 'today',
            label: currentLang === 'en' ? '(TODAY!)' : '(BUGÜN!)'
        };
    }

    if (diffDays <= 3) {
        return {
            class: 'upcoming',
            label: currentLang === 'en'
                ? `(${diffDays} day${diffDays > 1 ? 's' : ''} left)`
                : `(${diffDays} gün kaldı)`
        };
    }

    return { class: '', label: '' };
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);

    const locale = currentLang === 'en' ? 'en-US' : 'tr-TR';

    return date.toLocaleDateString(locale, { 
        day: 'numeric', 
        month: 'long',
        year: 'numeric'
    });
}

function getPriorityText(priority) {
    const priorityMap = {
        tr: {
            'yüksek': 'Yüksek',
            'orta': 'Orta',
            'düşük': 'Düşük'
        },
        en: {
            'yüksek': 'High',
            'orta': 'Medium',
            'düşük': 'Low'
        }
    };

    return priorityMap[currentLang][priority] || priority;
}

// Complete task
async function completeTask(taskId) {
    try {
        const response = await fetch(`${API_URL}/api/gorevler/${taskId}`, {
            method: 'PUT'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Görev tamamlandı! 🎉', 'success');
            loadTasks();
            loadReport();
            loadRecommendations();
        } else {
            showToast(data.error || 'Görev tamamlanırken hata oluştu', 'error');
        }
    } catch (error) {
        showToast('Bağlantı hatası: ' + error.message, 'error');
    }
}

// Add task to Google Calendar
function addToGoogleCalendar(taskId) {
    const task = tasks.find(t => t.id === taskId);

    if (!task) {
        showToast('Görev bulunamadı.', 'error');
        return;
    }

    const startDate = formatDateForGoogleCalendar(task.tarih, 9, 0);
    const endDate = formatDateForGoogleCalendar(task.tarih, 10, 0);

    const title = encodeURIComponent(task.baslik);
    const details = encodeURIComponent(
        `Görev: ${task.baslik}\n` +
        `Öncelik: ${task.oncelik}\n` +
        `Görev Yöneticisi Agent tarafından oluşturuldu.`
    );

    const googleCalendarUrl =
        `https://calendar.google.com/calendar/render?action=TEMPLATE` +
        `&text=${title}` +
        `&dates=${startDate}/${endDate}` +
        `&details=${details}`;

    window.open(googleCalendarUrl, '_blank');
    showToast('Google Takvim açılıyor 📅', 'success');
}

function formatDateForGoogleCalendar(dateStr, hour = 9, minute = 0) {
    const date = new Date(dateStr);
    date.setHours(hour, minute, 0, 0);

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = '00';

    return `${year}${month}${day}T${hours}${minutes}${seconds}`;
}

// Delete task
async function deleteTask(taskId) {
    if (!confirm('Bu görevi silmek istediğinize emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/gorevler/${taskId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Görev silindi', 'success');
            loadTasks();
            loadReport();
            loadRecommendations();
        } else {
            showToast(data.error || 'Görev silinirken hata oluştu', 'error');
        }
    } catch (error) {
        showToast('Bağlantı hatası: ' + error.message, 'error');
    }
}

// Load report
async function loadReport() {
    try {
        const response = await fetch(`${API_URL}/api/rapor`);
        const data = await response.json();
        
        if (data.success) {
            const rapor = data.rapor;
            statTotal.textContent = rapor.toplam_gorev;
            statCompleted.textContent = rapor.tamamlanan;
            statPending.textContent = rapor.bekleyen;
        }
    } catch (error) {
        console.error('Rapor yüklenirken hata:', error);
    }
}

// Load recommendations
async function loadRecommendations() {
    try {
        const response = await fetch(`${API_URL}/api/oneriler?lang=${currentLang}`);
        const data = await response.json();
        
        if (data.success) {
            renderRecommendations(data.oneriler);
        }
    } catch (error) {
        console.error('Öneriler yüklenirken hata:', error);
    }
}

// Render recommendations
function renderRecommendations(data) {
    let html = '';

    // Natural rule-based recommendation
    if (data.dogal_oneri) {
        html += `
            <div class="recommendation-card natural-recommendation">
                <div class="recommendation-header">
                    <span>🤖</span>
                    <span style="font-weight: 700;">Agent’ın Doğal Önerisi</span>
                </div>
                <div class="recommendation-body natural-text">
                    ${escapeHTML(data.dogal_oneri)}
                </div>
            </div>
        `;
    }

    // LLM recommendation, only if backend produced one
    if (data.llm_oneri) {
        html += `
            <div class="recommendation-card llm-recommendation">
                <div class="recommendation-header">
                    <span>🧠</span>
                    <span style="font-weight: 700;">AI Agent Yorumu</span>
                </div>
                <div class="recommendation-body llm-text">
                    ${escapeHTML(data.llm_oneri)}
                </div>
            </div>
        `;
    }

    if (data.durum === 'tamamlandi') {
        html += `
            <div class="empty-recommendations">
                <div class="icon">🎉</div>
                <p>${escapeHTML(data.mesaj)}</p>
            </div>
        `;

        recommendationsContent.innerHTML = html;
        return;
    }
    
    if (!data.oneriler || data.oneriler.length === 0) {
        html += `
            <div class="empty-recommendations">
                <div class="icon">✨</div>
                <p>Şu an için önerim yok. Görevleriniz kontrol altında!</p>
            </div>
        `;

        recommendationsContent.innerHTML = html;
        return;
    }
    
    const typeClassMap = {
        'gecikme': 'danger',
        'bugun': 'warning',
        'oncelik': 'warning',
        'deadline': 'info'
    };
    
    // Rule-based recommendation cards
    html += data.oneriler.map(oneri => `
        <div class="recommendation-card ${typeClassMap[oneri.tip] || ''}">
            <div class="recommendation-header">
                <span>${oneri.ikon}</span>
                <span>${escapeHTML(oneri.mesaj)}</span>
            </div>
            ${oneri.oneri ? `
                <div class="recommendation-body">
                    ${escapeHTML(oneri.oneri)}
                </div>
            ` : ''}
        </div>
    `).join('');
    
    recommendationsContent.innerHTML = html;
}

// Show toast notification
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Escape HTML to avoid unwanted HTML injection in task titles and AI outputs
function escapeHTML(value) {
    if (value === null || value === undefined) {
        return '';
    }

    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

// Apply selected language to static UI elements
function applyLanguage() {
    document.documentElement.lang = currentLang;

    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.dataset.i18n;

        if (translations[currentLang] && translations[currentLang][key]) {
            element.textContent = translations[currentLang][key];
        }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.dataset.i18nPlaceholder;

        if (translations[currentLang] && translations[currentLang][key]) {
            element.placeholder = translations[currentLang][key];
        }
    });

    langButtons.forEach(button => {
        button.classList.toggle('active', button.dataset.lang === currentLang);
    });

    renderTasks();
}

// Auto refresh every 30 seconds
setInterval(() => {
    loadReport();
    loadRecommendations();
}, 30000);