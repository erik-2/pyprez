/**
 * Système de Navigation pour Présentation avec Co-slides
 * Version finale sans slides cachées
 */

const PresentationNav = (function() {
    'use strict';

    let currentSlide = 0;  // Index de la slide principale (0, 1, 2...)
    let currentView = 0;   // 0=main, 1=detail, 2=question
    let totalSlides = 0;
    let slideGroups = [];  // [{main, detail, question, hasAnnexes}, ...]

    // Touch
    let touchStartX = 0, touchStartY = 0, touchEndX = 0, touchEndY = 0;
    let touchStartScrollTop = 0;
    const minSwipeDistance = 50;

    /**
     * Construit les groupes de slides
     * Parcourt toutes les slides et les groupe intelligemment
     */
    function buildSlideGroups() {
        slideGroups = [];
        const allSlides = Array.from(document.querySelectorAll('.slide'));
        let i = 0;
        
        while (i < allSlides.length) {
            const mainSlide = allSlides[i];
            
            if (!mainSlide.classList.contains('slide-main')) {
                console.warn('⚠️ Slide non-main trouvée en position main:', i);
                i++;
                continue;
            }
            
            const hasAnnexes = mainSlide.getAttribute('data-no-annexes') !== 'true';
            
            const group = {
                main: mainSlide,
                detail: null,
                question: null,
                hasAnnexes: hasAnnexes
            };
            
            if (hasAnnexes) {
                // Slide avec annexes : prendre les 2 suivantes
                group.detail = allSlides[i + 1];
                group.question = allSlides[i + 2];
                i += 3;
            } else {
                // Slide sans annexes : juste la main
                // Ajouter des placeholders pour aligner la grille
                for (let j = 0; j < 2; j++) {
                    const placeholder = document.createElement('div');
                    placeholder.classList.add('slide');
                    placeholder.style.visibility = 'hidden';
                    mainSlide.after(placeholder);
                }
                i += 1;
            }
            
            slideGroups.push(group);
        }
        
        console.log(`📦 ${slideGroups.length} slides principales:`, slideGroups.map((g, idx) => 
            `${idx}: ${g.hasAnnexes ? 'AVEC' : 'SANS'} annexes`
        ));
        console.log(slideGroups);
    }

    /**
     * Retourne l'élément DOM à afficher
     */
    function getActiveElement() {
        if (currentSlide < 0 || currentSlide >= slideGroups.length) return null;
        
        const group = slideGroups[currentSlide];
        
        if (currentView === 0) return group.main;
        if (currentView === 1 && group.hasAnnexes) return group.detail;
        if (currentView === 2 && group.hasAnnexes) return group.question;
        
        return group.main; // Fallback
    }

    /**
     * Vérifie si une slide a des annexes
     */
    function hasAnnexes(slideIndex) {
        return slideIndex >= 0 && slideIndex < slideGroups.length && slideGroups[slideIndex].hasAnnexes;
    }

    /**
     * Met à jour la position de la grille
     */
    function updatePosition() {
        const grid = document.getElementById('slidesGrid');
        
        let col = currentView;
        if (!hasAnnexes(currentSlide)) {
            col = 0;
            currentView = 0;
        }
        
        const row = currentSlide;
        
        const translateX = -col * 100;
        const translateY = -row * 100;
        
        grid.style.transform = `translate(${translateX}vw, ${translateY}vh)`;
        
        console.log(`✅ Slide ${currentSlide}, Vue ${currentView} → ligne ${row}, col ${col} → (${translateX}vw, ${translateY}vh)`);
        
        updateFixedElementsVisibility();
        
        setTimeout(() => {
            const el = getActiveElement();
            if (el) el.scrollTop = 0;
        }, 100);
    }

    /**
     * Gère la visibilité des éléments fixes
     */
    function updateFixedElementsVisibility() {
        // Masquer tous
        document.querySelectorAll('.slide-detail, .slide-question').forEach(slide => {
            const pos = slide.querySelector('.position-indicator');
            const nav = slide.querySelector('.nav-hint');
            if (pos) pos.style.opacity = '0';
            if (nav) nav.style.opacity = '0';
        });
        
        // Afficher l'actif
        if (currentView > 0) {
            const active = getActiveElement();
            if (active) {
                const pos = active.querySelector('.position-indicator');
                const nav = active.querySelector('.nav-hint');
                if (pos) pos.style.opacity = '0.7';
                if (nav) nav.style.opacity = '0.6';
            }
        }
    }

    /**
     * Navigation clavier
     */
    function handleKeyboard(e) {
        const active = getActiveElement();
        
        // Gestion du scroll sur slides défilables
        if (active && (active.classList.contains('slide-detail') || active.classList.contains('slide-question')) && currentView > 0) {
            const isAtTop = active.scrollTop <= 1;
            const isAtBottom = Math.abs(active.scrollHeight - active.scrollTop - active.clientHeight) <= 2;
            
            if (e.key === 'ArrowDown' && !isAtBottom) return;
            if (e.key === 'ArrowUp' && !isAtTop) return;
        }
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (currentSlide < totalSlides - 1) {
                    currentSlide++;
                    currentView = 0;
                    updatePosition();
                }
                break;
            
            case 'ArrowUp':
                e.preventDefault();
                if (currentSlide > 0) {
                    currentSlide--;
                    currentView = 0;
                    updatePosition();
                }
                break;
            
            case 'ArrowRight':
                e.preventDefault();
                if (!hasAnnexes(currentSlide)) return;
                if (currentView < 2) {
                    currentView++;
                    updatePosition();
                    setTimeout(() => {
                        const el = getActiveElement();
                        if (el) el.scrollTop = 0;
                    }, 100);
                }
                break;
            
            case 'ArrowLeft':
                e.preventDefault();
                if (currentView > 0) {
                    currentView--;
                    updatePosition();
                }
                break;
        }
    }

    /**
     * Touch
     */
    function handleTouchStart(e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
        
        const scrollable = document.elementFromPoint(touchStartX, touchStartY)?.closest('.slide-detail, .slide-question');
        touchStartScrollTop = scrollable ? scrollable.scrollTop : 0;
    }

    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    }

    function handleSwipe() {
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        const active = getActiveElement();
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            if (Math.abs(deltaX) > minSwipeDistance) {
                if (deltaX > 0) {
                    if (currentView > 0) {
                        currentView--;
                        updatePosition();
                    }
                } else {
                    if (!hasAnnexes(currentSlide)) return;
                    if (currentView < 2) {
                        currentView++;
                        updatePosition();
                        setTimeout(() => {
                            const el = getActiveElement();
                            if (el) el.scrollTop = 0;
                        }, 100);
                    }
                }
            }
        } else {
            if (Math.abs(deltaY) > minSwipeDistance) {
                if (active && (active.classList.contains('slide-detail') || active.classList.contains('slide-question')) && currentView > 0) {
                    const isAtTop = active.scrollTop <= 1;
                    const isAtBottom = Math.abs(active.scrollHeight - active.scrollTop - active.clientHeight) <= 2;
                    
                    if (deltaY > 0) {
                        if (!isAtTop || active.scrollTop !== touchStartScrollTop) return;
                        if (currentSlide > 0) {
                            currentSlide--;
                            currentView = 0;
                            updatePosition();
                        }
                    } else {
                        if (!isAtBottom || active.scrollTop !== touchStartScrollTop) return;
                        if (currentSlide < totalSlides - 1) {
                            currentSlide++;
                            currentView = 0;
                            updatePosition();
                        }
                    }
                } else {
                    if (deltaY > 0) {
                        if (currentSlide > 0) {
                            currentSlide--;
                            currentView = 0;
                            updatePosition();
                        }
                    } else {
                        if (currentSlide < totalSlides - 1) {
                            currentSlide++;
                            currentView = 0;
                            updatePosition();
                        }
                    }
                }
            }
        }
    }

    /**
     * Initialisation
     */
    function init(total) {
        if (!total || total < 1) {
            console.error('❌ totalSlides invalide');
            return;
        }

        totalSlides = total;
        buildSlideGroups();

        if (slideGroups.length !== totalSlides) {
            console.error(`❌ ERREUR: ${slideGroups.length} slides détectées mais ${totalSlides} attendues!`);
            console.error('Vérifiez votre HTML: chaque slide SANS annexes ne doit avoir QUE la slide principale (pas de slides cachées)');
        }

        document.addEventListener('keydown', handleKeyboard);
        document.addEventListener('touchstart', handleTouchStart, false);
        document.addEventListener('touchend', handleTouchEnd, false);

        currentSlide = 0;
        currentView = 0;
        updatePosition();

        console.log(`✅ PresentationNav: ${totalSlides} slides attendues, ${slideGroups.length} détectées`);
    }

    function destroy() {
        document.removeEventListener('keydown', handleKeyboard);
        document.removeEventListener('touchstart', handleTouchStart);
        document.removeEventListener('touchend', handleTouchEnd);
    }

    function goTo(slideIndex, view = 0) {
        if (slideIndex < 0 || slideIndex >= totalSlides || view < 0 || view > 2) {
            console.error('❌ Index invalide');
            return;
        }
        currentSlide = slideIndex;
        currentView = view;
        updatePosition();
    }

    function getCurrentPosition() {
        return { slide: currentSlide, view: currentView, total: totalSlides };
    }

    return { init, destroy, goTo, getCurrentPosition };
})();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PresentationNav;
}
