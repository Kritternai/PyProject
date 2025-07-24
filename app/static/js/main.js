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
          setupSectionForms(); // เรียก setupSectionForms หลัง loadPage
          setupNoteForms(); // เรียก setupNoteForms หลัง loadPage
          setupLessonAddModal(); // เรียก setupLessonAddModal หลัง loadPage
          setupSectionFilter(); // เรียก setupSectionFilter() หลัง loadPage
          // Auto show Lesson Content tab and scroll if on lesson detail
          if (page.startsWith('class/')) {
            // Activate Content tab
            const contentTabBtn = document.getElementById('content-tab');
            if (contentTabBtn) {
              contentTabBtn.click();
            }
            // Scroll to Lesson Content section
            setTimeout(() => {
              const lessonContent = document.querySelector('.card-body');
              if (lessonContent) lessonContent.scrollIntoView({behavior: 'smooth', block: 'start'});
            }, 300);
          }
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

function setupSectionForms() {
  // Modal logic
  const addSectionModal = document.getElementById('addSectionModal');
  const addSectionForm = document.getElementById('add-section-form');
  if (addSectionModal && addSectionForm) {
    addSectionModal.addEventListener('show.bs.modal', function () {
      addSectionForm.reset();
      const typeSelect = document.getElementById('type');
      if (typeSelect) typeSelect.dispatchEvent(new Event('change'));
      setTimeout(() => {
        const titleInput = document.getElementById('title');
        if (titleInput) titleInput.focus();
      }, 300);
    });
    // Dynamic field toggle
    const typeSelect = document.getElementById('type');
    if (typeSelect) {
      typeSelect.addEventListener('change', function() {
        const type = typeSelect.value;
        document.getElementById('content-group').classList.toggle('d-none', type === 'file');
        document.getElementById('file-group').classList.toggle('d-none', type !== 'file');
        document.getElementById('due-group').classList.toggle('d-none', type !== 'assignment');
        document.getElementById('content').required = (type !== 'file');
        document.getElementById('file').required = (type === 'file');
        document.getElementById('assignment_due').required = (type === 'assignment');
        // Dynamic label/placeholder
        const contentLabel = document.getElementById('content-label');
        const content = document.getElementById('content');
        if (type === 'text') {
          contentLabel.textContent = 'Content';
          content.placeholder = 'Enter content or instructions';
        } else if (type === 'assignment') {
          contentLabel.textContent = 'Assignment Instructions';
          content.placeholder = 'Enter assignment details or instructions';
        } else if (type === 'note') {
          contentLabel.textContent = 'Note';
          content.placeholder = 'Enter your note';
        }
      });
      // Trigger on load
      typeSelect.dispatchEvent(new Event('change'));
    }
    // Submit add section form
    addSectionForm.onsubmit = function(e) {
      e.preventDefault();
      const typeSelect = document.getElementById('type');
      const type = typeSelect ? typeSelect.value : '';
      const filesInput = document.getElementById('files');
      if (type === 'file' && filesInput && filesInput.files.length === 0) {
        alert('Please select at least one file.');
        filesInput.focus();
        return;
      }
      const formData = new FormData(addSectionForm);
      fetch(addSectionForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success && data.html) {
          document.getElementById('lesson-sections-list').innerHTML = data.html;
          // ปิด modal
          const modal = bootstrap.Modal.getOrCreateInstance(addSectionModal);
          modal.hide();
          addSectionForm.reset();
        } else {
          alert(data.message || 'Error adding content.');
        }
      });
    };
  }
}

function setupSectionFilter() {
  const filter = document.getElementById('section-type-filter');
  const keywordInput = document.getElementById('section-keyword-filter');
  const dueInput = document.getElementById('section-due-filter');
  function doFilter() {
    const val = filter ? filter.value : 'all';
    const keyword = keywordInput ? keywordInput.value.trim().toLowerCase() : '';
    const due = dueInput ? dueInput.value : '';
    const cards = document.querySelectorAll('#lesson-sections-list .card');
    cards.forEach(card => {
      const type = card.getAttribute('data-type');
      const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
      const content = card.querySelector('.mt-2')?.textContent.toLowerCase() || '';
      let show = (val === 'all' || type === val);
      if (keyword) {
        show = show && (title.includes(keyword) || content.includes(keyword));
      }
      if (due && type === 'assignment') {
        // หา due date ใน card
        const dueText = card.querySelector('.text-danger.small')?.textContent || '';
        // คาดว่า dueText มีรูปแบบ 'Due: YYYY-MM-DD HH:MM'
        const match = dueText.match(/Due:\s*(\d{4}-\d{2}-\d{2})/);
        if (match && match[1]) {
          show = show && (match[1] === due);
        } else {
          show = false;
        }
      }
      card.parentElement.style.display = show ? '' : 'none';
    });
  }
  if (filter) filter.onchange = doFilter;
  if (keywordInput) keywordInput.onkeyup = doFilter;
  if (dueInput) dueInput.onchange = doFilter;
}

