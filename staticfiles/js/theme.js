(function(){
  const KEY = 'alhadid:theme';
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const saved = localStorage.getItem(KEY);

  function apply(mode) {
    const root = document.documentElement;
    if (mode === 'dark') root.classList.add('dark'); else root.classList.remove('dark');
    localStorage.setItem(KEY, mode);
    document.querySelectorAll('[data-theme-toggle]').forEach(btn=>{
      btn.textContent = (mode === 'dark') ? 'Light Mode' : 'Dark Mode';
    });
  }

  apply(saved ? saved : (prefersDark ? 'dark' : 'light'));

  document.addEventListener('click', (e)=>{
    const btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    const isDark = document.documentElement.classList.contains('dark');
    apply(isDark ? 'light' : 'dark');
  });
})();
