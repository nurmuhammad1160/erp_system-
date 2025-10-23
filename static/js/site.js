// small site JS for nav toggle
document.addEventListener('DOMContentLoaded', function(){
  var btn = document.getElementById('navToggle');
  var nav = document.getElementById('mainNav');
  if(!btn || !nav) return;
  btn.addEventListener('click', function(){
    var isOpen = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', String(isOpen));
  });
});
