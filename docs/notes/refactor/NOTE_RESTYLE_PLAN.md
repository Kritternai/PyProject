# Note System UI Restyle - Implementation Plan

**Date:** October 12, 2025  
**Branch:** dev-web/refactor-note#4  
**Status:** 📋 Planning Phase

---

## 🎯 Overview

Comprehensive UI/UX restyle of Note System เพื่อปรับปรุงความสวยงาม ความสอดคล้อง และ User Experience

---

## 📋 Tasks Breakdown

### 1. 🌐 Global Note Styles (All Pages)

#### Header Improvements
- [x] เพิ่ม top border (25px)
- [x] เพิ่ม bottom border (25px)
- [ ] Consistent padding/margin

#### Form Elements
- [ ] ทำให้ inputs มี consistent style
- [ ] ทำให้ textareas มี consistent style
- [ ] Unified focus states
- [ ] Consistent border-radius

#### Editor Bottom Section
- [ ] แสดง save status indicator
  - `unsaved` state (⚠️ icon + text)
  - `saved` state (✓ icon + text)
- [ ] Consistent design ทุกหน้า

#### Status & Tags Section
- [ ] เพิ่ม Status dropdown ใต้ title
- [ ] เพิ่ม Tags input ใต้ title
- [ ] Consistent styling

**Estimated Time:** 3-4 hours

---

### 2. 📝 Note List Page

#### Search & Filter Inline Layout
**Current:**
```
Search box (full width)
Filter chips (separate row)
```

**Target:**
```
[Search box] [Filter: All | Pending | In Progress | Completed]
```

**Changes:**
- [ ] รวม search + filter ใน row เดียว
- [ ] Search box: 60% width
- [ ] Filter chips: 40% width, inline

#### Backend Statistics (Python)
**Current:** คำนวณใน Jinja2 template

**Target:** คำนวณใน Python backend

**Files to modify:**
- `app/routes/note_web_routes.py`
- `app/services.py` (NoteService)

**Stats to calculate:**
- Total notes count
- Completed notes count
- Notes with images count
- Notes with files count

```python
def get_note_statistics(user_id):
    """Calculate and return note statistics"""
    return {
        'total': total_count,
        'completed': completed_count,
        'images': image_count,
        'files': file_count
    }
```

#### Card Note Improvements
- [ ] แสดงรูปของ note เอง
- [ ] ถ้าไม่มีรูป → ใช้ default color background
- [ ] ปุ่ม Edit/Delete: border-radius 25px
- [ ] จัด date และ buttons บน X-axis เดียวกัน

**Before:**
```
[Note Card]
  Title
  Content preview
  Date
  [Edit] [Delete]
```

**After:**
```
[Note Card with Image/Color]
  Title
  Content preview
  Date ..................... [Edit] [Delete]  <- same line
```

**Estimated Time:** 4-5 hours

---

### 3. ➕ Add Note Page

#### Layout Adjustments
- [ ] ปรับ spacing ให้ตรงกับ Edit Note layout
- [ ] Remove buttons จากภายใน header
- [ ] Move action buttons ลงมาใกล้ editor

#### Header Button Styling
- [ ] Back button: ใช้ style เดียวกับ header buttons
- [ ] Consistent with Edit Note page

#### File Upload Features
- [ ] เพิ่ม file upload button
- [ ] Support multiple file types
- [ ] PDF preview feature
  - Embed PDF viewer
  - Thumbnail preview
  - Download option

**New Components:**
```html
<div class="file-upload-section">
  <button class="upload-btn">
    <i class="bi bi-paperclip"></i>
    Attach File
  </button>
  <input type="file" accept=".pdf,.doc,.docx,.jpg,.png">
</div>

<div class="file-preview" id="pdfPreview">
  <!-- PDF embed will appear here -->
</div>
```

**Estimated Time:** 5-6 hours

---

### 4. ✏️ Edit Note Page

