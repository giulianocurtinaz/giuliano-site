// E-mail montado só quando a pessoa pede (robôs de spam não leem)
document.querySelectorAll('.mostrar-email').forEach(function (botao) {
  botao.addEventListener('click', function () {
    var parte = function (v) { return atob(v).split('').reverse().join(''); };
    var email = parte(botao.dataset.u) + '@' + parte(botao.dataset.d);
    var link = document.createElement('a');
    link.href = 'mailto:' + email;
    link.textContent = email;
    link.className = 'email-revelado';
    botao.replaceWith(link);
    link.focus();
  });
});

// Certificados: abre a imagem grande numa janela sobre a página
var visor = document.querySelector('.visor');
if (visor && typeof visor.showModal === 'function') {
  var img = visor.querySelector('img');
  var legenda = visor.querySelector('.visor-legenda');
  document.querySelectorAll('a[data-grande]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      img.src = a.getAttribute('href');
      img.alt = a.dataset.titulo || '';
      legenda.textContent = a.dataset.titulo || '';
      visor.showModal();
    });
  });
  visor.addEventListener('click', function (e) { if (e.target === visor) visor.close(); });
  visor.addEventListener('close', function () { img.removeAttribute('src'); });
}
