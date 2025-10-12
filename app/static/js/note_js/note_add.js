/**
 * Note Add Page JavaScript
 * All functions for the note add/create page
 */

// app/static/js/note_js

// Save status updater
window.updateAddSaveStatus = function(status) {
  const statusEl = document.getElementById('addSaveStatus');
  if (!statusEl) return;
  
  statusEl.className = `save-status ${status}`;
  
  const icons = {
    unsaved: 'exclamation-circle',
    saving: 'arrow-repeat',
    saved: 'check-circle'
  };
  
  const texts = {
    unsaved: 'Unsaved changes',
    saving: 'Saving...',
    saved: 'All changes saved'
  };
  
  statusEl.innerHTML = `
    <i class="bi bi-${icons[status]}"></i>
    <span>${texts[status]}</span>
  `;
};

// Define all functions globally first
window.initializeNoteAdd = function() {
  console.log('Initializing note add page...');
  
  // Setup toolbar state tracking
  const editor = window.getAddEditor();
  if (editor) {
    // Remove old listeners if any
    editor.removeEventListener('mouseup', window.updateToolbarStates);
    editor.removeEventListener('keyup', window.updateToolbarStates);
    editor.removeEventListener('focus', window.updateToolbarStates);
    editor.removeEventListener('input', window.updateToolbarStates);
    
    // Add new listeners
    editor.addEventListener('mouseup', window.updateToolbarStates);
    editor.addEventListener('keyup', window.updateToolbarStates);
    editor.addEventListener('focus', window.updateToolbarStates);
    editor.addEventListener('input', window.updateToolbarStates);
    
    // Add listener for content changes to update save status
    editor.addEventListener('input', () => {
      window.updateAddSaveStatus('unsaved');
    });
    
    console.log('Editor event listeners attached');
  }
  
  // Also track title changes
  const titleInput = document.getElementById('addTitle');
  if (titleInput) {
    titleInput.addEventListener('input', () => {
      window.updateAddSaveStatus('unsaved');
    });
  }

  // Focus on editor when loaded
  setTimeout(() => {
    if (titleInput) {
      titleInput.focus();
      console.log('Title input focused');
    }
  }, 100);

  // Setup Ctrl+S to save (use named function to avoid duplicates)
  if (!window._noteAddKeySaveAttached) {
    document.addEventListener('keydown', window.handleNoteSaveShortcut);
    window._noteAddKeySaveAttached = true;
    console.log('Keyboard shortcut attached');
  }
  
  // Setup file upload handler
  setupAddFileUpload();
};

// File upload handler
window.setupAddFileUpload = function() {
  const fileInput = document.getElementById('addFileInput');
  const previewContainer = document.getElementById('addFilePreviewContainer');
  
  if (!fileInput || !previewContainer) return;
  
  let selectedFiles = [];
  
  fileInput.addEventListener('change', function(e) {
    const files = Array.from(e.target.files || []);
    selectedFiles = selectedFiles.concat(files);
    renderFilePreview();
  });
  
  function renderFilePreview() {
    if (selectedFiles.length === 0) {
      previewContainer.innerHTML = '';
      return;
    }
    
    previewContainer.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
      const fileItem = document.createElement('div');
      fileItem.className = 'file-preview-item';
      
      // Determine file type
      const ext = file.name.split('.').pop().toLowerCase();
      let fileType = 'document';
      let iconClass = 'bi-file-earmark';
      
      if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
        fileType = 'image';
        iconClass = 'bi-file-image';
      } else if (ext === 'pdf') {
        fileType = 'pdf';
        iconClass = 'bi-file-pdf';
      }
      
      fileItem.innerHTML = `
        <div class="d-flex align-items-center flex-grow-1">
          <div class="file-icon ${fileType}">
            <i class="bi ${iconClass}"></i>
          </div>
          <div>
            <div class="fw-semibold">${file.name}</div>
            <div class="small text-muted">${(file.size / 1024).toFixed(1)} KB</div>
          </div>
        </div>
        <button class="btn btn-sm btn-outline-danger btn-rounded-25" onclick="window.removeAddFile(${index})">
          <i class="bi bi-x"></i>
        </button>
      `;
      
      previewContainer.appendChild(fileItem);
      
      // Show PDF preview if PDF file
      if (ext === 'pdf') {
        const reader = new FileReader();
        reader.onload = function(e) {
          const pdfPreview = document.createElement('div');
          pdfPreview.className = 'pdf-preview-container';
          pdfPreview.innerHTML = `
            <div class="mb-2 d-flex justify-content-between align-items-center">
              <strong>PDF Preview:</strong>
              <button class="btn btn-sm btn-outline-secondary btn-rounded-25" onclick="this.parentElement.parentElement.remove()">
                <i class="bi bi-x"></i>Close Preview
              </button>
            </div>
            <iframe src="${e.target.result}"></iframe>
          `;
          previewContainer.appendChild(pdfPreview);
        };
        reader.readAsDataURL(file);
      }
      
      // Show image preview
      if (fileType === 'image') {
        const reader = new FileReader();
        reader.onload = function(e) {
          const imgPreview = document.createElement('div');
          imgPreview.className = 'mt-2 mb-2';
          imgPreview.innerHTML = `<img src="${e.target.result}" class="img-fluid" style="max-height: 200px; border-radius: 12px; box-shadow: var(--note-shadow);" alt="Preview">`;
          fileItem.appendChild(imgPreview);
        };
        reader.readAsDataURL(file);
      }
    });
  }
  
  window.removeAddFile = function(index) {
    selectedFiles.splice(index, 1);
    renderFilePreview();
  };
  
  window.getAddSelectedFiles = function() {
    return selectedFiles;
  };
};

