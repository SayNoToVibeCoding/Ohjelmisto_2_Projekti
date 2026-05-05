console.log('playerName in storage:', localStorage.getItem('playerName'));
let currentPlayer = null;
let currentGameState = {
    fuel: 100,
    resources: { Water: 0, Food: 0, Technology: 0 },
    round: 1,
    planetsVisited: []
};

function initGame(playerName) {
    console.log('initGame called with:', playerName);
    currentPlayer = playerName;
    fetch('http://localhost:5000/api/game/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: playerName })
    })

    .then(function(response) { 
        return response.json(); 
    })
    .then(function(data) {
        if (data.status === 'ok') {
            currentGameState.fuel = data.fuel;
            currentGameState.resources = data.resources;
            loadRound();
        } else {
            showError(data.message);
        }
    })
    .catch(function(err) {
        console.error('Error creating game:', err);
        showError('Pelin luominen epäonnistui');
    });
}

function loadRound() {
    fetch('http://localhost:5000/api/game/round', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: currentPlayer })
    })
    .then(function(response) { 
        return response.json(); 
    })
    .then(function(data) {
        if (data.status === 'ok') {
            currentGameState = Object.assign(currentGameState, data);
            updateUI();
            renderPlanets(data.planets);
        } else {
            showError(data.message);
        }
    })
    .catch(function(err) {
        console.error('Error loading round:', err);
        showError('Kierroksen lataaminen epäonnistui');
    });
}

function travelToPlanet(planet) {
    fetch('http://localhost:5000/api/game/travel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: currentPlayer, planet: planet })
    })
    .then(function(response) { 
        return response.json(); 
    })
    .then(function(data) {
        if (data.status === 'ok') {
            currentGameState.fuel = data.fuel;
            currentGameState.resources = data.resources;
            currentGameState.planetsVisited = data.planets_visited;
            triggerRandomEvent();
        } else {
            showError(data.message);
        }
    })
    .catch(function(err) {
        console.error('Error traveling:', err);
        showError('Matka epäonnistui');
    });
}

function triggerRandomEvent() {
    fetch('http://localhost:5000/api/game/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: currentPlayer })
    })
    .then(function(response) { 
        return response.json(); 
    })
    .then(function(data) {
        if (data.status === 'ok') {
            currentGameState.fuel = data.fuel;
            updateUI();
            checkVictory();
        }
    })
    .catch(function(err) {
        console.error('Error triggering event:', err);
    });
}

function checkVictory() {
    fetch('http://localhost:5000/api/game/check-victory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_name: currentPlayer })
    })
    .then(function(response) { 
        return response.json(); 
    })
    .then(function(data) {
        if (data.status === 'ok') {
            if (data.victory) {
                showVictoryModal();
            } else if (data.fuel <= 0) {
                showGameOverModal('Polttoaine loppui!');
            } else {
                setTimeout(function() {
                    loadRound();
                }, 1500);
            }
        }
    })
    .catch(function(err) {
        console.error('Error checking victory:', err);
    });
}

function updateUI() {
    document.getElementById('fuel-bar').style.width = currentGameState.fuel + '%';
    document.getElementById('fuel-value').textContent = currentGameState.fuel + '%';
    document.getElementById('res-water').textContent = currentGameState.resources.Water;
    document.getElementById('res-food').textContent = currentGameState.resources.Food;
    document.getElementById('res-tech').textContent = currentGameState.resources.Technology;
    document.getElementById('res-visited').textContent = currentGameState.planetsVisited.length;
}

function renderPlanets(planets) {
    const planetList = document.getElementById('planet-list');
    planetList.innerHTML = '';
    
    planets.forEach(function(planet) {
        const card = document.createElement('div');
        card.className = 'planet-card';
        card.innerHTML = '<strong>' + planet.name + '</strong><br>' +
                         'Polttoaine: ' + planet.fuel_cost + '%<br>' +
                         'Vesi: +' + planet.rewards.Water + ' ' +
                         'Ruoka: +' + planet.rewards.Food + ' ' +
                         'Teknologia: +' + planet.rewards.Technology;
        card.onclick = function() {
            travelToPlanet(planet);
        };
        planetList.appendChild(card);
    });
}

function showError(message) {
    const display = document.getElementById('event-display');
    display.innerHTML = '<p class="error-text">Virhe: ' + message + '</p>';
}

function showVictoryModal() {
    const modal = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const desc = document.getElementById('modal-desc');
    
    title.textContent = 'VOITTO!';
    desc.textContent = 'Löysit sopivan planeetan ihmiskunnalle! Vesi: ' + currentGameState.resources.Water + 
                       ' Ruoka: ' + currentGameState.resources.Food + 
                       ' Teknologia: ' + currentGameState.resources.Technology;
    modal.classList.remove('hidden');
}

function showGameOverModal(reason) {
    const modal = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const desc = document.getElementById('modal-desc');
    
    title.textContent = 'PELI OHI';
    desc.textContent = reason + ' Kierrokset: ' + currentGameState.round;
    modal.classList.remove('hidden');
}

function closeModal() {
    const modal = document.getElementById('modal-overlay');
    modal.classList.add('hidden');
    location.reload();
}

window.addEventListener('load', function() {
    const playerName = localStorage.getItem('playerName');
    console.log('Page loaded, playerName from storage:', playerName);
    
    if (playerName) {
        console.log('Calling initGame with:', playerName);
        initGame(playerName);
    } else {
        console.log('No player name found, redirecting to login');
        window.location.href = '/';
    }
});