/**
 * Note Editor Page JavaScript
 * All functions for the note editor page (split view with list + editor)
 */

// Global variables
window.currentEditingNoteId = null;

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
    
    console.log('Editor event listeners attached');
  }

  // Search filter
  setupEditorSearch();

  // Setup Ctrl+S to save
  if (!window._noteEditorKeySaveAttached) {
    document.addEventListener('keydown', window.handleEditorSaveShortcut);
    window._noteEditorKeySaveAttached = true;
    console.log('Keyboard shortcut attached');
  }
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
        
        if (status) status.textContent = 'Loaded';
        window.currentEditingNoteId = j.data.id;
        
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
  
  const form = new FormData(); 
  form.append('title', title); 
  form.append('content', content);
  
  if (!id) {
    // Create new note
    console.log('Creating new note...');
    if (status) status.textContent = 'Creating...';
    
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
        } 
      })
      .catch((err)=>{ 
        console.error('Save error:', err);
        if (status) status.textContent = 'Save error'; 
      });
  } else {
    // Update existing note
    console.log('Updating note:', id);
    if (status) status.textContent = 'Saving...';
    
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
          console.log('Note updated successfully');
        } else { 
          console.error('Update failed:', j);
          if (status) status.textContent = j.message || 'Save failed'; 
        } 
      })
      .catch((err)=>{ 
        console.error('Update error:', err);
        if (status) status.textContent = 'Save error'; 
      });
  }
};

// Initialize when script loads
console.log('note_editor.js loaded - Functions defined:', {
  loadEditorNote: typeof window.loadEditorNote,
  saveEditorNote: typeof window.saveEditorNote,
  formatText: typeof window.formatText,
  insertImage: typeof window.insertImage,
  initializeNoteEditor: typeof window.initializeNoteEditor
});

// Auto-initialize if page is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', window.initializeNoteEditor);
} else {
  // DOM is already ready, initialize now
  setTimeout(window.initializeNoteEditor, 100);
}