// Named function for keyboard shortcut
window.handleNoteSaveShortcut = function(e) {
  if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
    const addPage = document.getElementById('note-add-page');
    if (addPage) {  // Only trigger if we're on the add page
      e.preventDefault();
      window.saveNewNote();
    }
  }
};

// Helper functions - Define globally for onclick handlers
window.getAddEditor = function() { 
  return document.getElementById('addContent'); 
};

window.getAddEditorStatus = function() {
  return document.getElementById('addStatus');
};

window.execCommand = function(command, value = null) {
  const editor = window.getAddEditor(); 
  if (!editor) return false;
  editor.focus();
  const result = document.execCommand(command, false, value);
  setTimeout(window.updateToolbarStates, 10);
  return result;
};

window.updateToolbarStates = function() {
  const toolbar = document.querySelector('.editor-toolbar'); 
  if (!toolbar) return;
  const commandMap = { 
    bold: "formatText('bold')", 
    italic: "formatText('italic')", 
    underline: "formatText('underline')", 
    strikeThrough: "formatText('strikeThrough')" 
  };
  Object.keys(commandMap).forEach(cmd => {
    try {
      const isActive = document.queryCommandState(cmd);
      const button = toolbar.querySelector(`[onclick="${commandMap[cmd]}"]`);
      if (button) button.classList.toggle('active', isActive);
    } catch(_) {}
  });
};

window.addClickFeedback = function(buttonSelector) {
  const button = document.querySelector(buttonSelector);
  if (button) {
    button.style.transform = 'scale(0.96)';
    button.style.transition = 'transform 0.12s ease';
    setTimeout(() => { button.style.transform = ''; }, 100);
  }
};

// Formatting functions - Define globally for onclick handlers
window.formatText = function(command) { 
  window.addClickFeedback(`[onclick="formatText('${command}')"]`); 
  window.execCommand(command); 
};

window.insertList = function(type) { 
  window.addClickFeedback(`[onclick="insertList('${type}')"]`); 
  window.execCommand(type === 'ul' ? 'insertUnorderedList' : 'insertOrderedList'); 
};

window.alignText = function(alignment) { 
  window.addClickFeedback(`[onclick="alignText('${alignment}')"]`); 
  window.execCommand(alignment); 
};

window.insertImage = function() {
  window.addClickFeedback('[onclick="insertImage()"]');
  const fileInput = document.createElement('input'); 
  fileInput.type = 'file'; 
  fileInput.accept = 'image/*';
  fileInput.onchange = function(){
    const file = fileInput.files?.[0]; 
    if (!file) return;
    const status = document.getElementById('addStatus'); 
    if (status) status.textContent = 'Processing image...';
    
    // Read as base64 for preview
    const reader = new FileReader();
    reader.onload = function(){ 
      window.execCommand('insertHTML', `<img src="${reader.result}" style="max-width:100%;height:auto;border-radius:12px" alt="Image">`); 
      if (status) status.textContent = 'Image inserted'; 
    };
    reader.readAsDataURL(file);
  };
  fileInput.click();
};

