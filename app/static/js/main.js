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
          setupLessonSearchAndFilter(); // เรียก setupLessonSearchAndFilter หลัง loadPage
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
    alert.className = 'mt-2 alert alert-danger';
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

// Function to populate edit note modal with data
window.populateEditNoteModal = function(button) {
  const noteId = button.getAttribute('data-note-id');
  const noteTitle = button.getAttribute('data-note-title');
  const noteBody = button.getAttribute('data-note-body');
  const noteTags = button.getAttribute('data-note-tags');
  const noteStatus = button.getAttribute('data-note-status');
  const noteExternalLink = button.getAttribute('data-note-external-link');
  
  // Set form action
  const editForm = document.getElementById('edit-note-form');
  editForm.action = `/partial/note/${noteId}/edit`;
  editForm.method = 'post';
  
  // Populate form fields
  document.getElementById('edit-note-id').value = noteId;
  document.getElementById('edit-title').value = noteTitle;
  document.getElementById('edit-body').value = noteBody;
  document.getElementById('edit-tags').value = noteTags;
  document.getElementById('edit-status').value = noteStatus;
  document.getElementById('edit-external-link').value = noteExternalLink;

  // Show preview for existing image/file
  const imagePath = button.getAttribute('data-note-image');
  const filePath = button.getAttribute('data-note-file');
  const imagePreview = document.getElementById('edit-image-preview');
  const filePreview = document.getElementById('edit-file-preview');
  imagePreview.innerHTML = '';
  filePreview.innerHTML = '';
  if (imagePath) {
    const img = document.createElement('img');
    img.src = '/static/' + imagePath;
    img.className = 'img-fluid';
    img.style.maxHeight = '200px';
    imagePreview.appendChild(img);
  }
  if (filePath && filePath.endsWith('.pdf')) {
    const embed = document.createElement('embed');
    embed.src = '/static/' + filePath;
    embed.type = 'application/pdf';
    embed.width = '100%';
    embed.height = '300px';
    filePreview.appendChild(embed);
  }
};

function setupEditNotePreview() {
  // Image preview
  const imageInput = document.getElementById('edit-image');
  const imagePreview = document.getElementById('edit-image-preview');
  if (imageInput && imagePreview) {
    imageInput.addEventListener('change', function() {
      imagePreview.innerHTML = '';
      const file = imageInput.files && imageInput.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const img = document.createElement('img');
          img.src = e.target.result;
          img.style.maxWidth = '100%';
          img.style.maxHeight = '200px';
          imagePreview.appendChild(img);
        };
        reader.readAsDataURL(file);
      }
    });
  }
  // PDF preview
  const fileInput = document.getElementById('edit-file');
  const filePreview = document.getElementById('edit-file-preview');
  if (fileInput && filePreview) {
    fileInput.addEventListener('change', function() {
      filePreview.innerHTML = '';
      const file = fileInput.files && fileInput.files[0];
      if (file && file.type === 'application/pdf') {
        const reader = new FileReader();
        reader.onload = function(e) {
          const embed = document.createElement('embed');
          embed.src = e.target.result;
          embed.type = 'application/pdf';
          embed.width = '100%';
          embed.height = '300px';
          filePreview.appendChild(embed);
        };
        reader.readAsDataURL(file);
      } else if (file) {
        filePreview.textContent = 'Only PDF preview is supported.';
      }
    });
  }
}

function setupAddNotePreview() {
  // Image preview for add note
  const imageInput = document.getElementById('image');
  const imagePreview = document.getElementById('add-image-preview');
  if (imageInput && imagePreview) {
    imageInput.addEventListener('change', function() {
      imagePreview.innerHTML = '';
      const file = imageInput.files && imageInput.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const img = document.createElement('img');
          img.src = e.target.result;
          img.style.maxWidth = '100%';
          img.style.maxHeight = '200px';
          imagePreview.appendChild(img);
        };
        reader.readAsDataURL(file);
      }
    });
  }
  // PDF preview for add note
  const fileInput = document.getElementById('file');
  const filePreview = document.getElementById('add-file-preview');
  if (fileInput && filePreview) {
    fileInput.addEventListener('change', function() {
      filePreview.innerHTML = '';
      const file = fileInput.files && fileInput.files[0];
      if (file && file.type === 'application/pdf') {
        const reader = new FileReader();
        reader.onload = function(e) {
          const embed = document.createElement('embed');
          embed.src = e.target.result;
          embed.type = 'application/pdf';
          embed.width = '100%';
          embed.height = '300px';
          filePreview.appendChild(embed);
        };
        reader.readAsDataURL(file);
      } else if (file) {
        filePreview.textContent = 'Only PDF preview is supported.';
      }
    });
  }
}