#### Header
- [ ] Save button: match Add Note header button style
- [ ] Consistent positioning

#### Left Panel (Note List)
- [ ] Add border-radius 25px
- [ ] Search box: style เหมือน Note List page
- [ ] Improve spacing:
  - Title และ content
  - Content และ date
  - Icon sizing และ alignment

**Current:**
```
[Note Item - rectangle]
  Icon Title
  Content
  Date
```

**Target:**
```
[Note Item - rounded 25px]
  Icon  Title (proper spacing)
        Content (preview)
        Date (with icon)
```

#### Right Panel (Editor)
- [ ] Align editor width evenly along X-axis
- [ ] Title back button: same style as Add Note
- [ ] File upload feature (same as Add Note)
- [ ] PDF preview support (same as Add Note)

#### Split View Balance
- [ ] Left panel: 30% width
- [ ] Right panel: 70% width
- [ ] Responsive breakpoint for mobile

**Estimated Time:** 6-7 hours

---

## 🎨 CSS Changes Required

### New CSS Classes to Add

```css
/* Header with borders */
.note-header-bordered {
  border-top: 25px solid var(--note-primary);
  border-bottom: 25px solid var(--note-primary);
}

/* Consistent inputs */
.note-input-consistent {
  border-radius: 12px;
  padding: 12px 16px;
  border: 1px solid var(--note-border);
  transition: all var(--note-transition);
}

/* Save status indicator */
.save-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.save-status.unsaved {
  color: var(--note-warning);
}

.save-status.saved {
  color: var(--note-success);
}

/* Inline search + filter */
.search-filter-inline {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-filter-inline .search-box {
  flex: 0 0 60%;
}

.search-filter-inline .filter-chips {
  flex: 0 0 38%;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Card with default background */
.note-card-no-image {
  background: linear-gradient(135deg, 
    var(--note-accent1), 
    var(--note-accent2)
  );
  height: 140px;
}

/* Rounded buttons */
.btn-rounded-25 {
  border-radius: 25px !important;
}

/* Same-line layout */
.date-buttons-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* File upload section */
.file-upload-section {
  border: 2px dashed var(--note-border);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all var(--note-transition);
}

.file-upload-section:hover {
  border-color: var(--note-primary);
  background: rgba(0, 59, 142, 0.05);
}

/* PDF preview */
.pdf-preview-container {
  border: 1px solid var(--note-border);
  border-radius: 12px;
  padding: 16px;
  background: white;
}

.pdf-preview-container iframe {
  width: 100%;
  height: 600px;
  border: none;
  border-radius: 8px;
}
```

### CSS Files to Modify
1. `app/static/css/note_style/note_shared.css` - Global styles
2. `app/static/css/note_style/note_list_modals.css` - List page
3. `app/static/css/note_style/note_editor_layout.css` - Editor page

---

## 🔧 Backend Changes Required

### 1. Statistics Calculation (Python)

**File:** `app/routes/note_web_routes.py`

```python
@note_web_bp.route('/partial/note')
def partial_note():
    """Note fragment with backend stats"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        note_service = NoteService()
        notes = note_service.get_user_notes(g.user.id)
        notes = _enrich_notes_with_status_and_files(notes)
        
        # Calculate stats in Python
        stats = {
            'total': len(notes),
            'completed': sum(1 for n in notes if getattr(n, 'status', None) == 'completed'),
            'images': 0,  # TODO: Calculate from files
            'docs': 0     # TODO: Calculate from files
        }
        
        # Calculate file stats
        for note in notes:
            if hasattr(note, 'files') and note.files:
                for file in note.files:
                    if file and hasattr(file, 'file_type'):
                        if file.file_type == 'image':
                            stats['images'] += 1
                        elif file.file_type == 'document':
                            stats['docs'] += 1
        
        return render_template('note_fragment.html', 
                             notes=notes, 
                             stats=stats, 
                             user=g.user)
    except Exception as e:
        return render_template('note_fragment.html', 
                             notes=[], 
                             stats={'total': 0, 'completed': 0, 'images': 0, 'docs': 0}, 
                             user=g.user)
```

