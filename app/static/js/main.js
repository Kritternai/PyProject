function loadPage(page) {
  fetch('/partial/' + page)
    .then(response => {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json().then(handleJsonRedirect);
      } else {
        return response.text().then(html => {
          document.getElementById('main-content').innerHTML = html;
          if (page === 'dashboard') setupFullCalendar();
          setupAuthForms();
          setupLessonForms();
          setupLessonEditForm(); // <-- เพิ่มตรงนี้
        });
      }
    });
}

function updateSidebarAuth() {
  fetch('/partial/sidebar-auth')
    .then(r => r.text())
    .then(html => {
      document.querySelector('.sidebar-auth').innerHTML = html;
    });
}

function handleJsonRedirect(data) {
  if (data.redirect) {
    updateSidebarAuth();
    loadPage(data.redirect);
  } else if (data.message) {
    alert(data.message);
  }
}

function setupAuthForms() {
  // login
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(loginForm);
      fetch('/partial/login', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(r => r.json())
      .then(handleJsonRedirect)
      .catch(() => showAuthError(loginForm, 'Login failed.'));
    };
  }
  // register
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(registerForm);
      fetch('/partial/register', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(r => r.json())
      .then(handleJsonRedirect)
      .catch(() => showAuthError(registerForm, 'Registration failed.'));
    };
  }
  // change password
  const changePasswordForm = document.getElementById('change-password-form');
  if (changePasswordForm) {
    changePasswordForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(changePasswordForm);
      fetch('/partial/change_password', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          loadPage(data.redirect || 'profile');
        } else {
          showAuthError(changePasswordForm, data.message);
        }
      })
      .catch(() => showAuthError(changePasswordForm, 'Change password failed.'));
    };
  }
}

function showAuthError(form, message) {
  let alert = form.parentNode.querySelector('.alert');
  if (!alert) {
    alert = document.createElement('div');
    alert.className = 'alert alert-danger mt-2';
    form.parentNode.insertBefore(alert, form);
  }
  alert.textContent = message;
}

function loadLessonDetail(lessonId) {
  fetch('/partial/class/' + lessonId)
    .then(response => response.text())
    .then(html => {
      document.getElementById('main-content').innerHTML = html;
    });
}

function setupFullCalendar() {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) return;
  if (window.fullcalendar_events && window.initial_date) {
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'timeGridWeek',
      initialDate: window.initial_date,
      validRange: {
        start: window.initial_date,
        end: moment(window.initial_date).add(16, 'weeks').format('YYYY-MM-DD')
      },
      headerToolbar: {
        left: '',
        center: '',
        right: ''
      },
      dayHeaderFormat: {
        weekday: 'short'
      },
      slotMinTime: '08:00:00',
      slotMaxTime: '21:00:00',
      weekends: false,
      allDaySlot: false,
      events: window.fullcalendar_events,
      eventClick: function(info) {
        if (info.event.url && info.event.url !== 'null') {
          info.jsEvent.preventDefault();
          window.open(info.event.url);
        }
      },
      eventDidMount: function(info) {
        if (info.event.extendedProps.description) {
          let descriptionEl = document.createElement('div');
          descriptionEl.classList.add('fc-event-description');
          descriptionEl.innerHTML = info.event.extendedProps.description;
          info.el.querySelector('.fc-event-title').after(descriptionEl);
        }
      }
    });
    calendar.render();
  }
}

function setupLessonForms() {
  const addLessonForm = document.getElementById('add-lesson-form');
  if (addLessonForm) {
    addLessonForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(addLessonForm);
      fetch('/partial/class/add', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          loadPage(data.redirect || 'class');
        } else {
          alert(data.message || 'Error adding lesson.');
        }
      });
    };
  }
}

function setupLessonEditForm() {
  const editLessonForm = document.getElementById('edit-lesson-form');
  if (editLessonForm) {
    editLessonForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(editLessonForm);
      const lessonId = editLessonForm.dataset.lessonId;
      fetch(`/partial/class/${lessonId}/edit`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          loadPage(data.redirect || `class/${lessonId}`);
        } else {
          alert(data.message || 'Error updating lesson.');
        }
      });
    };
  }
}

document.addEventListener('DOMContentLoaded', function() {
  setupAuthForms();
});
// ถ้าใช้ SPA หรือ htmx ให้เรียก checkRegisterRedirect หลังเปลี่ยนหน้า
// หรือเรียก checkRegisterRedirect() หลังทุกครั้งที่ SPA เปลี่ยนหน้า 