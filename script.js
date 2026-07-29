/* ============================================
   LINETTKA — Photography Portfolio
   Interactive Script
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  // --- Page Loader ---
  const loader = document.getElementById('loader');
  window.addEventListener('load', () => {
    setTimeout(() => {
      loader.classList.add('is-hidden');
      setTimeout(() => loader.remove(), 700);
    }, 600);
  });

  // --- Navigation ---
  const nav = document.getElementById('nav');
  const navBurger = document.getElementById('navBurger');
  const navLinks = document.getElementById('navLinks');
  const navLinkElements = document.querySelectorAll('.nav__link');

  // Scroll effect for nav
  const handleNavScroll = () => {
    nav.classList.toggle('is-scrolled', window.scrollY > 50);
  };
  window.addEventListener('scroll', handleNavScroll, { passive: true });
  handleNavScroll();

  // Burger menu toggle
  navBurger.addEventListener('click', () => {
    nav.classList.toggle('is-open');
    navBurger.classList.toggle('is-open');
    navLinks.classList.toggle('is-open');
    document.body.style.overflow = navLinks.classList.contains('is-open') ? 'hidden' : '';
  });

  // Close mobile menu on link click
  navLinkElements.forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('is-open');
      navBurger.classList.remove('is-open');
      navLinks.classList.remove('is-open');
      document.body.style.overflow = '';
    });
  });

  // Active section tracking
  const sections = document.querySelectorAll('section[id]');
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -60% 0px',
    threshold: 0
  };

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navLinkElements.forEach(link => {
          link.classList.toggle('is-active', link.dataset.section === id);
        });
      }
    });
  }, observerOptions);

  sections.forEach(section => sectionObserver.observe(section));

  // --- Fade-in on Scroll ---
  const fadeElements = document.querySelectorAll('.fade-in');
  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        fadeObserver.unobserve(entry.target);
      }
    });
  }, {
    root: null,
    rootMargin: '0px 0px -80px 0px',
    threshold: 0.1
  });

  fadeElements.forEach(el => fadeObserver.observe(el));

  // --- Lazy Loading with High-Res Swap ---
  const lazyImages = document.querySelectorAll('.gallery__item img[data-src]');
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const highResSrc = img.dataset.src;
        if (highResSrc) {
          // Create a new image to preload
          const preloader = new Image();
          preloader.onload = () => {
            img.src = highResSrc;
            img.removeAttribute('data-src');
          };
          preloader.src = highResSrc;
        }
        imageObserver.unobserve(img);
      }
    });
  }, {
    root: null,
    rootMargin: '200px 400px 200px 400px', // Preload images well before they appear
    threshold: 0
  });

  lazyImages.forEach(img => imageObserver.observe(img));

  // --- Gallery Horizontal Scroll ---
  const galleryTrack = document.getElementById('galleryTrack');
  const galleryPrev = document.getElementById('galleryPrev');
  const galleryNext = document.getElementById('galleryNext');

  // Scroll amount per click
  const getScrollAmount = () => {
    return window.innerWidth * 0.6;
  };

  galleryPrev.addEventListener('click', () => {
    galleryTrack.scrollBy({ left: -getScrollAmount(), behavior: 'smooth' });
  });

  galleryNext.addEventListener('click', () => {
    galleryTrack.scrollBy({ left: getScrollAmount(), behavior: 'smooth' });
  });

  // Drag to scroll (desktop)
  let isDragging = false;
  let startX;
  let scrollLeft;
  let dragVelocity = 0;
  let lastX;
  let lastTime;

  galleryTrack.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.pageX - galleryTrack.offsetLeft;
    scrollLeft = galleryTrack.scrollLeft;
    lastX = e.pageX;
    lastTime = Date.now();
    dragVelocity = 0;
    galleryTrack.style.cursor = 'grabbing';
    galleryTrack.style.scrollBehavior = 'auto';
    e.preventDefault();
  });

  galleryTrack.addEventListener('mouseleave', () => {
    if (isDragging) {
      isDragging = false;
      galleryTrack.style.cursor = 'grab';
      galleryTrack.style.scrollBehavior = 'smooth';
      applyMomentum();
    }
  });

  galleryTrack.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      galleryTrack.style.cursor = 'grab';
      galleryTrack.style.scrollBehavior = 'smooth';
      applyMomentum();
    }
  });

  galleryTrack.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const x = e.pageX - galleryTrack.offsetLeft;
    const walk = (x - startX) * 1.5;
    galleryTrack.scrollLeft = scrollLeft - walk;

    // Track velocity for momentum
    const now = Date.now();
    const dt = now - lastTime;
    if (dt > 0) {
      dragVelocity = (e.pageX - lastX) / dt;
    }
    lastX = e.pageX;
    lastTime = now;
  });

  function applyMomentum() {
    const momentum = dragVelocity * 150;
    if (Math.abs(momentum) > 10) {
      galleryTrack.scrollBy({ left: -momentum, behavior: 'smooth' });
    }
  }

  // Prevent click on gallery items after drag
  let dragDistance = 0;
  galleryTrack.addEventListener('mousedown', (e) => {
    dragDistance = 0;
  });

  galleryTrack.addEventListener('mousemove', () => {
    if (isDragging) dragDistance++;
  });

  // --- Gallery Filters ---
  const filterButtons = document.querySelectorAll('.gallery__filter-btn');
  const galleryItems = document.querySelectorAll('.gallery__item');

  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;

      // Update active button
      filterButtons.forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');

      // Start fade-out transition
      galleryTrack.classList.add('is-filtering');

      setTimeout(() => {
        // Filter items
        galleryItems.forEach(item => {
          const category = item.dataset.category;
          const shouldShow = filter === 'all' || category === filter;

          if (shouldShow) {
            item.classList.remove('is-hidden');
          } else {
            item.classList.add('is-hidden');
          }
        });

        // Update counter
        updateGalleryCounter();

        // Scroll gallery to start instantly (while track is transparent)
        galleryTrack.scrollTo({ left: 0 });

        // Fade-in transition back
        galleryTrack.classList.remove('is-filtering');
      }, 250);
    });
  });

  // Gallery counter
  function updateGalleryCounter() {
    const counter = document.getElementById('galleryCounter');
    const visible = document.querySelectorAll('.gallery__item:not(.is-hidden)');
    counter.textContent = `${visible.length} фото`;
  }
  updateGalleryCounter();

  // --- Lightbox ---
  const lightbox = document.getElementById('lightbox');
  const lightboxImage = document.getElementById('lightboxImage');
  const lightboxClose = document.getElementById('lightboxClose');
  const lightboxPrev = document.getElementById('lightboxPrev');
  const lightboxNext = document.getElementById('lightboxNext');
  const lightboxCounter = document.getElementById('lightboxCounter');
  let currentLightboxIndex = 0;

  function getVisibleImages() {
    return Array.from(document.querySelectorAll('.gallery__item:not(.is-hidden) img'));
  }

  function openLightbox(index) {
    const images = getVisibleImages();
    if (index < 0 || index >= images.length) return;

    currentLightboxIndex = index;
    const img = images[index];
    const src = img.dataset.src || img.src;

    lightboxImage.src = src;
    lightboxCounter.textContent = `${index + 1} / ${images.length}`;
    lightbox.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('is-open');
    document.body.style.overflow = '';
    setTimeout(() => {
      lightboxImage.src = '';
    }, 400);
  }

  function navigateLightbox(direction) {
    const images = getVisibleImages();
    currentLightboxIndex += direction;
    if (currentLightboxIndex < 0) currentLightboxIndex = images.length - 1;
    if (currentLightboxIndex >= images.length) currentLightboxIndex = 0;
    openLightbox(currentLightboxIndex);
  }

  // Click on gallery item to open lightbox
  galleryItems.forEach(item => {
    item.addEventListener('click', (e) => {
      // Don't open if we were dragging
      if (dragDistance > 5) return;

      const images = getVisibleImages();
      const img = item.querySelector('img');
      const index = images.indexOf(img);
      if (index !== -1) {
        openLightbox(index);
      }
    });
  });

  lightboxClose.addEventListener('click', closeLightbox);
  lightboxPrev.addEventListener('click', () => navigateLightbox(-1));
  lightboxNext.addEventListener('click', () => navigateLightbox(1));

  // Close on background click
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('is-open')) return;

    switch (e.key) {
      case 'Escape':
        closeLightbox();
        break;
      case 'ArrowLeft':
        navigateLightbox(-1);
        break;
      case 'ArrowRight':
        navigateLightbox(1);
        break;
    }
  });

  // Touch swipe for lightbox
  let touchStartX = 0;
  let touchEndX = 0;

  lightbox.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  lightbox.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > 50) {
      navigateLightbox(diff > 0 ? 1 : -1);
    }
  }, { passive: true });

  // --- Smooth Scroll for anchor links ---
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        const navHeight = nav.offsetHeight;
        const targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight;
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // --- Gift Certificate Toggle ---
  const certificateToggle = document.getElementById('certificateToggle');
  const certificateDetails = document.getElementById('certificateDetails');

  if (certificateToggle && certificateDetails) {
    certificateToggle.addEventListener('click', () => {
      const isOpen = certificateDetails.classList.toggle('is-open');
      certificateToggle.setAttribute('aria-expanded', isOpen);
    });
  }

  // --- Pricing Tabs Accordion Toggle / Collapse ---
  const pricingTabBtns = document.querySelectorAll('[data-pricing-tab]');
  const pricingDetailCards = document.querySelectorAll('.pricing__detail-card');

  pricingTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabTarget = btn.getAttribute('data-pricing-tab');
      const isAlreadyActive = btn.classList.contains('is-active');

      if (isAlreadyActive) {
        // Collapse active item
        btn.classList.remove('is-active');
        btn.setAttribute('aria-expanded', 'false');

        pricingDetailCards.forEach(card => {
          card.classList.remove('is-active');
        });
      } else {
        // Expand target item and collapse others
        pricingTabBtns.forEach(b => {
          b.classList.remove('is-active');
          b.setAttribute('aria-expanded', 'false');
        });

        btn.classList.add('is-active');
        btn.setAttribute('aria-expanded', 'true');

        pricingDetailCards.forEach(card => {
          card.classList.remove('is-active');
          if (card.id === `pricingDetail-${tabTarget}`) {
            void card.offsetWidth; // Trigger reflow for smooth animation
            card.classList.add('is-active');
          }
        });
      }
    });
  });
});