function setupNoteEditForm() {
  const editNoteForm = document.getElementById('edit-note-form');
  if (editNoteForm) {
    setupEditNotePreview();
    editNoteForm.onsubmit = function(e) {
      e.preventDefault();
      const formData = new FormData(editNoteForm);
      const noteId = document.getElementById('edit-note-id').value;
      
      console.log('DEBUG: Submitting edit form for note ID:', noteId);
      
      fetch(`/partial/note/${noteId}/edit`, {
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
          // Close modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('editNoteModal'));
          modal.hide();
          // Reload note list
          loadPage('note');
        } else {
          alert(data.message || 'Error updating note.');
        }
      })
      .catch(error => {
        console.error('Error updating note:', error);
        alert('Error updating note');
      });
    };
  }
}

function setupNoteForms() {
  // Add Note Modal
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
          setupNoteForms(); // re-bind modal events for new Edit buttons
        } else {
          alert(data.message || 'Error adding note.');
        }
      });
    };
  }
  
  // Edit Note Modal
  const editNoteModal = document.getElementById('editNoteModal');
  if (editNoteModal) {
    editNoteModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (button) {
        populateEditNoteModal(button);
      }
    });
    
    editNoteModal.addEventListener('hidden.bs.modal', function () {
      // Reset form when modal is closed
      const editForm = document.getElementById('edit-note-form');
      if (editForm) {
        editForm.reset();
      }
    });
  }
  
  // Setup edit note form
  setupNoteEditForm();
  setupAddNotePreview();
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

// Make setupAddLessonModal globally available
window.setupAddLessonModal = function() {
  console.log('setupAddLessonModal called'); // Debug log
  
  // Color selection functionality
  const colorOptions = document.querySelectorAll('.color-option');
  const previewCardHeader = document.getElementById('previewCardHeader');
  const colorInput = document.getElementById('selectedColor');

  // Color definitions
  const colors = {
    1: { primary: '#007bff', secondary: '#0056b3' },
    2: { primary: '#28a745', secondary: '#1e7e34' },
    3: { primary: '#dc3545', secondary: '#c82333' },
    4: { primary: '#ffc107', secondary: '#e0a800' },
    5: { primary: '#6f42c1', secondary: '#5a2d91' },
    6: { primary: '#fd7e14', secondary: '#e8690b' }
  };

  // Reset color selection and preview
  colorOptions.forEach(opt => opt.classList.remove('active'));
  if (colorOptions[0]) colorOptions[0].classList.add('active');
  if (previewCardHeader) {
    previewCardHeader.style.background = 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)';
  }
  if (colorInput) colorInput.value = '1';

  // Remove old event listeners and add new ones
  colorOptions.forEach(option => {
    option.onclick = function() {
      colorOptions.forEach(opt => opt.classList.remove('active'));
      this.classList.add('active');
      const colorId = this.getAttribute('data-color');
      const color = colors[colorId];
      if (previewCardHeader && color) {
        previewCardHeader.style.background = `linear-gradient(135deg, ${color.primary} 0%, ${color.secondary} 100%)`;
      }
      if (colorInput) colorInput.value = colorId;
    };
  });

  // Live preview updates
  const titleInput = document.getElementById('title');
  const descriptionInput = document.getElementById('description');
  const authorInput = document.getElementById('author_name');
  const statusSelect = document.getElementById('status');

  const previewTitle = document.getElementById('previewTitle');
  const previewDescription = document.getElementById('previewDescription');
  const previewAuthor = document.getElementById('previewAuthor');
  const previewStatus = document.getElementById('previewStatus');

  if (titleInput && previewTitle) {
    titleInput.oninput = function() {
      previewTitle.textContent = this.value || 'Your Lesson Title';
    };
  }
  if (descriptionInput && previewDescription) {
    descriptionInput.oninput = function() {
      previewDescription.textContent = this.value || 'Your lesson description will appear here...';
    };
  }
  if (authorInput && previewAuthor) {
    authorInput.oninput = function() {
      previewAuthor.textContent = this.value || 'Unknown Author';
    };
  }
  if (statusSelect && previewStatus) {
    statusSelect.onchange = function() {
      previewStatus.textContent = this.value;
    };
  }

  // Reset preview on form reset
  const form = document.getElementById('add-lesson-form');
  if (form) {
    form.onreset = function() {
      setTimeout(() => {
        if (previewTitle) previewTitle.textContent = 'Your Lesson Title';
        if (previewDescription) previewDescription.textContent = 'Your lesson description will appear here...';
        if (previewAuthor) previewAuthor.textContent = 'Unknown Author';
        if (previewStatus) previewStatus.textContent = 'Not Started';
        colorOptions.forEach(opt => opt.classList.remove('active'));
        if (colorOptions[0]) colorOptions[0].classList.add('active');
        if (previewCardHeader) previewCardHeader.style.background = 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)';
        if (colorInput) colorInput.value = '1';
      }, 10);
    };
  }

  // Form validation (unchanged)
  if (form) {
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    });
    // Real-time validation
    if (titleInput) {
      titleInput.addEventListener('input', function() {
        if (this.value.trim() === '') {
          this.classList.remove('is-valid');
          this.classList.add('is-invalid');
        } else {
          this.classList.remove('is-invalid');
          this.classList.add('is-valid');
        }
      });
    }
  }
}

