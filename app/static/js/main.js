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
          setupNoteListFilters(); // ตั้งค่า search + status chips สำหรับหน้าโน้ต
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

function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
  notification.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  // Add to body
  document.body.appendChild(notification);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 5000);
}

function updateLessonNotesSection() {
  // Get current lesson ID from URL
  const pathParts = window.location.pathname.split('/');
  const lessonId = pathParts[pathParts.indexOf('class') + 1];
  
  if (lessonId) {
    // Fetch updated lesson detail
    fetch(`/partial/class/${lessonId}`)
      .then(response => response.text())
      .then(html => {
        // Create a temporary div to parse the HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Find the notes section in the new HTML
        const newNotesSection = tempDiv.querySelector('#content .mt-4');
        if (newNotesSection) {
          // Find existing notes section
          const existingNotesSection = document.querySelector('#content .mt-4');
          if (existingNotesSection) {
            // Replace the existing notes section
            existingNotesSection.innerHTML = newNotesSection.innerHTML;
          } else {
            // Add new notes section
            const contentTab = document.querySelector('#content');
            if (contentTab) {
              contentTab.appendChild(newNotesSection);
            }
          }
        }
      })
      .catch(error => {
        console.error('Error updating lesson notes section:', error);
      });
  }
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
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
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
  const noteTitle = button.getAttribute('data-note-title') || '';
  const noteContent = button.getAttribute('data-note-content') || '';
  const noteTags = button.getAttribute('data-note-tags') || '';
  const noteStatus = button.getAttribute('data-note-status') || 'pending';
  const noteType = button.getAttribute('data-note-type') || 'text';
  const noteIsPublic = (button.getAttribute('data-note-is-public') || '0') === '1';
  const noteExternalLink = button.getAttribute('data-note-external-link') || '';

  const editForm = document.getElementById('edit-note-form');
  editForm.action = `/partial/note/${noteId}/edit`;
  editForm.method = 'post';

  document.getElementById('edit-note-id').value = noteId;
  const titleEl = document.getElementById('edit-title'); if (titleEl) titleEl.value = noteTitle;
  const contentEl = document.getElementById('edit-content'); if (contentEl) contentEl.value = noteContent;
  const tagsEl = document.getElementById('edit-tags'); if (tagsEl) tagsEl.value = noteTags;
  const statusEl = document.getElementById('edit-status'); if (statusEl) statusEl.value = noteStatus;
  const typeEl = document.getElementById('edit-note-type'); if (typeEl) typeEl.value = noteType;
  const publicEl = document.getElementById('edit-is-public'); if (publicEl) publicEl.checked = noteIsPublic;
  const linkEl = document.getElementById('edit-external-link'); if (linkEl) linkEl.value = noteExternalLink;

  // Clear previews (files/images will be previewed only after user selects new ones)
  const imagePreview = document.getElementById('edit-image-preview'); if (imagePreview) imagePreview.innerHTML = '';
  const filePreview = document.getElementById('edit-file-preview'); if (filePreview) filePreview.innerHTML = '';
};