### 2. File Upload Handling

**New route:** `/partial/note/<note_id>/upload-file`

```python
@note_web_bp.route('/partial/note/<note_id>/upload-file', methods=['POST'])
def upload_note_file(note_id):
    """Handle file upload for notes"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        # Save file
        saved_path = _save_note_file(note_id, file, g.user.id)
        
        return jsonify({
            'success': True,
            'file_path': saved_path,
            'file_name': file.filename
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

---

## 🧪 Testing Plan

### Visual Testing
- [ ] Note List: inline search/filter ทำงานถูกต้อง
- [ ] Note List: stats แสดงถูกต้อง (Python backend)
- [ ] Note List: cards มี rounded buttons
- [ ] Note List: date และ buttons อยู่บรรทัดเดียว
- [ ] Add Note: layout ตรงกับ Edit Note
- [ ] Add Note: file upload ทำงาน
- [ ] Add Note: PDF preview แสดงถูกต้อง
- [ ] Edit Note: left panel มี border-radius 25px
- [ ] Edit Note: search box style ถูกต้อง
- [ ] Edit Note: file upload และ PDF preview ทำงาน
- [ ] All pages: header มี borders 25px
- [ ] All pages: inputs มี consistent style
- [ ] All pages: save status แสดงถูกต้อง

### Functional Testing
- [ ] Statistics accurate (backend calculation)
- [ ] File upload successful
- [ ] PDF preview loads correctly
- [ ] Search + filter work together
- [ ] Responsive design (mobile/tablet)

### Browser Testing
- [ ] Chrome ✓
- [ ] Firefox ✓
- [ ] Safari ✓
- [ ] Edge ✓

---

## 📅 Implementation Timeline

| Phase | Tasks | Time | Status |
|-------|-------|------|--------|
| **Phase 1** | Global styles + Header borders | 3-4h | 🔄 Pending |
| **Phase 2** | Note List inline search/filter + backend stats | 4-5h | 🔄 Pending |
| **Phase 3** | Card improvements + rounded buttons | 2-3h | 🔄 Pending |
| **Phase 4** | Add Note layout + file upload | 5-6h | 🔄 Pending |
| **Phase 5** | Edit Note panels + file upload | 6-7h | 🔄 Pending |
| **Phase 6** | Testing + Bug fixes | 3-4h | 🔄 Pending |
| **Total** | | **23-29 hours** | |

---

## 🎯 Success Criteria

✅ Search และ filter อยู่ใน inline layout เดียว  
✅ Statistics คำนวณด้วย Python backend  
✅ Cards แสดงรูปของ note หรือ default color  
✅ ปุ่มทั้งหมดมี border-radius 25px  
✅ Date และ buttons อยู่บรรทัดเดียว  
✅ File upload ทำงานทั้ง Add และ Edit Note  
✅ PDF preview แสดงได้ถูกต้อง  
✅ Header มี borders 25px ทุกหน้า  
✅ Inputs มี consistent style  
✅ Save status indicator ทำงาน  
✅ Responsive design ทำงานบน mobile  

---

## 📝 Notes

### Design Decisions
- ใช้ existing design system จาก `note_shared.css`
- Border-radius 25px เพื่อ modern look
- Inline layout ลด vertical space
- Backend stats เพิ่ม performance
- PDF preview ใช้ browser native viewer

### Technical Considerations
- File upload: max size 10MB
- Supported formats: PDF, DOC, DOCX, JPG, PNG, GIF
- PDF preview: iframe embed
- Mobile: stack search/filter vertically
- Save status: auto-update ทุก 3 seconds

---

**Created:** October 12, 2025  
**Last Updated:** October 12, 2025  
**Status:** Ready for implementation

