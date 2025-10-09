// Tiny handler to show spinner state when Google sign-in buttons are clicked
document.addEventListener('DOMContentLoaded', function () {
  function attach(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('click', function () {
      el.classList.add('loading');
      // Let the browser follow the link; spinner indicates action
      // In case of JS-heavy forms, we could disable/submit here.
    });
  }
  attach('google-signin-sidebar');
  attach('google-signin-login');
});