function fetchAndPopulateEditModal(button) {
  const noteId = button.getAttribute('data-note-id');
  fetch(`/partial/note/${noteId}/data`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(json => {
      if (json && json.success && json.data) {
        button.setAttribute('data-note-title', json.data.title || '');
        button.setAttribute('data-note-content', json.data.content || '');
        const tags = Array.isArray(json.data.tags) ? json.data.tags.join(', ') : (json.data.tags || '');
        button.setAttribute('data-note-tags', tags);
        button.setAttribute('data-note-type', (json.data.note_type || 'text'));
        button.setAttribute('data-note-is-public', json.data.is_public ? '1' : '0');
        if (json.data.status !== undefined) button.setAttribute('data-note-status', json.data.status || 'pending');
        if (json.data.external_link !== undefined) button.setAttribute('data-note-external-link', json.data.external_link || '');
      }
      window.populateEditNoteModal(button);
    })
    .catch(() => {
      window.populateEditNoteModal(button);
    });
}

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
          const modal = bootstrap.Modal.getInstance(document.getElementById('editNoteModal'));
          if (modal) modal.hide();
          refreshNoteListPreserveFilters();
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
          const modal = bootstrap.Modal.getInstance(addNoteModal);
          if (modal) modal.hide();
          addNoteForm.reset();
          // Replace only the list container to preserve toolbar
          const temp = document.createElement('div');
          temp.innerHTML = data.html;
          const newList = temp.querySelector('#note-list-container');
          if (newList) {
            const oldList = document.getElementById('note-list-container');
            if (oldList) oldList.outerHTML = newList.outerHTML;
            setupNoteListFilters();
            refreshNoteListPreserveFilters();
          } else {
            // fallback: full replacement
            document.getElementById('main-content').innerHTML = data.html;
          }
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
        fetchAndPopulateEditModal(button);
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

// Initialize search + status chip filters on Note list page
function setupNoteListFilters() {
  const container = document.getElementById('note-list-container');
  if (!container) return;
  const searchInput = container.querySelector('#noteSearch');
  const cards = () => container.querySelectorAll('.neo-card');
  function applyFilter(status) {
    const term = (searchInput?.value || '').toLowerCase();
    cards().forEach(card => {
      const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
      const body = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
      const st = card.getAttribute('data-status') || '';
      const show = (!term || title.includes(term) || body.includes(term)) && (!status || status === st);
      card.parentElement.style.display = show ? '' : 'none';
    });
  }
  if (searchInput) {
    searchInput.addEventListener('input', () => applyFilter(document.querySelector('.chip-group .chip.active')?.getAttribute('data-status') || ''));
  }
  container.querySelectorAll('.chip-group .chip').forEach(btn => {
    btn.addEventListener('click', function() {
      container.querySelectorAll('.chip-group .chip').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      applyFilter(this.getAttribute('data-status') || '');
    });
  });
}

// Refresh only note list fragment and re-apply current search/filter without full page reload
function refreshNoteListPreserveFilters() {
  const container = document.getElementById('note-list-container');
  if (!container) return;
  const term = (container.querySelector('#noteSearch')?.value || '').toLowerCase();
  const activeChip = container.querySelector('.chip-group .chip.active');
  const status = activeChip ? (activeChip.getAttribute('data-status') || '') : '';
  fetch('/partial/note')
    .then(r => r.text())
    .then(html => {
      // Replace list container only
      const temp = document.createElement('div');
      temp.innerHTML = html;
      const newList = temp.querySelector('#note-list-container');
      if (newList) {
        container.outerHTML = newList.outerHTML;
        // re-bind and re-apply filters
        setupNoteListFilters();
        const newContainer = document.getElementById('note-list-container');
        const searchInput = newContainer.querySelector('#noteSearch');
        if (searchInput) searchInput.value = term;
        // set active chip
        if (status !== '') {
          const chip = newContainer.querySelector(`.chip-group .chip[data-status="${status}"]`);
          if (chip) {
            newContainer.querySelectorAll('.chip-group .chip').forEach(b=>b.classList.remove('active'));
            chip.classList.add('active');
          }
        }
        // apply display
        const active = newContainer.querySelector('.chip-group .chip.active');
        const st = active ? active.getAttribute('data-status') || '' : '';
        const cards = newContainer.querySelectorAll('.neo-card');
        cards.forEach(card => {
          const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
          const body = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
          const cst = card.getAttribute('data-status') || '';
          const show = (!term || title.includes(term) || body.includes(term)) && (!st || st===cst);
          card.parentElement.style.display = show ? '' : 'none';
        });
      }
    });
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

// Global updateCharCount function for form validation
window.updateCharCount = function(element, counterId, maxLength) {
  const counter = document.getElementById(counterId);
  if (counter) {
    const currentLength = element.value.length;
    counter.textContent = currentLength;
    
    // Add color feedback
    if (currentLength > maxLength * 0.9) {
      counter.style.color = '#dc3545'; // danger
    } else if (currentLength > maxLength * 0.7) {
      counter.style.color = '#ffc107'; // warning
    } else {
      counter.style.color = '#6c757d'; // muted
    }
  }
};

// Global updatePreview function (placeholder - can be enhanced later)
window.updatePreview = function() {
  // This function can be enhanced to show live preview
  // For now, it's just a placeholder to prevent errors
  console.log('Preview updated');
};

// Global color selection function - UPDATED for single selection
window.selectColor = function(element, colorId) {
  console.log('=== main.js selectColor START ===');
  console.log('selectColor called with colorId:', colorId);
  
  // Prevent default and stop propagation
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  try {
    // Find the actual color div (support both .color-option and .color-option-neo)
    const colorDiv = (element.classList.contains('color-option') || element.classList.contains('color-option-neo'))
      ? element 
      : element.closest('.color-option, .color-option-neo');
      
    if (!colorDiv) {
      console.error('❌ Could not find color element');
      return;
    }
    
    console.log('✓ Found colorDiv:', colorDiv);
    
    // Remove active from ALL color options (both old and neo styles)
    const allColorOptions = document.querySelectorAll('.color-option, .color-option-neo');
    console.log('Total colors found:', allColorOptions.length);
    
    allColorOptions.forEach(function(opt, index) {
      const hadActive = opt.classList.contains('active');
      opt.classList.remove('active');
      console.log(`Color ${index + 1}: had active=${hadActive}, removed`);
    });
    
    // Verify all removed
    const stillActiveCount = document.querySelectorAll('.color-option.active, .color-option-neo.active').length;
    console.log('Active colors after removal:', stillActiveCount);
    
    // Add active class to clicked element ONLY
    colorDiv.classList.add('active');
    console.log('✓ Added active to color', colorId);
    
    // Verify exactly one active
    const finalActiveCount = document.querySelectorAll('.color-option.active, .color-option-neo.active').length;
    console.log('✓ Final active count:', finalActiveCount, '(should be 1)');
    
    if (finalActiveCount !== 1) {
      console.error('⚠️ WARNING: Active count is not 1!');
    }
    
    // Update preview card header (if exists)
    const previewCardHeader = document.getElementById('previewCardHeader');
    const colorInput = document.getElementById('selectedColor');
    
    const colors = {
      1: { primary: '#007bff', secondary: '#0056b3', name: 'Blue' },
      2: { primary: '#28a745', secondary: '#1e7e34', name: 'Green' },
      3: { primary: '#dc3545', secondary: '#c82333', name: 'Red' },
      4: { primary: '#ffc107', secondary: '#e0a800', name: 'Yellow' },
      5: { primary: '#6f42c1', secondary: '#5a2d91', name: 'Purple' },
      6: { primary: '#fd7e14', secondary: '#e8690b', name: 'Orange' }
    };
    
    const color = colors[colorId];
    if (previewCardHeader && color) {
      previewCardHeader.style.background = `linear-gradient(135deg, ${color.primary} 0%, ${color.secondary} 100%)`;
    }
    if (colorInput) {
      colorInput.value = colorId;
      console.log('✓ Hidden input updated:', colorId);
    }
    
    // Update color name display (if exists)
    const colorNameElement = document.getElementById('selected-color-name');
    if (colorNameElement && color) {
      colorNameElement.textContent = color.name;
      console.log('✓ Color name updated:', color.name);
    }
    
    console.log('=== main.js selectColor END ===\n');
    
  } catch (error) {
    console.error('❌ Error in selectColor:', error);
  }
}

// Class Notes System Functions
window.openNoteModal = function() {
    const modal = new bootstrap.Modal(document.getElementById('createNoteModal'));
    modal.show();
}

window.openAnnouncementModal = function() {
    const modal = new bootstrap.Modal(document.getElementById('createAnnouncementModal'));
    modal.show();
}

window.previewNoteImage = function(input) {
    const preview = document.getElementById('noteImagePreview');
    const placeholder = document.getElementById('noteImagePlaceholder');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
            placeholder.classList.add('d-none');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

window.filterNotes = function(status) {
    // Update active filter button
    document.querySelectorAll('.class-notes-section .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Get lesson ID from current URL
    const pathParts = window.location.pathname.split('/');
    const lessonId = pathParts[pathParts.length - 1];
    
    console.log(`🔧 Filtering notes by status: ${status}`);
    
    // Load notes with filter
    fetch(`/class/${lessonId}/notes?status=${status}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('class-notes-grid').innerHTML = html;
            console.log('✅ Notes filtered successfully');
        })
        .catch(error => {
            console.error('❌ Error filtering notes:', error);
        });
}

window.searchNotes = function(query) {
    console.log(`🔧 Searching notes: "${query}"`);
    
    const noteCards = document.querySelectorAll('.note-card-enhanced');
    noteCards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const content = card.querySelector('.card-text').textContent.toLowerCase();
        const searchQuery = query.toLowerCase();
        
        if (title.includes(searchQuery) || content.includes(searchQuery)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

window.sortNotes = function(sortBy) {
    console.log(`🔧 Sorting notes by: ${sortBy}`);
    
    const grid = document.getElementById('class-notes-grid');
    const noteCards = Array.from(grid.querySelectorAll('.note-card-enhanced'));
    
    noteCards.sort((a, b) => {
        switch(sortBy) {
            case 'newest':
                return new Date(b.dataset.createdAt || 0) - new Date(a.dataset.createdAt || 0);
            case 'oldest':
                return new Date(a.dataset.createdAt || 0) - new Date(b.dataset.createdAt || 0);
            case 'title':
                return a.querySelector('.card-title').textContent.localeCompare(b.querySelector('.card-title').textContent);
            default:
                return 0;
        }
    });
    
    // Re-append sorted cards
    noteCards.forEach(card => grid.appendChild(card));
    console.log('✅ Notes sorted successfully');
}

// iPhone-style Notes Functions
window.openNote = function(noteId) {
    console.log(`🔧 Opening note: ${noteId}`);
    currentNoteId = noteId;
    
    // Update active note in list
    document.querySelectorAll('.note-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-note-id="${noteId}"]`).classList.add('active');
    
    // Load note content
    fetch(`/class/{{ lesson.id }}/notes/${noteId}`)
        .then(response => response.json())
        .then(note => {
            document.getElementById('noteTitle').value = note.title;
            document.getElementById('noteContent').innerHTML = note.content;
            document.getElementById('lastSaved').textContent = 'Loaded';
        })
        .catch(error => {
            console.error('❌ Error loading note:', error);
        });
}

window.createNewNote = function() {
    console.log('🔧 Creating new note');
    currentNoteId = null;
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteContent').innerHTML = '';
    document.getElementById('lastSaved').textContent = 'Not saved';
    
    // Remove active state from all notes
    document.querySelectorAll('.note-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Focus on title
    document.getElementById('noteTitle').focus();
}

window.saveNote = function() {
    const title = document.getElementById('noteTitle').value.trim();
    const content = document.getElementById('noteContent').innerHTML;
    
    if (!title) {
        alert('Please enter a note title');
        return;
    }
    
    const lessonId = '{{ lesson.id }}';
    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    formData.append('status', 'pending');
    
    const url = currentNoteId ? 
        `/class/${lessonId}/notes/${currentNoteId}/update` : 
        `/class/${lessonId}/notes/create`;
    
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        console.log('✅ Note saved successfully');
        document.getElementById('lastSaved').textContent = 'Saved';
        loadNotesList();
    })
    .catch(error => {
        console.error('❌ Error saving note:', error);
        alert('Error saving note');
    });
}

window.autoSaveNote = function() {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
        if (currentNoteId) {
            saveNote();
        }
    }, 2000);
}

window.loadNotesList = function() {
    const lessonId = '{{ lesson.id }}';
    console.log('🔧 Loading notes list for lesson:', lessonId);
    
    fetch(`/class/${lessonId}/notes-list`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('notesList').innerHTML = html;
            console.log('✅ Notes list loaded');
            
            // Setup toolbar buttons after notes are loaded
            setTimeout(() => {
                if (typeof window.setupToolbarButtons === 'function') {
                    window.setupToolbarButtons();
                }
            }, 500);
            
            // Also attach functions to window object
            setTimeout(() => {
                attachNoteFunctions();
            }, 1000);
        })
        .catch(error => {
            console.error('❌ Error loading notes list:', error);
        });
}