// Edit Section (inline)
window.editSection = function(lessonId, sectionId) {
  // โหลดฟอร์มแก้ไขมาแสดงแทนฟอร์ม add
  fetch(`/partial/class/${lessonId}/sections/${sectionId}/edit`)
    .then(r => r.text())
    .then(html => {
      const addForm = document.getElementById('add-section-form');
      if (addForm) addForm.classList.add('d-none');
      let editDiv = document.getElementById('edit-section-form-wrapper');
      if (!editDiv) {
        editDiv = document.createElement('div');
        editDiv.id = 'edit-section-form-wrapper';
        addForm.parentNode.insertBefore(editDiv, addForm);
      }
      editDiv.innerHTML = html;
      // setup dynamic field toggle for edit form
      const typeSelect = document.getElementById('type');
      if (typeSelect) {
        typeSelect.addEventListener('change', function() {
          const type = typeSelect.value;
          document.getElementById('content-group').classList.toggle('d-none', type === 'file');
          document.getElementById('file-group').classList.toggle('d-none', type !== 'file');
          document.getElementById('due-group').classList.toggle('d-none', type !== 'assignment');
          document.getElementById('content').required = (type !== 'file');
          document.getElementById('file').required = (type === 'file');
          document.getElementById('assignment_due').required = (type === 'assignment');
          // Dynamic label/placeholder
          const contentLabel = document.getElementById('content-label');
          const content = document.getElementById('content');
          if (type === 'text') {
            contentLabel.textContent = 'Content';
            content.placeholder = 'Enter content or instructions';
          } else if (type === 'assignment') {
            contentLabel.textContent = 'Assignment Instructions';
            content.placeholder = 'Enter assignment details or instructions';
          } else if (type === 'note') {
            contentLabel.textContent = 'Note';
            content.placeholder = 'Enter your note';
          }
        });
        typeSelect.dispatchEvent(new Event('change'));
      }
      // setup submit
      const editForm = document.getElementById('edit-section-form');
      if (editForm) {
        editForm.onsubmit = function(e) {
          e.preventDefault();
          const formData = new FormData(editForm);
          fetch(editForm.action, {
            method: 'POST',
            body: formData,
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'Accept': 'application/json'
            }
          })
          .then(r => r.json())
          .then(data => {
            if (data.success && data.html) {
              document.getElementById('lesson-sections-list').innerHTML = data.html;
              editDiv.remove();
            } else {
              alert(data.message || 'Error updating content.');
            }
          });
        };
      }
    });
};

// Delete Section (SPA)
window.deleteSection = function(lessonId, sectionId) {
  if (!confirm('Delete this content?')) return;
  fetch(`/partial/class/${lessonId}/sections/${sectionId}/delete`, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json'
    }
  })
  .then(r => r.json())
  .then(data => {
    if (data.success && data.html) {
      document.getElementById('lesson-sections-list').innerHTML = data.html;
    } else {
      alert(data.message || 'Error deleting content.');
    }
  });
}; 

// Global functions for note operations
window.loadNoteEdit = function(noteId) {
  console.log('DEBUG: Loading note edit for ID:', noteId);
  
  const mainContent = document.getElementById('main-content');
  console.log('DEBUG: Target element:', mainContent);
  
  if (!mainContent) {
    console.error('DEBUG: main-content element not found!');
    alert('Error: main-content element not found');
    return;
  }
  
  const url = `/partial/note/${noteId}/edit`;
  console.log('DEBUG: Fetching URL:', url);
  
  fetch(url)
    .then(response => {
      console.log('DEBUG: Response status:', response.status);
      console.log('DEBUG: Response headers:', response.headers);
      return response.text();
    })
    .then(html => {
      console.log('DEBUG: Received HTML response length:', html.length);
      console.log('DEBUG: HTML preview:', html.substring(0, 200));
      mainContent.innerHTML = html;
      setupNoteEditForm();
    })
    .catch(error => {
      console.error('Error loading note edit page:', error);
      alert('Error loading note edit page');
    });
};

window.deleteNote = function(noteId) {
  console.log('DEBUG: Deleting note with ID:', noteId);
  if (confirm('Are you sure you want to delete this note?')) {
    fetch(`/partial/note/${noteId}/delete`, {
      method: 'POST'
    })
    .then(response => response.text())
    .then(html => {
      console.log('DEBUG: Delete successful, updating HTML');
      document.getElementById('note-list-container').outerHTML = html;
    })
    .catch(error => {
      console.error('Error deleting note:', error);
      alert('Error deleting note');
    });
  }
};

function setupNoteEditForm() {
  const editNoteForm = document.getElementById('edit-note-form');
  if (editNoteForm) {
    editNoteForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(editNoteForm);
      const sectionId = editNoteForm.dataset.sectionId;
      fetch(`/partial/note/${sectionId}/edit`, {
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
          loadPage(data.redirect || 'note');
        } else {
          alert(data.message || 'Error updating note.');
        }
      });
    };
  }
}

function setupNoteForms() {
  const addNoteModal = document.getElementById('addNoteModal');
  const addNoteForm = document.getElementById('add-note-form');
  if (addNoteModal && addNoteForm) {
    addNoteModal.addEventListener('show.bs.modal', function () {
      addNoteForm.reset();
      setTimeout(() => {
        const titleInput = addNoteForm.querySelector('#title');
        if (titleInput) titleInput.focus();
      }, 300);
    });

    addNoteForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(addNoteForm);
      fetch(addNoteForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success && data.html) {
          document.getElementById('main-content').innerHTML = data.html;
          const modal = bootstrap.Modal.getInstance(addNoteModal);
          modal.hide();
          addNoteForm.reset();
        } else {
          alert(data.message || 'Error adding note.');
        }
      });
    };
  }
}

function setupLessonAddModal() {
  const addLessonModal = document.getElementById('addLessonModal');
  const addLessonForm = document.getElementById('add-lesson-form');
  if (addLessonModal && addLessonForm) {
    addLessonModal.addEventListener('show.bs.modal', function () {
      addLessonForm.reset();
      setTimeout(() => {
        const titleInput = addLessonForm.querySelector('#title');
        if (titleInput) titleInput.focus();
      }, 300);
    });

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
          const modal = bootstrap.Modal.getInstance(addLessonModal);
          modal.hide();
          addLessonForm.reset();
        } else {
          alert(data.message || 'Error adding lesson.');
        }
      });
    };
  }
}