// Global function to toggle advanced search panel
window.toggleAdvancedSearch = function() {
  const panel = document.getElementById('advancedSearchPanel');
  const toggleBtn = document.getElementById('advancedSearchToggle');
  
  if (panel && toggleBtn) {
    const isVisible = panel.style.display !== 'none';
    panel.style.display = isVisible ? 'none' : 'block';
    
    if (isVisible) {
      toggleBtn.classList.remove('btn-primary');
      toggleBtn.classList.add('btn-outline-secondary');
    } else {
      toggleBtn.classList.remove('btn-outline-secondary');
      toggleBtn.classList.add('btn-primary');
    }
  }
}

function setupLessonSearchAndFilter() {
  console.log('setupLessonSearchAndFilter called');
  
  // Add a small delay to ensure DOM is ready
  setTimeout(() => {
    const searchInput = document.getElementById('lessonSearch');
    const filterSelect = document.getElementById('lessonFilter');
    const clearSearchBtn = document.getElementById('clearSearch');
    const searchContainer = document.querySelector('.search-container');
    
    if (!searchInput && !filterSelect) {
      console.log('Not on lessons page - returning early');
      return; // Not on lessons page
    }
    
    console.log('Setting up lesson search and filter...');
    
    // Debounce function
    let debounceTimer;
    function debounceFilter(func, delay) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(func, delay);
    }
    
    function showLoading() {
      if (searchContainer) {
        searchContainer.classList.add('searching');
      }
    }
    
    function hideLoading() {
      if (searchContainer) {
        searchContainer.classList.remove('searching');
      }
    }
    
    function updateClearButton() {
      if (clearSearchBtn) {
        const hasValue = searchInput.value.trim() !== '' || filterSelect.value !== '';
        clearSearchBtn.style.display = hasValue ? 'block' : 'none';
      }
    }
    
    function getSearchOptions() {
      return {
        searchTitle: document.getElementById('searchTitle')?.checked ?? true,
        searchDescription: document.getElementById('searchDescription')?.checked ?? true,
        searchTags: document.getElementById('searchTags')?.checked ?? false,
        searchAuthor: document.getElementById('searchAuthor')?.checked ?? false,
        sortBy: document.getElementById('sortBy')?.value ?? 'title',
        sortOrder: document.getElementById('sortOrder')?.value ?? 'asc'
      };
    }
    
    function filterLessons() {
      const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
      const filterValue = filterSelect ? filterSelect.value : '';
      const searchOptions = getSearchOptions();
      const lessonCards = document.querySelectorAll('.lesson-card');
      
      showLoading();
      
      // Use setTimeout to show loading briefly
      setTimeout(() => {
        lessonCards.forEach((card, index) => {
          const titleElement = card.querySelector('.lesson-title');
          const descriptionElement = card.querySelector('.lesson-description');
          const statusElement = card.querySelector('.status-badge');
          const authorElement = card.querySelector('.author-name');
          const tagsContainer = card.querySelector('.tags-container');
          
          if (!titleElement || !descriptionElement || !statusElement) {
            return;
          }
          
          const title = titleElement.textContent.toLowerCase();
          const description = descriptionElement.textContent.toLowerCase();
          const status = statusElement.textContent;
          const author = authorElement ? authorElement.textContent.toLowerCase() : '';
          const tags = tagsContainer ? Array.from(tagsContainer.querySelectorAll('.tag-badge')).map(tag => tag.textContent.toLowerCase()) : [];
          
          // Advanced search logic
          let matchesSearch = !searchTerm;
          if (searchTerm) {
            matchesSearch = false;
            if (searchOptions.searchTitle && title.includes(searchTerm)) matchesSearch = true;
            if (searchOptions.searchDescription && description.includes(searchTerm)) matchesSearch = true;
            if (searchOptions.searchAuthor && author.includes(searchTerm)) matchesSearch = true;
            if (searchOptions.searchTags && tags.some(tag => tag.includes(searchTerm))) matchesSearch = true;
          }
          
          const matchesFilter = !filterValue || status === filterValue;
          
          const cardContainer = card.closest('.lesson-card-wrapper');
          if (cardContainer) {
            if (matchesSearch && matchesFilter) {
              cardContainer.classList.remove('hidden');
              cardContainer.classList.add('visible');
            } else {
              cardContainer.classList.add('hidden');
              cardContainer.classList.remove('visible');
            }
          }
        });
        
        // Sort cards if needed
        if (searchOptions.sortBy !== 'title' || searchOptions.sortOrder !== 'asc') {
          sortLessonCards(searchOptions.sortBy, searchOptions.sortOrder);
        }
        
        // Show/hide "no results" message
        const visibleCards = document.querySelectorAll('.lesson-card-wrapper.visible');
        const hasVisibleCards = visibleCards.length > 0;
        
        let noResultsDiv = document.getElementById('no-results-message');
        if (!hasVisibleCards) {
          if (!noResultsDiv) {
            noResultsDiv = document.createElement('div');
            noResultsDiv.id = 'no-results-message';
            noResultsDiv.className = 'col-12 text-center py-5';
            noResultsDiv.innerHTML = `
              <div class="text-muted">
                <i class="fas fa-search fa-3x mb-3"></i>
                <h5>No lessons found</h5>
                <p>Try adjusting your search or filter criteria.</p>
                <button class="btn btn-outline-primary" onclick="clearSearchAndFilter()">
                  <i class="fas fa-times me-2"></i>Clear Filters
                </button>
              </div>
            `;
            const container = document.getElementById('lessons-container');
            if (container) {
              container.appendChild(noResultsDiv);
            }
          }
        } else if (noResultsDiv) {
          noResultsDiv.remove();
        }
        
        hideLoading();
        updateClearButton();
      }, 150); // Brief delay to show loading
    }
    
    function sortLessonCards(sortBy, sortOrder) {
      const container = document.getElementById('lessons-container');
      const cards = Array.from(container.querySelectorAll('.lesson-card-wrapper.visible'));
      
      cards.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
          case 'title':
            aValue = a.querySelector('.lesson-title')?.textContent || '';
            bValue = b.querySelector('.lesson-title')?.textContent || '';
            break;
          case 'status':
            aValue = a.querySelector('.status-badge')?.textContent || '';
            bValue = b.querySelector('.status-badge')?.textContent || '';
            break;
          case 'created':
          case 'updated':
            // For now, use title as fallback since we don't have date elements
            aValue = a.querySelector('.lesson-title')?.textContent || '';
            bValue = b.querySelector('.lesson-title')?.textContent || '';
            break;
          default:
            aValue = a.querySelector('.lesson-title')?.textContent || '';
            bValue = b.querySelector('.lesson-title')?.textContent || '';
        }
        
        if (sortOrder === 'desc') {
          return bValue.localeCompare(aValue);
        } else {
          return aValue.localeCompare(bValue);
        }
      });
      
      // Re-append cards in sorted order
      cards.forEach(card => container.appendChild(card));
    }
    
    // Add event listeners
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        debounceFilter(filterLessons, 300);
      });
      searchInput.addEventListener('keyup', updateClearButton);
    }
    
    if (filterSelect) {
      filterSelect.addEventListener('change', () => {
        filterLessons();
        updateClearButton();
      });
    }
    
    // Advanced search option listeners
    const advancedOptions = ['searchTitle', 'searchDescription', 'searchTags', 'searchAuthor', 'sortBy', 'sortOrder'];
    advancedOptions.forEach(optionId => {
      const element = document.getElementById(optionId);
      if (element) {
        element.addEventListener('change', filterLessons);
      }
    });
    
    // Initial filter
    filterLessons();
    updateClearButton();
  }, 100); // Small delay to ensure DOM is ready
}

