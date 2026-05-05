function playAgain() {
    sessionStorage.removeItem('gameEndData');
    window.location.href = 'http://localhost:5000/Pelihtml.html';
}

function goLogin() {
    sessionStorage.removeItem('gameEndData');
    window.location.href = 'http://localhost:5000/';
}

window.addEventListener('load', function () {
    document.getElementById('play-again').addEventListener('click', playAgain);
    document.getElementById('go-login').addEventListener('click', goLogin);

    const raw = sessionStorage.getItem('gameEnddata');
    const data = raw ? JSON.parse(raw) : null;

    const title = document.getElementById('end-title');
    const subtitle = document.getElementById('end-subtitle');
    const display = document.getElementById('event-display');

    if (!data) {
        title.textContent = 'Ei dataa';
        display.innerHTML = '<p>Dataa ei löydetty.</p>';
        return;
    }

     if (data.reason === 'victory') {
    title.textContent = 'VOITTO!';
    subtitle.textContent = 'Onnittelut';
    display.innerHTML =
      '<p class="system-text">Löysit sopivan planeetan ihmiskunnalle!</p>' +
      '<p>Kerätyt resurssit:</p>' +
      '<ul>' +
        '<li>Vesi: <strong>' + data.resources.Water + '</strong></li>' +
        '<li>Ruoka: <strong>' + data.resources.Food + '</strong></li>' +
        '<li>Teknologia: <strong>' + data.resources.Technology + '</strong></li>' +
      '</ul>';
    return;
  }

  if (data.reason === 'fuel') {
    title.textContent = 'Game Over';
    subtitle.textContent = 'Häviö';
    display.innerHTML =
      '<p>Hävisit, koska <strong>polttoaine loppui</strong>.</p>' +
      '<p>Pelasit <strong>' + data.round + '</strong> kierrosta.</p>';
    return;
  }

  title.textContent = 'PELI OHI';
  display.innerHTML = '<p>Syy: ' + data.reason + '</p>';
});