// Attach note functions to window object
function attachNoteFunctions() {
    console.log('🔧 Attaching note functions to window object');
    
    // Initialize global variables
    window.autoSaveTimer = null;
    
    // Basic formatting functions
    window.formatText = function(command) {
        console.log(`🔧 Formatting text: ${command}`);
        const editor = document.getElementById('noteContent');
        if (editor) {
            editor.focus();
            const success = document.execCommand(command, false, null);
            console.log(`✅ Command ${command} executed: ${success}`);
        }
    };
    
    window.insertList = function(type) {
        console.log(`🔧 Inserting ${type} list`);
        const editor = document.getElementById('noteContent');
        if (editor) {
            editor.focus();
            if (type === 'ul') {
                document.execCommand('insertHTML', false, '<ul><li>List item</li></ul>');
            } else {
                document.execCommand('insertHTML', false, '<ol><li>List item</li></ol>');
            }
        }
    };
    
    window.alignText = function(alignment) {
        console.log(`🔧 Aligning text: ${alignment}`);
        const editor = document.getElementById('noteContent');
        if (editor) {
            editor.focus();
            document.execCommand(alignment, false, null);
        }
    };
    
    window.insertImage = function() {
        console.log('🔧 Inserting image');
        const imageInput = document.getElementById('imageInput');
        if (imageInput) {
            imageInput.click();
        }
    };
    
    window.insertLink = function() {
        console.log('🔧 Inserting link');
        const url = prompt('Enter URL:');
        if (url) {
            const text = window.getSelection().toString() || 'Link text';
            document.execCommand('insertHTML', false, `<a href="${url}" target="_blank">${text}</a>`);
        }
    };
    
    window.insertTable = function() {
        console.log('🔧 Inserting table');
        const tableHTML = `
            <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Cell 1</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Cell 2</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Cell 3</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Cell 4</td>
                </tr>
            </table>
        `;
        document.execCommand('insertHTML', false, tableHTML);
    };
    
    window.undoAction = function() {
        console.log('🔧 Undo action');
        document.execCommand('undo', false, null);
    };
    
    window.redoAction = function() {
        console.log('🔧 Redo action');
        document.execCommand('redo', false, null);
    };
    
    // Auto-save functionality
    window.autoSaveNote = function() {
        if (window.autoSaveTimer) {
            clearTimeout(window.autoSaveTimer);
        }
        window.autoSaveTimer = setTimeout(() => {
            console.log('🔧 Auto-saving note...');
            // Auto-save logic here
        }, 2000);
    };
    
    // Image upload handler
    window.handleImageUpload = function(input) {
        console.log('🔧 Handling image upload');
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                document.execCommand('insertHTML', false, img.outerHTML);
            };
            reader.readAsDataURL(file);
        }
    };
    
    console.log('✅ Note functions attached to window object');
}