// Global function to clear search and filter
window.clearSearchAndFilter = function() {
  const searchInput = document.getElementById('lessonSearch');
  const filterSelect = document.getElementById('lessonFilter');
  const clearSearchBtn = document.getElementById('clearSearch');
  
  if (searchInput) {
    searchInput.value = '';
  }
  if (filterSelect) {
    filterSelect.value = '';
  }
  
  // Reset advanced search options
  const searchTitle = document.getElementById('searchTitle');
  const searchDescription = document.getElementById('searchDescription');
  const searchTags = document.getElementById('searchTags');
  const searchAuthor = document.getElementById('searchAuthor');
  const sortBy = document.getElementById('sortBy');
  const sortOrder = document.getElementById('sortOrder');
  
  if (searchTitle) searchTitle.checked = true;
  if (searchDescription) searchDescription.checked = true;
  if (searchTags) searchTags.checked = false;
  if (searchAuthor) searchAuthor.checked = false;
  if (sortBy) sortBy.value = 'title';
  if (sortOrder) sortOrder.value = 'asc';
  
  // Re-show all cards
  const lessonCards = document.querySelectorAll('.lesson-card-wrapper');
  lessonCards.forEach(card => {
    card.classList.remove('hidden');
    card.classList.add('visible');
  });
  
  // Remove no results message
  const noResultsDiv = document.getElementById('no-results-message');
  if (noResultsDiv) {
    noResultsDiv.remove();
  }
  
  // Hide clear button
  if (clearSearchBtn) {
    clearSearchBtn.style.display = 'none';
  }
  
  // Focus back to search input
  if (searchInput) {
    searchInput.focus();
  }
}

