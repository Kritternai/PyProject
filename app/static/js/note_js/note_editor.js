/**
 * Note Editor Page JavaScript
 * All functions for the note editor page (split view with list + editor)
 */

// Global variables
window.currentEditingNoteId = null;

// Save status updater
window.updateEditorSaveStatus = function(status) {
  const statusEl = document.getElementById('editorSaveStatus');
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

// Clear editor to create new note
window.clearEditorForNew = function() {
  console.log('Clearing editor for new note...');
  
  const titleInput = document.getElementById('editorTitle');
  const contentEditor = document.getElementById('editorContent');
  const status = document.getElementById('editorStatus');
  
  if (titleInput) titleInput.value = '';
  if (contentEditor) contentEditor.innerHTML = '';
  if (status) status.textContent = 'Ready to create';
  
  // Clear current note ID
  window.currentEditingNoteId = null;
  
  // Remove active highlight from all notes
  document.querySelectorAll('#editorNotesList .note-row').forEach(row => {
    row.classList.remove('active');
  });
  
  // Focus on title input
  if (titleInput) {
    setTimeout(() => titleInput.focus(), 100);
  }
  
  console.log('Editor cleared, ready for new note');
};

// Initialize note editor
window.initializeNoteEditor = function() {
  console.log('Initializing note editor page...');
  
  // Load selected note if specified
  const container = document.getElementById('note-editor-page');
  const selected = container?.getAttribute('data-selected-note-id');
  if (selected && selected !== '') { 
    console.log('Loading selected note:', selected);
    window.loadEditorNote(selected); 
  }

  // Setup toolbar state tracking
  const editor = window.getEditor();
  if (editor) {
    // Remove old listeners
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
      window.updateEditorSaveStatus('unsaved');
    });
    
    console.log('Editor event listeners attached');
  }
  
  // Also track title changes
  const titleInput = document.getElementById('editorTitle');
  if (titleInput) {
    titleInput.addEventListener('input', () => {
      window.updateEditorSaveStatus('unsaved');
    });
  }

  // Search filter - delay to ensure DOM is ready
  setTimeout(() => {
    setupEditorSearch();
  }, 100);

  // Setup Ctrl+S to save
  if (!window._noteEditorKeySaveAttached) {
    document.addEventListener('keydown', window.handleEditorSaveShortcut);
    window._noteEditorKeySaveAttached = true;
    console.log('Keyboard shortcut attached');
  }
  
  // Setup file upload handler
  setupEditorFileUpload();
};

// File upload handler for editor
window.setupEditorFileUpload = function() {
  const fileInput = document.getElementById('editorFileInput');
  const previewContainer = document.getElementById('editorFilePreviewContainer');
  
  if (!fileInput || !previewContainer) return;
  
  let selectedFiles = [];
  
  fileInput.addEventListener('change', function(e) {
    const files = Array.from(e.target.files || []);
    selectedFiles = selectedFiles.concat(files);
    renderEditorFilePreview();
  });
  
  function renderEditorFilePreview() {
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
        <button class="btn btn-sm btn-outline-danger btn-rounded-25" onclick="window.removeEditorFile(${index})">
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
  
  window.removeEditorFile = function(index) {
    selectedFiles.splice(index, 1);
    renderEditorFilePreview();
  };
  
  window.getEditorSelectedFiles = function() {
    return selectedFiles;
  };
};

// Setup editor search functionality
window.setupEditorSearch = function() {
  const search = document.getElementById('editorNoteSearch');
  
  if (!search) {
    console.warn('Editor search input not found');
    return;
  }
  
  console.log('Setting up editor search...');
  
  // Remove old listener if exists
  search.removeEventListener('input', window._editorSearchHandler);
  
  // Create and attach new listener
  window._editorSearchHandler = function() {
    const term = this.value.toLowerCase().trim();
    console.log('Editor searching for:', term);
    window.filterEditorNotes(term);
  };
  
  search.addEventListener('input', window._editorSearchHandler);
  console.log('Editor search filter attached');
}

// Filter editor note list
window.filterEditorNotes = function(searchTerm) {
  const rows = document.querySelectorAll('#editorNotesList .note-row');
  
  console.log('Filtering editor notes:', {
    searchTerm: searchTerm,
    totalRows: rows.length
  });
  
  let visibleCount = 0;
  
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    const matches = !searchTerm || text.includes(searchTerm);
    
    row.style.display = matches ? '' : 'none';
    
    if (matches) visibleCount++;
  });
  
  console.log('Visible notes in editor:', visibleCount, '/', rows.length);
  
  // Show "no results" message if needed
  showEditorNoResults(visibleCount === 0);
}