// Global function to load class notes
window.loadClassNotes = function() {
    const pathParts = window.location.pathname.split('/');
    const lessonId = pathParts[pathParts.length - 1];
    console.log('🔧 Loading class notes for lesson:', lessonId);
    
    fetch(`/class/${lessonId}/notes`)
        .then(response => response.text())
        .then(html => {
            console.log('✅ Class notes loaded');
            document.getElementById('class-notes-grid').innerHTML = html;
        })
        .catch(error => {
            console.error('❌ Error loading class notes:', error);
        });
}

window.submitNoteForm = function(event) {
    event.preventDefault();
    const form = document.getElementById('createNoteForm');
    const formData = new FormData(form);
    
    console.log('🔧 Submitting note form...');
    
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        console.log('✅ Note created successfully');
        // Close modal first
        const modal = bootstrap.Modal.getInstance(document.getElementById('createNoteModal'));
        modal.hide();
        // Reset form
        form.reset();
        // Reload notes grid
        if (typeof loadClassNotes === 'function') {
            loadClassNotes();
        } else {
            // Fallback: reload the page
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('❌ Error creating note:', error);
        alert('Error creating note. Please try again.');
    });
}

// Global favorite toggle function - REALTIME UPDATE
window.toggleFavorite = function(lessonId, btn) {
  console.log('🌟 Toggle favorite:', lessonId);
  
  fetch(`/partial/class/${lessonId}/favorite`, {
    method: 'POST',
    headers: { 
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/json'
    }
  })
  .then(r => r.json())
  .then(data => {
    console.log('Favorite response:', data);
    if (data.success) {
      // Update button appearance
      if (data.is_favorite) {
        btn.classList.add('active');
        console.log('✅ Added to favorites');
      } else {
        btn.classList.remove('active');
        console.log('✅ Removed from favorites');
      }
      
      // REALTIME UPDATE: Move card to top or reorder
      const lessonCard = document.querySelector(`.lesson-item[data-lesson-id="${lessonId}"]`);
      if (lessonCard) {
        const lessonsGrid = lessonCard.parentElement;
        
        // Update data attribute
        lessonCard.setAttribute('data-is-favorite', data.is_favorite ? 'true' : 'false');
        
        if (data.is_favorite) {
          // Move to top (after any existing favorites)
          const firstNonFavorite = lessonsGrid.querySelector('.lesson-item[data-is-favorite="false"]');
          if (firstNonFavorite) {
            lessonsGrid.insertBefore(lessonCard, firstNonFavorite);
          } else {
            // All are favorites or this is the first, move to beginning
            lessonsGrid.insertBefore(lessonCard, lessonsGrid.firstChild);
          }
          
          // Add animation
          lessonCard.style.animation = 'slideDown 0.5s ease-out';
          setTimeout(() => {
            lessonCard.style.animation = '';
          }, 500);
          
          console.log('📌 Card moved to favorites section (top)');
        } else {
          // Move to after all favorites
          const favorites = lessonsGrid.querySelectorAll('.lesson-item[data-is-favorite="true"]');
          if (favorites.length > 0) {
            const lastFavorite = favorites[favorites.length - 1];
            lessonsGrid.insertBefore(lessonCard, lastFavorite.nextSibling);
          }
          
          console.log('📍 Card moved to regular section');
        }
        
        // Update stats
        updateStatsCounters();
      }
    } else {
      console.error('Failed to toggle favorite:', data.message);
      alert('Failed to toggle favorite: ' + data.message);
    }
  })
  .catch(err => {
    console.error('Error toggling favorite:', err);
    alert('Error toggling favorite');
  });
}

