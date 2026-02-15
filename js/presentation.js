/**
 * Navigation pour Présentation avec slides annexes
 * Supporte: data-no-annexes="true" et data-max-view="1"
 */

const PresentationNav = (function() {
    'use strict';

    let currentSlide = 0;
    let currentView = 0;   // 0=main, 1=detail, 2=question
    let totalSlides = 0;
    let slideGroups = [];

    // Touch
    let touchStartX = 0, touchStartY = 0, touchEndX = 0, touchEndY = 0;
    let touchStartScrollTop = 0;
    const minSwipeDistance = 50;

    /**
     * Construit les groupes de slides
     */
    function buildSlideGroups() {
        slideGroups = [];
        const allSlides = Array.from(document.querySelectorAll('.slide'));
        let i = 0;
        
        while (i < allSlides.length) {
            const mainSlide = allSlides[i];
            
            if (!mainSlide.classList.contains('slide-main') && !mainSlide.classList.contains('slide-section')) {
               i++;
                continue;
            }
            
            // Déterminer maxView
            let maxView = 2;
            if (mainSlide.dataset.noAnnexes === 'true') {
                maxView = 0;
            } else if (mainSlide.dataset.maxView === '1') {
                maxView = 1;
            } else if (mainSlide.classList.contains('slide-section')) {
               maxView = 0;
            }
            
            const group = {
                main: mainSlide,
                detail: null,
                question: null,
                maxView: maxView
            };
            
            if (maxView === 0) {
                // Sans annexes: ajouter placeholders
                for (let j = 0; j < 2; j++) {
                    const ph = document.createElement('div');
                    ph.className = 'slide';
                    ph.style.visibility = 'hidden';
                    mainSlide.after(ph);
                }
                i += 1;
            } else {
                // Avec annexes
                group.detail = allSlides[i + 1];
                if (maxView === 2) {
                    group.question = allSlides[i + 2];
                }
                i += 3;
            }
            
            slideGroups.push(group);
        }
        
        console.log(`📦 ${slideGroups.length} slides:`, 
            slideGroups.map((g, i) => `${i}:maxView=${g.maxView}`).join(', '));
    }

    function getMaxView(idx) {
        return (idx >= 0 && idx < slideGroups.length) ? slideGroups[idx].maxView : 0;
    }

    function getActiveElement() {
        if (currentSlide < 0 || currentSlide >= slideGroups.length) return null;
        const g = slideGroups[currentSlide];
        if (currentView === 0) return g.main;
        if (currentView === 1 && g.maxView >= 1) return g.detail;
        if (currentView === 2 && g.maxView >= 2) return g.question;
        return g.main;
    }

    function updatePosition() {
        const grid = document.getElementById('slidesGrid');
        const maxView = getMaxView(currentSlide);
        
        if (currentView > maxView) {
            currentView = maxView;
        }
        
        grid.style.transform = `translate(${-currentView * 100}vw, ${-currentSlide * 100}vh)`;
        
        updateFixedElements();
        
        setTimeout(() => {
            const el = getActiveElement();
            if (el) el.scrollTop = 0;
        }, 100);
    }

    function updateFixedElements() {
        // Masquer tous
        document.querySelectorAll('.slide-detail, .slide-question').forEach(s => {
            const p = s.querySelector('.position-indicator');
            const n = s.querySelector('.nav-hint');
            if (p) p.style.opacity = '0';
            if (n) n.style.opacity = '0';
        });
        
        // Afficher actif
        if (currentView > 0) {
            const active = getActiveElement();
            if (active) {
                const p = active.querySelector('.position-indicator');
                const n = active.querySelector('.nav-hint');
                if (p) p.style.opacity = '0.7';
                if (n) n.style.opacity = '0.6';
            }
        }
    }

    function handleKeyboard(e) {
        const active = getActiveElement();
        const maxView = getMaxView(currentSlide);
        
        // Scroll sur slides défilables
        if (active && currentView > 0) {
            const isScrollable = active.classList.contains('slide-detail') || 
                                 active.classList.contains('slide-question');
            if (isScrollable) {
                const atTop = active.scrollTop <= 1;
                const atBottom = Math.abs(active.scrollHeight - active.scrollTop - active.clientHeight) <= 2;
                if (e.key === 'ArrowDown' && !atBottom) return;
                if (e.key === 'ArrowUp' && !atTop) return;
            }
        }
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (currentSlide < totalSlides - 1) {
                    currentSlide++;
                    currentView = 0;
                    updatePosition();
                    updateHash();
                }
                break;
            
            case 'ArrowUp':
                e.preventDefault();
                if (currentSlide > 0) {
                    currentSlide--;
                    currentView = 0;
                    updatePosition();
                    updateHash();
                }
                break;
            
            case 'ArrowRight':
                e.preventDefault();
                if (currentView < maxView) {
                    currentView++;
                    updatePosition();
                }
                break;
            
            case 'ArrowLeft':
                e.preventDefault();
                if (currentView > 0) {
                    currentView--;
                    updatePosition();
                }
                break;

            case 'q':
            case 'Q':
            case 'Escape':
                history.back();
                break;
        }
    }

    
    function handleTouchStart(e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
        const scrollable = document.elementFromPoint(touchStartX, touchStartY)
            ?.closest('.slide-detail, .slide-question');
        touchStartScrollTop = scrollable ? scrollable.scrollTop : 0;
    }

    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    }

    function handleSwipe() {
        const dX = touchEndX - touchStartX;
        const dY = touchEndY - touchStartY;
        const maxView = getMaxView(currentSlide);
        
        if (Math.abs(dX) > Math.abs(dY) && Math.abs(dX) > minSwipeDistance) {
            // Swipe horizontal
            if (dX > 0 && currentView > 0) {
                currentView--;
                updatePosition();
            } else if (dX < 0 && currentView < maxView) {
                currentView++;
                updatePosition();
            }
        } else if (Math.abs(dY) > minSwipeDistance) {
            // Swipe vertical
            if (dY > 0 && currentSlide > 0) {
                currentSlide--;
                currentView = 0;
                updatePosition();
            } else if (dY < 0 && currentSlide < totalSlides - 1) {
                currentSlide++;
                currentView = 0;
                updatePosition();
            }
        }
    }

    function init(total) {
        if (!total || total < 1) {
            console.error('❌ totalSlides invalide');
            return;
        }

        totalSlides = total;
        buildSlideGroups();

        document.addEventListener('keydown', handleKeyboard);
        document.addEventListener('touchstart', handleTouchStart, false);
        document.addEventListener('touchend', handleTouchEnd, false);

        currentSlide = 0;
        currentView = 0;
        updatePosition();
        initFromHash();

    }

    function initFromHash() {
       const hash = window.location.hash;
        if (hash && hash.startsWith('#slide-')) {
            const slideNum = parseInt(hash.replace('#slide-', ''), 10);
            if (!isNaN(slideNum) && slideNum > 0) {
                goTo(slideNum);
            }
        }
    }

    function destroy() {
        document.removeEventListener('keydown', handleKeyboard);
        document.removeEventListener('touchstart', handleTouchStart);
        document.removeEventListener('touchend', handleTouchEnd);
    }

    function updateHash() {
        const slideNum = currentSlide;
        history.replaceState(null, null, `#slide-${slideNum}`);
    }

    function goTo(slideIndex, view = 0) {
        if (slideIndex < 0 || slideIndex >= totalSlides) return;
        currentSlide = slideIndex;
        currentView = Math.min(view, getMaxView(slideIndex));
        updatePosition();
        updateHash(slideIndex);
    }

    function getCurrentPosition() {
        return { slide: currentSlide, view: currentView, total: totalSlides };
    }

    return { init, destroy, goTo, getCurrentPosition };
})();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PresentationNav;
}