// Global color selection function
window.selectColor = function(element, colorId) {
  console.log('selectColor called with colorId:', colorId);
  
  // Remove active class from all color options
  const colorOptions = document.querySelectorAll('.color-option');
  colorOptions.forEach(opt => opt.classList.remove('active'));
  
  // Add active class to clicked element
  element.classList.add('active');
  
  // Update preview card header
  const previewCardHeader = document.getElementById('previewCardHeader');
  const colorInput = document.getElementById('selectedColor');
  
  const colors = {
    1: { primary: '#007bff', secondary: '#0056b3' },
    2: { primary: '#28a745', secondary: '#1e7e34' },
    3: { primary: '#dc3545', secondary: '#c82333' },
    4: { primary: '#ffc107', secondary: '#e0a800' },
    5: { primary: '#6f42c1', secondary: '#5a2d91' },
    6: { primary: '#fd7e14', secondary: '#e8690b' }
  };
  
  const color = colors[colorId];
  if (previewCardHeader && color) {
    previewCardHeader.style.background = `linear-gradient(135deg, ${color.primary} 0%, ${color.secondary} 100%)`;
  }
  if (colorInput) colorInput.value = colorId;
}

// Global favorite toggle function
window.toggleFavorite = function(lessonId, btn) {
  fetch(`/partial/class/${lessonId}/favorite`, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      const icon = btn.querySelector('i');
      if (data.is_favorite) {
        icon.classList.add('text-warning', 'favorite-active');
        icon.classList.remove('text-secondary');
      } else {
        icon.classList.remove('text-warning', 'favorite-active');
        icon.classList.add('text-secondary');
      }
      // Reload lessons to re-sort
      loadPage('class');
    }
  });
}