// Helper function to update stats counters
function updateStatsCounters() {
  const allLessons = document.querySelectorAll('.lesson-item');
  const favorites = document.querySelectorAll('.lesson-item[data-is-favorite="true"]');
  
  // Update favorites counter
  const favCounter = document.querySelector('.stat-card .stat-icon.bg-warning-subtle').closest('.stat-card').querySelector('.display-6');
  if (favCounter) {
    favCounter.textContent = favorites.length;
  }
  
  console.log(`📊 Stats updated: ${favorites.length} favorites out of ${allLessons.length} total`);
}

// =============================================================================
// CLASSWORK FUNCTIONS
// =============================================================================

// Classwork modal functions
window.openCreateTaskModal = function() {
    console.log('🔧 Opening create task modal');
    const modal = new bootstrap.Modal(document.getElementById('createTaskModal'));
    modal.show();
};

window.openCreateMaterialModal = function() {
    console.log('🔧 Opening create material modal');
    const modal = new bootstrap.Modal(document.getElementById('createMaterialModal'));
    modal.show();
};


// Classwork submit functions
window.submitCreateTask = function() {
    console.log('🔧 Submitting create task');
    const form = document.getElementById('createTaskForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Get lesson ID from URL
    const pathParts = window.location.pathname.split('/');
    const lessonId = pathParts[pathParts.length - 1];
    data.lesson_id = lessonId;
    
    fetch('/classwork/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('createTaskModal')).hide();
            if (typeof loadClassworkTasks === 'function') {
                loadClassworkTasks();
            }
            if (typeof loadClassworkDashboard === 'function') {
                loadClassworkDashboard();
            }
        } else {
            alert('Error creating task: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating task');
    });
};

