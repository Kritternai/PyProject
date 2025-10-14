/**
 * Note List Page JavaScript  
 * Search and filter functions for note list page
 */

// Initialize note list page
window.initializeNoteList = function() {
  console.log('Initializing note list page...');
  
  setupNoteSearch();
  setupNoteFilterChips();
  
  console.log('Note list initialized');
};

// Setup search functionality
function setupNoteSearch() {
  const searchInput = document.getElementById('noteSearch');
  
  if (!searchInput) {
    console.warn('Search input not found');
    return;
  }
  
  console.log('Setting up note search...');
  
  searchInput.addEventListener('input', function() {
    const term = this.value.toLowerCase().trim();
    
    console.log('Searching for:', term);
    
    // Get active status filter
    const activeChip = document.querySelector('.chip-group .chip.active');
    const statusFilter = activeChip ? activeChip.getAttribute('data-status') || '' : '';
    
    filterNoteCards(term, statusFilter);
  });
  
  console.log('Search input listener attached');
}

// Setup chip filter buttons
function setupNoteFilterChips() {
  const chips = document.querySelectorAll('.chip-group .chip');
  
  if (chips.length === 0) {
    console.warn('Filter chips not found');
    return;
  }
  
  console.log('Setting up filter chips:', chips.length);
  
  chips.forEach(chip => {
    chip.addEventListener('click', function() {
      // Remove active class from all chips
      chips.forEach(c => c.classList.remove('active'));
      
      // Add active class to clicked chip
      this.classList.add('active');
      
      // Get status filter
      const statusFilter = this.getAttribute('data-status') || '';
      
      console.log('Filter by status:', statusFilter || 'All');
      
      // Get search term
      const searchInput = document.getElementById('noteSearch');
      const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
      
      filterNoteCards(searchTerm, statusFilter);
    });
  });
  
  console.log('Filter chips listeners attached');
}

// Filter note cards based on search term and status
function filterNoteCards(searchTerm, statusFilter) {
  const cards = document.querySelectorAll('#note-list-container .neo-card');
  
  console.log('Filtering notes:', {
    searchTerm: searchTerm,
    statusFilter: statusFilter,
    totalCards: cards.length
  });
  
  let visibleCount = 0;
  
  cards.forEach(card => {
    const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
    const body = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
    const cardStatus = card.getAttribute('data-status') || '';
    
    // Check if card matches search term
    const matchesSearch = !searchTerm || 
                          title.includes(searchTerm) || 
                          body.includes(searchTerm);
    
    // Check if card matches status filter
    const matchesStatus = !statusFilter || statusFilter === cardStatus;
    
    // Show card if matches both filters
    const matches = matchesSearch && matchesStatus;
    
    // Toggle visibility
    const cardContainer = card.parentElement;
    if (cardContainer) {
      cardContainer.style.display = matches ? '' : 'none';
    }
    
    if (matches) visibleCount++;
  });
  
  console.log('Visible notes:', visibleCount, '/', cards.length);
  
  // Show "no results" message if needed
  showNoResultsMessage(visibleCount === 0);
}

// Show/hide "no results" message
function showNoResultsMessage(show) {
  let noResultsMsg = document.getElementById('no-results-message');
  
  if (show) {
    if (!noResultsMsg) {
      // Create message if doesn't exist
      noResultsMsg = document.createElement('div');
      noResultsMsg.id = 'no-results-message';
      noResultsMsg.className = 'col-12 text-center py-5';
      noResultsMsg.innerHTML = `
        <div class="text-muted">
          <i class="bi bi-search display-4 d-block mb-3"></i>
          <h5>No notes found</h5>
          <p>Try adjusting your search or filter</p>
        </div>
      `;
      
      const noteContainer = document.querySelector('#note-list-container .row.g-3');
      if (noteContainer) {
        noteContainer.appendChild(noResultsMsg);
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

// Global function to clear search and filters
window.clearNoteFilters = function() {
  console.log('Clearing all filters...');
  
  // Clear search input
  const searchInput = document.getElementById('noteSearch');
  if (searchInput) {
    searchInput.value = '';
  }
  
  // Reset to "All" chip
  const chips = document.querySelectorAll('.chip-group .chip');
  chips.forEach((chip, index) => {
    if (index === 0) {
      chip.classList.add('active');
    } else {
      chip.classList.remove('active');
    }
  });
  
  // Show all cards
  filterNoteCards('', '');
  
  console.log('Filters cleared');
};

// Global function to filter by status programmatically
window.filterNotesByStatus = function(status) {
  console.log('Filtering by status:', status);
  
  const chips = document.querySelectorAll('.chip-group .chip');
  chips.forEach(chip => {
    const chipStatus = chip.getAttribute('data-status') || '';
    if (chipStatus === status) {
      chip.click();
    }
  });
};

// Global function to search notes programmatically
window.searchNotes = function(term) {
  console.log('Searching for:', term);
  
  const searchInput = document.getElementById('noteSearch');
  if (searchInput) {
    searchInput.value = term;
    searchInput.dispatchEvent(new Event('input'));
  }
};

// Initialize when script loads
console.log('note_list.js loaded - Functions defined:', {
  initializeNoteList: typeof window.initializeNoteList,
  clearNoteFilters: typeof window.clearNoteFilters,
  filterNotesByStatus: typeof window.filterNotesByStatus,
  searchNotes: typeof window.searchNotes
});

// Auto-initialize if page is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', window.initializeNoteList);
} else {
  // DOM is already ready, initialize now
  setTimeout(window.initializeNoteList, 100);
}

