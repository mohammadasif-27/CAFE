document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('[data-nav-toggle]');
  const mobileNav = document.querySelector('[data-mobile-nav]');
  const mobileNavLinks = document.querySelectorAll('[data-mobile-nav] a');
  const navLinks = document.querySelectorAll('.nav-link');
  const filterButtons = document.querySelectorAll('[data-filter]');
  const menuCards = document.querySelectorAll('.menu-card');
  const cartButtons = document.querySelectorAll('.add-to-cart');
  const sections = document.querySelectorAll('section[id]');
  const lightbox = document.querySelector('[data-lightbox]');
  const lightboxImage = document.querySelector('[data-lightbox-image]');
  const lightboxCaption = document.querySelector('[data-lightbox-caption]');
  const galleryItems = document.querySelectorAll('[data-gallery-item]');
  const contactForm = document.querySelector('#contact-form');
  const formFeedback = document.querySelector('[data-form-feedback]');
  const navbar = document.querySelector('.navbar');

  const closeMobileNav = () => {
    mobileNav.classList.remove('mobile-nav--open');
    navToggle.setAttribute('aria-expanded', 'false');
  };

  const openMobileNav = () => {
    mobileNav.classList.add('mobile-nav--open');
    navToggle.setAttribute('aria-expanded', 'true');
  };

  navToggle.addEventListener('click', () => {
    const isOpen = mobileNav.classList.contains('mobile-nav--open');
    if (isOpen) {
      closeMobileNav();
    } else {
      openMobileNav();
    }
  });

  mobileNavLinks.forEach((link) => link.addEventListener('click', closeMobileNav));

  navLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      const targetId = link.getAttribute('href');
      if (targetId.startsWith('#')) {
        event.preventDefault();
        document.querySelector(targetId).scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;
      filterButtons.forEach((btn) => btn.classList.remove('filter-button--active'));
      button.classList.add('filter-button--active');
      menuCards.forEach((card) => {
        const category = card.dataset.category;
        const matches = filter === 'all' || category === filter;
        card.style.display = matches ? 'grid' : 'none';
      });
    });
  });

  cartButtons.forEach((button) => {
    button.addEventListener('click', () => {
      button.classList.add('button-clicked');
      const itemName = button.closest('.menu-card').querySelector('.menu-card__title').textContent;
      const toast = document.createElement('div');
      toast.className = 'toast-message';
      toast.textContent = `${itemName} added to cart.`;
      document.body.appendChild(toast);
      setTimeout(() => toast.classList.add('toast-message--visible'), 10);
      setTimeout(() => {
        toast.classList.remove('toast-message--visible');
        setTimeout(() => toast.remove(), 300);
      }, 1800);
      setTimeout(() => button.classList.remove('button-clicked'), 500);
    });
  });

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const id = entry.target.id;
      const activeLink = document.querySelector(`.nav-link[href="#${id}"]`);
      if (activeLink) {
        if (entry.isIntersecting) {
          navLinks.forEach((link) => link.classList.remove('nav-link--active'));
          activeLink.classList.add('nav-link--active');
        }
      }
    });
  }, { threshold: 0.55 });
  sections.forEach((section) => sectionObserver.observe(section));

  const pageObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-visible');
      }
    });
  }, { threshold: 0.2 });

  document.querySelectorAll('.animate-on-scroll').forEach((element) => pageObserver.observe(element));

  const onScroll = () => {
    if (window.scrollY > 20) {
      navbar.classList.add('navbar--scrolled');
    } else {
      navbar.classList.remove('navbar--scrolled');
    }
  };
  window.addEventListener('scroll', onScroll);
  onScroll();

  const openLightbox = (imageUrl, captionText) => {
    lightboxImage.src = imageUrl;
    lightboxImage.alt = captionText;
    lightboxCaption.textContent = captionText;
    lightbox.classList.add('lightbox--open');
    document.body.style.overflow = 'hidden';
  };

  const closeLightbox = () => {
    lightbox.classList.remove('lightbox--open');
    document.body.style.overflow = '';
  };

  galleryItems.forEach((item) => {
    item.addEventListener('click', () => {
      openLightbox(item.dataset.image, item.dataset.caption);
    });
  });

  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox || event.target.closest('.lightbox__close')) {
      closeLightbox();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && lightbox.classList.contains('lightbox--open')) {
      closeLightbox();
    }
  });

  if (contactForm) {
    contactForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const name = contactForm.elements.name.value.trim();
      const email = contactForm.elements.email.value.trim();
      const phone = contactForm.elements.phone.value.trim();
      const message = contactForm.elements.message.value.trim();
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const phonePattern = /^[0-9+\s-]{7,20}$/;
      let error = '';

      if (!name) {
        error = 'Please enter your name.';
      } else if (!email || !emailPattern.test(email)) {
        error = 'Please enter a valid email address.';
      } else if (!phone || !phonePattern.test(phone)) {
        error = 'Please enter a valid phone number.';
      } else if (!message) {
        error = 'Please write a short message.';
      }

      if (error) {
        formFeedback.textContent = error;
        formFeedback.classList.remove('success');
        formFeedback.classList.add('error');
      } else {
        formFeedback.textContent = 'Message ready to send! Thank you for reaching out.';
        formFeedback.classList.remove('error');
        formFeedback.classList.add('success');
        contactForm.reset();
      }
    });
  }

  // Password visibility toggle used on auth forms
  const passwordToggles = document.querySelectorAll('.password-toggle');
  passwordToggles.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const parent = btn.closest('div') || btn.parentElement;
      const input = parent.querySelector('input[type="password"], input[type="text"]');
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Hide';
        btn.setAttribute('aria-pressed', 'true');
      } else {
        input.type = 'password';
        btn.textContent = 'Show';
        btn.setAttribute('aria-pressed', 'false');
      }
    });
  });
});