window.submitCreateMaterial = function() {
    console.log('🔧 Submitting create material');
    const form = document.getElementById('createMaterialForm');
    const formData = new FormData(form);
    
    // Get lesson ID from URL
    const pathParts = window.location.pathname.split('/');
    const lessonId = pathParts[pathParts.length - 1];
    formData.append('lesson_id', lessonId);
    
    fetch('/classwork/materials', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('createMaterialModal')).hide();
            if (typeof loadClassworkMaterials === 'function') {
                loadClassworkMaterials();
            }
        } else {
            alert('Error creating material: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating material');
    });
};


// Load classwork dashboard
window.loadClassworkDashboard = function() {
    console.log('🔧 Loading classwork dashboard');
    fetch('/classwork/dashboard')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('total-tasks').textContent = data.dashboard.total_tasks;
                document.getElementById('completed-tasks').textContent = data.dashboard.completed_tasks;
                document.getElementById('in-progress-tasks').textContent = data.dashboard.in_progress_tasks;
                document.getElementById('overdue-tasks').textContent = data.dashboard.overdue_tasks;
            }
        })
        .catch(error => console.error('Error loading dashboard:', error));
};

// Load classwork tasks
window.loadClassworkTasks = function() {
    console.log('🔧 Loading classwork tasks');
    const pathParts = window.location.pathname.split('/');
    const lessonId = pathParts[pathParts.length - 1];
    
    fetch(`/classwork/lessons/${lessonId}/tasks`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (typeof renderClassworkTasks === 'function') {
                    renderClassworkTasks(data.tasks);
                }
            }
        })
        .catch(error => console.error('Error loading tasks:', error));
};

