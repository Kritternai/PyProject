# Note System UI Restyle - Progress Report

**Date Started:** October 12, 2025  
**Branch:** dev-web/refactor-note#4  
**Status:** 🔄 In Progress (Phase 1)

---

## ✅ Completed

### Phase 1: Global Note Styles (Partial)

#### 1. Header Borders ✅
**File Modified:** `app/static/css/note_style/note_shared.css`

**Changes:**
```css
.note-header {
  border-top: 25px solid var(--note-primary);
  border-bottom: 25px solid var(--note-primary);
}
```

**Result:** ทุกหน้า Note จะมี header borders สีน้ำเงิน 25px บนและล่าง

---

#### 2. Save Status Indicator ✅
**File Modified:** `app/static/css/note_style/note_shared.css`

**New CSS Classes:**
```css
.save-status          /* Base style */
.save-status.unsaved  /* Warning color (yellow) */
.save-status.saved    /* Success color (green) */
.save-status.saving   /* Info color (blue) */
```

**Usage Example:**
```html
<!-- Unsaved -->
<div class="save-status unsaved">
  <i class="bi bi-exclamation-circle"></i>
  <span>Unsaved changes</span>
</div>

<!-- Saved -->
<div class="save-status saved">
  <i class="bi bi-check-circle"></i>
  <span>All changes saved</span>
</div>

<!-- Saving -->
<div class="save-status saving">
  <i class="bi bi-arrow-repeat"></i>
  <span>Saving...</span>
</div>
```

---

#### 3. Rounded Buttons (25px) ✅
**File Modified:** `app/static/css/note_style/note_shared.css`

**New CSS Class:**
```css
.btn-rounded-25 {
  border-radius: 25px !important;
}
```

**Usage:** เพิ่ม class `btn-rounded-25` ให้กับปุ่ม Edit/Delete ใน note cards

---

## 🔄 In Progress

### Phase 1: Global Note Styles (Remaining)

#### Tasks Left:
- [ ] Consistent input styles (ต้องทำต่อ)
- [ ] Consistent textarea styles (ต้องทำต่อ)
- [ ] Implement save status indicator ใน Add/Edit pages (ต้องทำต่อ)

---

## 📋 Pending (Not Started)

### Phase 2: Note List Page
- [ ] Inline search + filter layout
- [ ] Backend statistics (Python)
- [ ] Card image/default background
- [ ] Rounded buttons on cards
- [ ] Date & buttons same line

### Phase 3: Add Note Page
- [ ] Layout adjustments
- [ ] Remove buttons from header
- [ ] File upload feature
- [ ] PDF preview

### Phase 4: Edit Note Page
- [ ] Left panel styling
- [ ] Right panel width
- [ ] File upload feature
- [ ] PDF preview

### Phase 5: Status & Tags Section
- [ ] Add status dropdown
- [ ] Add tags input
- [ ] Position below title

---

## 🎯 Next Steps

### Immediate (Continue Phase 1):

1. **Apply rounded buttons to existing cards**
   ```html
   <!-- In note_fragment.html, update buttons: -->
   <button class="ng-btn-outline-primary ng-btn-sm btn-rounded-25">
     <i class="bi bi-pencil"></i>Edit
   </button>
   <button class="ng-btn-outline-danger ng-btn-sm btn-rounded-25">
     <i class="bi bi-trash"></i>Delete
   </button>
   ```

2. **Add save status to Add Note page**
   ```html
   <!-- In note_add_fragment.html, add before closing </div>: -->
   <div class="save-status unsaved" id="addSaveStatus">
     <i class="bi bi-exclamation-circle"></i>
     <span>Unsaved changes</span>
   </div>
   ```

3. **Add save status to Edit Note page**
   ```html
   <!-- In note_editor_fragment.html, add: -->
   <div class="save-status unsaved" id="editorSaveStatus">
     <i class="bi bi-exclamation-circle"></i>
     <span>Unsaved changes</span>
   </div>
   ```

4. **Update JavaScript to change save status**
   ```javascript
   // In note_add.js:
   function updateSaveStatus(status) {
     const statusEl = document.getElementById('addSaveStatus');
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
   }
   
   // Call when saving:
   updateSaveStatus('saving');
   // After save success:
   updateSaveStatus('saved');
   // On content change:
   updateSaveStatus('unsaved');
   ```

---

### Short-term (Start Phase 2):

1. **Refactor note_fragment.html**
   - Inline search + filter layout
   - Apply rounded buttons to cards

2. **Update note_web_routes.py**
   - Move stats calculation to Python
   - Pass stats to template

3. **Update note cards**
   - Show note image or default background
   - Align date & buttons on same line

---

## 📊 Progress Summary

| Phase | Status | Progress |
|-------|--------|----------|
| **Phase 1: Global Styles** | 🔄 In Progress | 50% (3/6 tasks) |
| **Phase 2: Note List** | ⏳ Pending | 0% (0/5 tasks) |
| **Phase 3: Add Note** | ⏳ Pending | 0% (0/4 tasks) |
| **Phase 4: Edit Note** | ⏳ Pending | 0% (0/4 tasks) |
| **Phase 5: Status & Tags** | ⏳ Pending | 0% (0/2 tasks) |
| **Overall** | 🔄 In Progress | **15%** (3/21 tasks) |

---

## 🔧 Files Modified So Far

1. ✅ `app/static/css/note_style/note_shared.css`
   - Added header borders
   - Added save status styles
   - Added rounded button class

---

## 📝 Implementation Notes

### Design Decisions Made:
- Header borders: 25px สี primary (น้ำเงิน) เพื่อเด่นชัด
- Save status: pill-shaped badges พร้อม icon + text
- Rounded buttons: 25px border-radius สำหรับ modern look

### Technical Considerations:
- ใช้ CSS variables ที่มีอยู่แล้วใน design system
- Save status transitions smooth (0.2s ease)
- Rounded buttons ใช้ !important เพื่อ override Bootstrap

---

## ⚠️ Important Notes for Continuation

**งานนี้ใหญ่มาก** - ประมาณ 23-29 ชั่วโมง แบ่งเป็น 6 phases

**แนะนำ:**
1. ทำทีละ phase
2. Test หลังแต่ละ phase
3. Commit เป็นระยะ
4. อัพเดทเอกสารนี้ทุกครั้งที่ทำเสร็จ

**ใช้เวลาแล้ว:** ~2 ชั่วโมง (Planning + Phase 1 partial)
**เหลือโดยประมาณ:** ~21-27 ชั่วโมง

---

## 🎯 Success Criteria (Phase 1)

**Completed:**
- ✅ Header มี borders 25px (สีน้ำเงิน)
- ✅ CSS สำหรับ save status indicator
- ✅ CSS สำหรับ rounded buttons 25px

**Remaining:**
- ⏳ Apply rounded buttons ใน HTML
- ⏳ Implement save status ใน Add Note
- ⏳ Implement save status ใน Edit Note
- ⏳ Consistent input/textarea styles

---

**Created:** October 12, 2025  
**Last Updated:** October 12, 2025  
**Next Update:** After Phase 1 completion