// Show/hide "no results" message in editor
function showEditorNoResults(show) {
  let noResultsMsg = document.getElementById('editor-no-results');
  
  if (show) {
    if (!noResultsMsg) {
      noResultsMsg = document.createElement('div');
      noResultsMsg.id = 'editor-no-results';
      noResultsMsg.className = 'text-center text-muted py-5';
      noResultsMsg.innerHTML = `
        <i class="bi bi-search display-6 d-block mb-2"></i>
        <p>No matching notes</p>
      `;
      
      const notesList = document.getElementById('editorNotesList');
      if (notesList) {
        notesList.appendChild(noResultsMsg);
      }
    } else {
      noResultsMsg.style.display = '';
    }
  } else {
    if (noResultsMsg) {
      noResultsMsg.style.display = 'none';
    }
  }
}

// Global function to clear editor search
window.clearEditorSearch = function() {
  console.log('Clearing editor search...');
  
  const searchInput = document.getElementById('editorNoteSearch');
  if (searchInput) {
    searchInput.value = '';
    window.filterEditorNotes('');
  }
};

// Named function for keyboard shortcut
window.handleEditorSaveShortcut = function(e) {
  if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
    const editorPage = document.getElementById('note-editor-page');
    if (editorPage) {  // Only trigger if we're on the editor page
      e.preventDefault();
      window.saveEditorNote();
    }
  }
};

// Helper functions
window.getEditor = function() { 
  return document.getElementById('editorContent'); 
};