// Load classwork materials
window.loadClassworkMaterials = function() {
    console.log('🔧 Loading classwork materials');
    const pathParts = window.location.pathname.split('/');
    const lessonId = pathParts[pathParts.length - 1];
    
    fetch(`/classwork/lessons/${lessonId}/materials`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (typeof renderClassworkMaterials === 'function') {
                    renderClassworkMaterials(data.materials);
                }
            }
        })
        .catch(error => console.error('Error loading materials:', error));
};

// Render classwork tasks
window.renderClassworkTasks = function(tasks) {
    console.log('🔧 Rendering classwork tasks:', tasks);
    const container = document.getElementById('classwork-tasks');
    if (!container) return;
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="text-muted">No tasks yet. Create your first task!</p>';
        return;
    }
    
    container.innerHTML = tasks.map(task => `
        <div class="classwork-task-item mb-3 p-3 border rounded">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1">${task.title}</h6>
                    <p class="text-muted mb-2">${task.description || 'No description'}</p>
                    <div class="d-flex gap-2">
                        <span class="badge bg-${getPriorityColor(task.priority)}">${task.priority}</span>
                        <span class="badge bg-${getStatusColor(task.status)}">${task.status}</span>
                        ${task.subject ? `<span class="badge bg-secondary">${task.subject}</span>` : ''}
                    </div>
                </div>
                <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                        <i class="bi bi-three-dots"></i>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" onclick="editTask('${task.id}')">Edit</a></li>
                        <li><a class="dropdown-item" href="#" onclick="deleteTask('${task.id}')">Delete</a></li>
                    </ul>
                </div>
            </div>
        </div>
    `).join('');
};

// Render classwork materials
window.renderClassworkMaterials = function(materials) {
    console.log('🔧 Rendering classwork materials:', materials);
    const container = document.getElementById('classwork-materials');
    if (!container) return;
    
    if (materials.length === 0) {
        container.innerHTML = '<p class="text-muted">No materials yet. Upload your first material!</p>';
        return;
    }
    
    container.innerHTML = materials.map(material => `
        <div class="classwork-material-item mb-3 p-3 border rounded">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1">${material.title}</h6>
                    <p class="text-muted mb-2">${material.description || 'No description'}</p>
                    <div class="d-flex gap-2">
                        <span class="badge bg-info">${material.file_type || 'File'}</span>
                        ${material.subject ? `<span class="badge bg-secondary">${material.subject}</span>` : ''}
                    </div>
                </div>
                <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                        <i class="bi bi-three-dots"></i>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" onclick="downloadMaterial('${material.id}')">Download</a></li>
                        <li><a class="dropdown-item" href="#" onclick="editMaterial('${material.id}')">Edit</a></li>
                        <li><a class="dropdown-item" href="#" onclick="deleteMaterial('${material.id}')">Delete</a></li>
                    </ul>
                </div>
            </div>
        </div>
    `).join('');
};

// Utility functions
window.getPriorityColor = function(priority) {
    switch(priority) {
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'success';
        default: return 'secondary';
    }
};

window.getStatusColor = function(status) {
    switch(status) {
        case 'done': return 'success';
        case 'in_progress': return 'warning';
        case 'todo': return 'secondary';
        default: return 'secondary';
    }
};

// Action functions
window.editTask = function(taskId) {
    console.log('Edit task:', taskId);
    // TODO: Implement edit task
};

window.deleteTask = function(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        fetch(`/classwork/tasks/${taskId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadClassworkTasks();
                loadClassworkDashboard();
            } else {
                alert('Error deleting task: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting task');
        });
    }
};

window.downloadMaterial = function(materialId) {
    console.log('Download material:', materialId);
    // TODO: Implement download material
};

window.editMaterial = function(materialId) {
    console.log('Edit material:', materialId);
    // TODO: Implement edit material
};

window.deleteMaterial = function(materialId) {
    if (confirm('Are you sure you want to delete this material?')) {
        fetch(`/classwork/materials/${materialId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadClassworkMaterials();
            } else {
                alert('Error deleting material: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting material');
        });
    }
};

// Initialize classwork
window.initClasswork = function(lessonId) {
    console.log('🔧 Initializing classwork for lesson:', lessonId);
    loadClassworkDashboard();
    loadClassworkTasks();
    loadClassworkMaterials();
};

console.log('✅ Classwork functions loaded');