window.insertLink = function() {
  window.addClickFeedback('[onclick="insertLink()"]');
  const selection = window.getSelection(); 
  const selectedText = selection.toString();
  let url = prompt('Enter link URL:', 'https://'); 
  if (!url) return;
  if (!/^https?:\/\//.test(url)) url = 'https://' + url;
  if (selectedText) window.execCommand('createLink', url);
  else { 
    const linkText = prompt('Enter link text:', url); 
    if (linkText) window.execCommand('insertHTML', `<a href="${url}" target="_blank">${linkText}</a>`); 
  }
};

window.insertTable = function() {
  window.addClickFeedback('[onclick="insertTable()"]');
  const rows = parseInt(prompt('Number of rows:', '3')) || 3;
  const cols = parseInt(prompt('Number of columns:', '3')) || 3;
  if (rows < 1 || cols < 1 || rows > 20 || cols > 10) { 
    alert('Please enter valid dimensions (1-20 rows, 1-10 columns)'); 
    return; 
  }
  let html = '<table class="table table-bordered" style="width:100%;margin:10px 0"><tbody>';
  for (let r=0;r<rows;r++){ 
    html += '<tr>'; 
    for (let c=0;c<cols;c++){ 
      html += '<td style="padding:10px;min-width:50px">&nbsp;</td>'; 
    } 
    html += '</tr>'; 
  }
  html += '</tbody></table><p>&nbsp;</p>';
  window.execCommand('insertHTML', html);
  setTimeout(()=>{ 
    const table=window.getAddEditor()?.querySelector('table:last-of-type'); 
    const firstCell=table?.querySelector('td'); 
    if(firstCell){ 
      const range=document.createRange(); 
      range.selectNodeContents(firstCell); 
      range.collapse(true); 
      const sel=window.getSelection(); 
      sel.removeAllRanges(); 
      sel.addRange(range);
    } 
  },10);
};

window.undoAction = function() { 
  window.addClickFeedback('[onclick="undoAction()"]'); 
  window.execCommand('undo'); 
};

window.redoAction = function() { 
  window.addClickFeedback('[onclick="redoAction()"]'); 
  window.execCommand('redo'); 
};

// Clear note - Define as global function
window.clearNote = function() {
  if (confirm('Are you sure you want to clear all content?')) {
    // Clear form elements
    const titleInput = document.getElementById('addTitle');
    const contentEditor = document.getElementById('addContent');
    const status = document.getElementById('addStatus');
    
    if (titleInput) titleInput.value = '';
    if (contentEditor) contentEditor.innerHTML = '<em class="text-muted">Start writing your note here...</em>';
    if (status) status.textContent = 'Ready to write';
    
    // Focus on title input after clearing
    setTimeout(() => {
      if (titleInput) titleInput.focus();
    }, 100);
    
    console.log('Note cleared');
  }
};

// Save new note - Define as global function
window.saveNewNote = function() {
  console.log('=== saveNewNote called ===');
  
  // Get form elements (only title and content now)
  const titleInput = document.getElementById('addTitle');
  const contentEditor = document.getElementById('addContent');
  const status = document.getElementById('addStatus');
  
  console.log('Elements found:', {
    titleInput: !!titleInput,
    contentEditor: !!contentEditor,
    status: !!status
  });
  
  const title = titleInput?.value?.trim() || '';
  const content = contentEditor?.innerHTML || '';
  
  console.log('Values:', {
    title: title,
    contentLength: content.length,
    contentPreview: content.substring(0, 50)
  });
  
  // Validation
  if (!title) {
    alert('Please enter a note title');
    if (titleInput) titleInput.focus();
    return;
  }
  
  if (!content || content === '' || content === '<br>' || content === '<em class="text-muted">Start writing your note here...</em>') {
    alert('Please enter note content');
    if (contentEditor) contentEditor.focus();
    return;
  }
  
  if (status) status.textContent = 'Saving...';
  window.updateAddSaveStatus('saving');
  
  // Get status and tags
  const statusSelect = document.getElementById('addNoteStatus');
  const tagsInput = document.getElementById('addNoteTags');
  const status_value = statusSelect?.value || 'pending';
  const tags = tagsInput?.value || '';
  
  // Prepare form data
  const form = new FormData(); 
  form.append('title', title); 
  form.append('content', content);
  form.append('status', status_value);
  if (tags) form.append('tags', tags);
  
  // Append files if any
  const files = window.getAddSelectedFiles ? window.getAddSelectedFiles() : [];
  files.forEach((file, index) => {
    form.append(`files[${index}]`, file);
  });
  
  console.log('FormData prepared:', {
    title: form.get('title'),
    content: form.get('content')?.substring(0, 50)
  });
  
  console.log('Sending POST request to /partial/note/add');
  
  // Send request
  fetch('/partial/note/add', { 
    method: 'POST', 
    body: form, 
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  .then(r => {
    console.log('Response received:', {
      status: r.status,
      statusText: r.statusText,
      ok: r.ok
    });
    return r.json();
  })
  .then(j => { 
    console.log('Response data:', j);
    
    if (j && j.success) { 
      if (status) status.textContent = 'Saved successfully!'; 
      window.updateAddSaveStatus('saved');
      
      // Auto redirect back to note list after successful save
      setTimeout(() => {
        if (typeof loadPage === 'function') {
          console.log('Redirecting to note list via loadPage');
          loadPage('note');
        } else {
          console.log('Redirecting to note list via location');
          window.location.href = '/notes';
        }
      }, 800);
    } else { 
      const errorMsg = j?.message || 'Save failed';
      console.error('Save failed:', errorMsg);
      if (status) status.textContent = errorMsg; 
      window.updateAddSaveStatus('unsaved');
      alert(errorMsg);
    } 
  })
  .catch(err => { 
    console.error('Save error:', err);
    if (status) status.textContent = 'Save error'; 
    window.updateAddSaveStatus('unsaved');
    alert('An error occurred while saving. Please check console for details.');
  });
};

// Initialize when script loads
console.log('note_add.js loaded - Functions defined:', {
  saveNewNote: typeof window.saveNewNote,
  clearNote: typeof window.clearNote,
  formatText: typeof window.formatText,
  insertImage: typeof window.insertImage,
  initializeNoteAdd: typeof window.initializeNoteAdd
});

// Auto-initialize if page is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', window.initializeNoteAdd);
} else {
  // DOM is already ready, initialize now
  setTimeout(window.initializeNoteAdd, 100);
}