window.execCommand = function(command, value = null) {
  const editor = window.getEditor(); 
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

// Formatting functions
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
    const status = document.getElementById('editorStatus'); 
    if (status) status.textContent = 'Uploading image...';
    const noteId = window.currentEditingNoteId;
    
    if (!noteId) {
      // No note ID yet, insert base64
      const reader = new FileReader();
      reader.onload = function(){ 
        window.execCommand('insertHTML', `<img src="${reader.result}" style="max-width:100%;height:auto;border-radius:12px" alt="Image">`); 
        if (status) status.textContent = 'Image inserted'; 
      };
      reader.readAsDataURL(file); 
      return;
    }
    
    // Upload image with note
    const formData = new FormData();
    formData.append('image', file);
    formData.append('title', document.getElementById('editorTitle')?.value || '');
    formData.append('content', document.getElementById('editorContent')?.innerHTML || '');
    
    fetch(`/partial/note/${noteId}/edit`, { 
      method:'POST', 
      body: formData, 
      headers:{ 'X-Requested-With':'XMLHttpRequest' } 
    })
      .then(r=>r.json())
      .then(()=> fetch(`/partial/note/${noteId}/data`, { 
        headers:{ 'X-Requested-With':'XMLHttpRequest' } 
      }).then(r=>r.json()))
      .then(data=>{
        if (data?.success && data?.data?.files?.length) {
          const imgs = data.data.files.filter(f=> (f.file_type||'').toLowerCase()==='image');
          const latest = imgs[imgs.length-1];
          if (latest?.file_path) {
            window.execCommand('insertHTML', `<img src="/static/${latest.file_path}" style="max-width:100%;height:auto;border-radius:12px" alt="${latest.file_name||'Image'}">`);
          }
          if (status) status.textContent = 'Image uploaded and inserted';
        } else { 
          if (status) status.textContent = 'Image upload failed'; 
        }
      })
      .catch(()=>{ 
        if (status) status.textContent = 'Image upload error'; 
      });
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
    const table=window.getEditor()?.querySelector('table:last-of-type'); 
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

// Data fetching and saving
window.loadEditorNote = function(noteId){
  console.log('=== loadEditorNote called ===', noteId);
  
  const status = document.getElementById('editorStatus'); 
  if (status) status.textContent = 'Loading...';
  
  console.log('Fetching note data from:', `/partial/note/${noteId}/data`);
  
  fetch(`/partial/note/${noteId}/data`, { 
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(r=>{
      console.log('Response received:', r.status);
      return r.json();
    })
    .then(j=>{
      console.log('Note data:', j);
      
      if (j && j.success && j.data){
        const titleInput = document.getElementById('editorTitle');
        const contentEditor = document.getElementById('editorContent');
        
        if (titleInput) titleInput.value = j.data.title || '';
        if (contentEditor) contentEditor.innerHTML = j.data.content || '';
        
        // Load status and tags if available
        const statusSelect = document.getElementById('editorNoteStatus');
        const tagsInput = document.getElementById('editorNoteTags');
        if (statusSelect && j.data.status) statusSelect.value = j.data.status;
        if (tagsInput && j.data.tags) {
          tagsInput.value = Array.isArray(j.data.tags) ? j.data.tags.join(', ') : j.data.tags;
        }
        
        // Load existing files if available
        if (j.data.files && Array.isArray(j.data.files)) {
          console.log('Loading existing files:', j.data.files);
          window.loadExistingFiles(j.data.files);
        }
        
        if (status) status.textContent = 'Loaded';
        window.currentEditingNoteId = j.data.id;
        window.updateEditorSaveStatus('saved');
        
        // Highlight active note in list
        document.querySelectorAll('#editorNotesList .note-row').forEach(row => {
          row.classList.toggle('active', row.getAttribute('data-note-id') === String(j.data.id));
        });
        
        console.log('Note loaded successfully:', j.data.id);
      } else { 
        console.error('Load failed:', j);
        if (status) status.textContent = 'Load failed'; 
      }
    })
    .catch((err)=>{ 
      console.error('Load error:', err);
      if (status) status.textContent = 'Load error'; 
    });
};

window.refreshEditorNote = function(){ 
  if (window.currentEditingNoteId) window.loadEditorNote(window.currentEditingNoteId); 
};

window.saveEditorNote = function(){
  console.log('=== saveEditorNote called ===');
  
  const titleInput = document.getElementById('editorTitle');
  const contentEditor = document.getElementById('editorContent');
  const status = document.getElementById('editorStatus');
  
  const title = titleInput?.value || '';
  const content = contentEditor?.innerHTML || '';
  const id = window.currentEditingNoteId;
  
  console.log('Saving note:', {
    id: id,
    title: title.substring(0, 30),
    contentLength: content.length
  });
  
  if (!title) {
    alert('Please enter a note title');
    if (titleInput) titleInput.focus();
    return;
  }
  
  if (!content || content === '' || content === '<br>') {
    alert('Please enter note content');
    if (contentEditor) contentEditor.focus();
    return;
  }
  
  // Get status and tags
  const statusSelect = document.getElementById('editorNoteStatus');
  const tagsInput = document.getElementById('editorNoteTags');
  const status_value = statusSelect?.value || 'pending';
  const tags = tagsInput?.value || '';
  
  const form = new FormData(); 
  form.append('title', title); 
  form.append('content', content);
  form.append('status', status_value);
  if (tags) form.append('tags', tags);
  
  // Append files if any
  const files = window.getEditorSelectedFiles ? window.getEditorSelectedFiles() : [];
  files.forEach((file, index) => {
    form.append(`files[${index}]`, file);
  });
  
  if (!id) {
    // Create new note
    console.log('Creating new note...');
    if (status) status.textContent = 'Creating...';
    window.updateEditorSaveStatus('saving');
    
    fetch('/partial/note/add', { 
      method: 'POST', 
      body: form, 
      headers: { 'X-Requested-With':'XMLHttpRequest' }
    })
      .then(r=>r.json())
      .then(j=>{ 
        console.log('Create response:', j);
        if (j && j.success){ 
          if (status) status.textContent = 'Saved'; 
          window.updateEditorSaveStatus('saved');
          if (j.note_id){ 
            window.currentEditingNoteId = j.note_id; 
            console.log('Note created with ID:', j.note_id);
          }
          // Reload page to show new note in list
          setTimeout(() => {
            if (typeof loadPage === 'function') {
              loadPage('note/editor/' + (j.note_id || ''));
            }
          }, 500);
        } else { 
          console.error('Save failed:', j);
          if (status) status.textContent = j.message || 'Save failed'; 
          window.updateEditorSaveStatus('unsaved');
        } 
      })
      .catch((err)=>{ 
        console.error('Save error:', err);
        if (status) status.textContent = 'Save error'; 
        window.updateEditorSaveStatus('unsaved');
      });
  } else {
    // Update existing note
    console.log('Updating note:', id);
    if (status) status.textContent = 'Saving...';
    window.updateEditorSaveStatus('saving');
    
    fetch(`/partial/note/${id}/edit`, { 
      method:'POST', 
      body: form, 
      headers: { 'X-Requested-With':'XMLHttpRequest' }
    })
      .then(r=>r.json())
      .then(j=>{ 
        console.log('Update response:', j);
        if (j && j.success){ 
          if (status) status.textContent = 'Saved'; 
          window.updateEditorSaveStatus('saved');
          console.log('Note updated successfully');
        } else { 
          console.error('Update failed:', j);
          if (status) status.textContent = j.message || 'Save failed'; 
          window.updateEditorSaveStatus('unsaved');
        } 
      })
      .catch((err)=>{ 
        console.error('Update error:', err);
        if (status) status.textContent = 'Save error'; 
        window.updateEditorSaveStatus('unsaved');
      });
  }
};

// Load existing files for editing
window.loadExistingFiles = function(files) {
  console.log('Loading existing files:', files);
  
  const container = document.getElementById('editorFilePreviewContainer');
  if (!container) {
    console.error('File preview container not found');
    return;
  }
  
  // Clear existing previews
  container.innerHTML = '';
  
  files.forEach(file => {
    if (file && file.file_path) {
      const fileElement = createFilePreviewElement(file);
      if (fileElement) {
        container.appendChild(fileElement);
      }
    }
  });
  
  console.log('Existing files loaded:', files.length);
};

// Create file preview element
function createFilePreviewElement(file) {
  const div = document.createElement('div');
  div.className = 'file-preview-item';
  
  // Create file icon based on type
  const icon = document.createElement('div');
  icon.className = `file-icon ${file.file_type || 'document'}`;
  
  // Create file info
  const info = document.createElement('div');
  info.className = 'file-info';
  
  const name = document.createElement('div');
  name.className = 'file-name';
  name.textContent = file.filename || 'Unknown file';
  
  const size = document.createElement('div');
  size.className = 'file-size';
  if (file.size) {
    size.textContent = formatFileSize(file.size);
  }
  
  info.appendChild(name);
  info.appendChild(size);
  
  // Create preview based on file type
  const preview = document.createElement('div');
  preview.className = 'file-preview';
  
  if (file.file_type === 'image') {
    const img = document.createElement('img');
    img.src = `/static/${file.file_path}`;
    img.alt = file.filename;
    img.style.maxWidth = '100px';
    img.style.maxHeight = '100px';
    img.style.objectFit = 'cover';
    preview.appendChild(img);
  } else if (file.file_type === 'pdf') {
    const iframe = document.createElement('iframe');
    iframe.src = `/static/${file.file_path}`;
    iframe.style.width = '100px';
    iframe.style.height = '100px';
    iframe.style.border = '1px solid #ddd';
    preview.appendChild(iframe);
  } else {
    // Generic document icon
    const docIcon = document.createElement('div');
    docIcon.className = 'document-icon';
    docIcon.innerHTML = '📄';
    docIcon.style.fontSize = '24px';
    preview.appendChild(docIcon);
  }
  
  // Create remove button
  const removeBtn = document.createElement('button');
  removeBtn.className = 'btn btn-sm btn-outline-danger remove-file';
  removeBtn.innerHTML = '×';
  removeBtn.title = 'Remove file';
  removeBtn.onclick = () => {
    div.remove();
  };
  
  div.appendChild(icon);
  div.appendChild(info);
  div.appendChild(preview);
  div.appendChild(removeBtn);
  
  return div;
}

// Format file size
function formatFileSize(bytes) {
  if (!bytes) return '';
  
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Initialize when script loads
console.log('note_editor.js loaded - Functions defined:', {
  loadEditorNote: typeof window.loadEditorNote,
  saveEditorNote: typeof window.saveEditorNote,
  formatText: typeof window.formatText,
  insertImage: typeof window.insertImage,
  initializeNoteEditor: typeof window.initializeNoteEditor,
  loadExistingFiles: typeof window.loadExistingFiles
});

// Auto-initialize if page is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', window.initializeNoteEditor);
} else {
  // DOM is already ready, initialize now
  setTimeout(window.initializeNoteEditor, 100);
}

