// 国际化功能
// 当前语言
let currentLang = localStorage.getItem('preferred_language') || 'zh';
let i18n = {};

// 动态加载JSON
async function loadI18n(lang) {
    const resp = await fetch(`/static/i18n/${lang}.json`);
    i18n = await resp.json();
}

// 切换语言函数
async function switchLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('preferred_language', lang);
    await loadI18n(lang);
    // 更新所有文本
    document.title = i18n['title'];
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (i18n[key]) {
            element.textContent = i18n[key];
        }
    });
    // 更新placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (i18n[key]) {
            element.placeholder = i18n[key];
        }
    });
    // 更新语言切换按钮状态
    document.querySelectorAll('.lang-switch').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });
}

// 页面加载完成后初始化语言
document.addEventListener('DOMContentLoaded', async () => {
    await switchLanguage(currentLang);
}); 