/**
 * Fragrantica Explorer - Main JavaScript
 */

// ═══════════════════════════════════════════════════════════
// Initialisation
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌸 Fragrantica Explorer loaded');
    
    // Initialiser les animations
    initAnimations();
    
    // Auto-dismiss des messages flash
    autoDismissFlashMessages();
    
    // Améliorer la recherche
    enhanceSearch();
});

// ═══════════════════════════════════════════════════════════
// Animations
// ═══════════════════════════════════════════════════════════
function initAnimations() {
    // Fade-in pour les cartes de parfums
    const cards = document.querySelectorAll('.perfume-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(20px)';
                    entry.target.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    
                    requestAnimationFrame(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    });
                }, index * 50);
                
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    cards.forEach(card => observer.observe(card));
}

// ═══════════════════════════════════════════════════════════
// Messages Flash
// ═══════════════════════════════════════════════════════════
function autoDismissFlashMessages() {
    const messages = document.querySelectorAll('.flash-messages .alert');
    
    messages.forEach(message => {
        // Auto-dismiss après 5 secondes
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
        
        // Permettre de fermer manuellement
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.className = 'alert-close';
        closeBtn.onclick = () => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        };
        message.appendChild(closeBtn);
    });
}

// ═══════════════════════════════════════════════════════════
// Recherche améliorée
// ═══════════════════════════════════════════════════════════
function enhanceSearch() {
    const searchInput = document.querySelector('.search-input');
    
    if (!searchInput) return;
    
    // Debounce pour éviter trop de requêtes
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        
        searchTimeout = setTimeout(() => {
            const query = e.target.value.trim();
            
            if (query.length >= 3) {
                // Optionnel: suggestions en temps réel
                console.log('Recherche:', query);
            }
        }, 300);
    });
}

// ═══════════════════════════════════════════════════════════
// Utilitaires
// ═══════════════════════════════════════════════════════════

/**
 * Formatte un nombre avec des espaces comme séparateurs de milliers
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

/**
 * Copie du texte dans le presse-papier
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copié !', 'success');
    } catch (err) {
        console.error('Erreur de copie:', err);
        showNotification('Erreur de copie', 'error');
    }
}

/**
 * Affiche une notification temporaire
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Styles pour les animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .alert-close {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: none;
        border: none;
        color: inherit;
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0.7;
        line-height: 1;
    }
    
    .alert-close:hover {
        opacity: 1;
    }
    
    .alert {
        position: relative;
        padding: 1rem 2rem 1rem 1rem;
        margin: 0.5rem;
        border-radius: 0.5rem;
        transition: opacity 0.3s ease;
    }
    
    .alert-success {
        background: #D1FAE5;
        color: #065F46;
        border-left: 4px solid #10B981;
    }
    
    .alert-error {
        background: #FEE2E2;
        color: #991B1B;
        border-left: 4px solid #EF4444;
    }
    
    .alert-info {
        background: #DBEAFE;
        color: #1E40AF;
        border-left: 4px solid #3B82F6;
    }
    
    .flash-messages {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9998;
        max-width: 400px;
    }
`;
document.head.appendChild(style);