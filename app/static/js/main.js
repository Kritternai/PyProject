function loadPage(page) {
  fetch('/partial/' + page)
    .then(response => response.text())
    .then(html => {
      document.getElementById('main-content').innerHTML = html;
      if (page === 'dashboard') {
        setupFullCalendar();
      }
    });
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