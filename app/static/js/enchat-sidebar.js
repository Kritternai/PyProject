/**
 * ENCHAT SIDEBAR ENHANCEMENTS
 * Interactive features and utilities for the Enchat Sidebar
 */

(function() {
  'use strict';

  /**
   * Sidebar Controller
   */
  const SidebarController = {
    sidebar: null,
    isCollapsed: false,
    isMobile: false,

    /**
     * Initialize the sidebar
     */
    init() {
      this.sidebar = document.querySelector('.enchat-sidebar');
      if (!this.sidebar) return;

      this.checkMobile();
      this.setupEventListeners();
      this.restoreState();
      this.setupScrollSpy();
      this.setupTooltips();
    },

    /**
     * Check if device is mobile
     */
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
      // Handle window resize
      let resizeTimer;
      window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
          this.checkMobile();
          this.handleResize();
        }, 250);
      });

      // Handle nav link clicks with smooth animation
      const navLinks = document.querySelectorAll('.enchat-sidebar__nav-link');
      navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
          this.handleNavClick(e, link);
        });
      });

      // Handle dropdown toggle animation
      const dropdownBtn = document.querySelector('.enchat-sidebar__user-btn');
      if (dropdownBtn) {
        dropdownBtn.addEventListener('click', () => {
          this.animateDropdownIcon(dropdownBtn);
        });
      }

      // Close dropdown when clicking outside
      document.addEventListener('click', (e) => {
        const dropdown = document.querySelector('.enchat-sidebar__user.dropdown');
        if (dropdown && !dropdown.contains(e.target)) {
          const dropdownMenu = dropdown.querySelector('.dropdown-menu');
          if (dropdownMenu && dropdownMenu.classList.contains('show')) {
            const bsDropdown = bootstrap.Dropdown.getInstance(dropdownBtn);
            if (bsDropdown) bsDropdown.hide();
          }
        }
      });
    },

    /**
     * Handle nav link clicks
     */
    handleNavClick(e, link) {
      // Add ripple effect
      this.createRipple(e, link);
      
      // Update active state with animation
      this.updateActiveNav(link);
      
      // Save to localStorage
      const page = link.dataset.page;
      if (page) {
        localStorage.setItem('enchant-active-page', page);
      }
    },

    /**
     * Create ripple effect on click
     */
    createRipple(e, element) {
      const ripple = document.createElement('span');
      const rect = element.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        left: ${x}px;
        top: ${y}px;
        animation: enchat-ripple 0.6s ease-out;
        pointer-events: none;
      `;

      element.style.position = 'relative';
      element.style.overflow = 'hidden';
      element.appendChild(ripple);

      setTimeout(() => ripple.remove(), 600);
    },

    /**
     * Update active navigation state
     */
    updateActiveNav(activeLink) {
      const links = document.querySelectorAll('.enchat-sidebar__nav-link');
      links.forEach(link => {
        link.classList.remove('active');
        link.style.animation = 'none';
      });
      
      activeLink.classList.add('active');
      activeLink.style.animation = 'enchat-slideIn 0.3s ease-out';
    },

    /**
     * Animate dropdown icon
     */
    animateDropdownIcon(btn) {
      const icon = btn.querySelector('.enchat-sidebar__user-dropdown-icon');
      if (icon) {
        icon.style.transition = 'transform 0.3s ease';
      }
    },

    /**
     * Setup scroll spy for menu
     */
    setupScrollSpy() {
      const menu = document.querySelector('.enchat-sidebar__menu');
      if (!menu) return;

      let scrollTimeout;
      menu.addEventListener('scroll', () => {
        menu.classList.add('scrolling');
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
          menu.classList.remove('scrolling');
        }, 150);
      });
    },

    /**
     * Setup tooltips for collapsed state
     */
    setupTooltips() {
      if (this.isCollapsed && window.bootstrap && bootstrap.Tooltip) {
        const navLinks = document.querySelectorAll('.enchat-sidebar__nav-link');
        navLinks.forEach(link => {
          const text = link.querySelector('.enchat-sidebar__nav-text');
          if (text) {
            new bootstrap.Tooltip(link, {
              title: text.textContent,
              placement: 'right',
              trigger: 'hover'
            });
          }
        });
      }
    },

    /**
     * Restore sidebar state from localStorage
     */
    restoreState() {
      const activePage = localStorage.getItem('enchant-active-page');
      if (activePage) {
        const activeLink = document.querySelector(`.enchat-sidebar__nav-link[data-page="${activePage}"]`);
        if (activeLink) {
          activeLink.classList.add('active');
        }
      }
    },

    /**
     * Handle window resize
     */
    handleResize() {
      if (this.isMobile) {
        this.sidebar.classList.add('enchat-sidebar--mobile');
      } else {
        this.sidebar.classList.remove('enchat-sidebar--mobile');
      }
    },

    /**
     * Toggle sidebar (for future collapse feature)
     */
    toggle() {
      this.isCollapsed = !this.isCollapsed;
      this.sidebar.classList.toggle('enchat-sidebar--collapsed');
      localStorage.setItem('enchant-sidebar-collapsed', this.isCollapsed);
      
      // Dispatch custom event
      window.dispatchEvent(new CustomEvent('enchat-sidebar-toggled', {
        detail: { isCollapsed: this.isCollapsed }
      }));
    }
  };

  /**
   * Badge Manager - For notification badges
   */
  const BadgeManager = {
    /**
     * Add badge to nav item
     */
    addBadge(page, count) {
      const link = document.querySelector(`.enchat-sidebar__nav-link[data-page="${page}"]`);
      if (!link) return;

      let badge = link.querySelector('.enchat-sidebar__nav-badge');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'enchat-sidebar__nav-badge';
        link.appendChild(badge);
      }

      badge.textContent = count > 99 ? '99+' : count;
      badge.style.display = count > 0 ? 'inline-flex' : 'none';
    },

    /**
     * Remove badge from nav item
     */
    removeBadge(page) {
      const link = document.querySelector(`.enchat-sidebar__nav-link[data-page="${page}"]`);
      if (!link) return;

      const badge = link.querySelector('.enchat-sidebar__nav-badge');
      if (badge) {
        badge.remove();
      }
    },

    /**
     * Update badge count
     */
    updateBadge(page, count) {
      if (count > 0) {
        this.addBadge(page, count);
      } else {
        this.removeBadge(page);
      }
    }
  };

  /**
   * Theme Manager - For switching sidebar themes
   */
  const ThemeManager = {
    themes: ['purple', 'blue', 'green', 'dark', 'light'],
    
    /**
     * Apply theme to sidebar
     */
    applyTheme(themeName) {
      const sidebar = document.querySelector('.enchat-sidebar');
      if (!sidebar) return;

      // Remove all theme classes
      this.themes.forEach(theme => {
        sidebar.classList.remove(`enchat-sidebar--${theme}`);
      });

      // Add new theme class
      if (this.themes.includes(themeName)) {
        sidebar.classList.add(`enchat-sidebar--${themeName}`);
        localStorage.setItem('enchat-sidebar-theme', themeName);
      }
    },

    /**
     * Get current theme
     */
    getCurrentTheme() {
      return localStorage.getItem('enchat-sidebar-theme') || 'purple';
    },

    /**
     * Restore theme from localStorage
     */
    restoreTheme() {
      const theme = this.getCurrentTheme();
      this.applyTheme(theme);
    }
  };

  /**
   * Add custom CSS for ripple animation
   */
  function addRippleAnimation() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes enchat-ripple {
        from {
          opacity: 1;
          transform: scale(0);
        }
        to {
          opacity: 0;
          transform: scale(2);
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Initialize everything when DOM is ready
   */
  function init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        addRippleAnimation();
        SidebarController.init();
        ThemeManager.restoreTheme();
      });
    } else {
      addRippleAnimation();
      SidebarController.init();
      ThemeManager.restoreTheme();
    }
  }

  // Auto-initialize
  init();

  // Expose API to window
  window.EnchatSidebar = {
    controller: SidebarController,
    badges: BadgeManager,
    themes: ThemeManager
  };

})();

/**
 * Example Usage:
 * 
 * // Toggle sidebar
 * window.EnchatSidebar.controller.toggle();
 * 
 * // Add notification badge
 * window.EnchatSidebar.badges.addBadge('note', 5);
 * window.EnchatSidebar.badges.addBadge('class', 3);
 * 
 * // Change theme
 * window.EnchatSidebar.themes.applyTheme('blue');
 * window.EnchatSidebar.themes.applyTheme('green');
 * window.EnchatSidebar.themes.applyTheme('dark');
 * 
 * // Listen to sidebar toggle events
 * window.addEventListener('enchat-sidebar-toggled', (e) => {
 *   console.log('Sidebar collapsed:', e.detail.isCollapsed);
 * });
 */

