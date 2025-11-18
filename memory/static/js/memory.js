// --- Generador de Números Aleatorios con Semilla (LCG) ---
function LCG(seed) {
    const m = 2147483647;
    const a = 16807;
    const c = 0;
    let z = seed;

    return function() {
        z = (a * z + c) % m;
        return (z - 1) / (m - 1); // Retorna un float entre 0 y 1
    };
}
// Inicializamos el generador (se definirá dentro del DOMContentLoaded usando la variable global gameSeed)
let seededRandom = Math.random;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
document.addEventListener('DOMContentLoaded', () => {

    /*
    * Lógica para el Modo Oscuro (Dark Mode)
    * Se aplica en memory_game.html
    */
    const themeToggleButton = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            if (themeIcon) themeIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            if (themeIcon) themeIcon.classList.replace('bi-sun-fill', 'bi-moon-fill');
        }
    };

    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        applyTheme(systemPrefersDark ? 'dark' : 'light');
    }

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = (currentTheme === 'dark') ? 'light' : 'dark';
            
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }

    /* --- FIN DEL CÓDIGO DE MODO OSCURO --- */

    /* --- CÓDIGO DEL JUEGO EMPIEZA AQUÍ --- */

    const board = document.getElementById('game-board');
    if (board) {
        const movesDisplay = document.getElementById('moves');
        const failsDisplay = document.getElementById('fails');
        const timerDisplay = document.getElementById('timer');
        const pairsFoundDisplay = document.getElementById('pairs-found');
        const totalPairsDisplay = document.getElementById('total-pairs');

        //sonido
        const winSound = new Audio("/static/sounds/win.mp3");
        const loseSound = new Audio("/static/sounds/lose.mp3");
        const flipSound = new Audio("/static/sounds/flip.mp3");

        //modal
        const endGameModal = new bootstrap.Modal(document.getElementById('endGameModal'));
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalButton = document.getElementById('modalButton');

        const resetBtn = document.getElementById('reset-game-btn');
        const muteBtn = document.getElementById('mute-btn');
        const muteIcon = document.getElementById('mute-icon');
        const shareBtn = document.getElementById('share-btn');

        const difficulty = board.dataset.difficulty;
        let isMuted = false;
        let cards = [];
        let hasFlippedCard = false;
        let lockBoard = false;
        let firstCard, secondCard;

        let isGameOver = false;

        let moves = 0;
        let fails = 0;
        let pairsFound = 0;
        let totalPairs = 0;
        let timer = 0;
        let timerInterval = null;

        // Inicializar el generador con la semilla que vino del HTML
        if (typeof gameSeed !== 'undefined' && gameSeed) {
             // Convertimos el string a número para el generador
             const seedNum = parseInt(gameSeed.replace(/\D/g,'').slice(0, 9)) || 12345;
             seededRandom = LCG(seedNum);
        }

        // Configuración de niveles
        const difficultySettings = {
            'basico': { pairs: 6, cols: 4, fails: 15 }, // 15 fallos máx
            'medio': { pairs: 8, cols: 4, fails: 20 }, // 20 fallos máx
            'avanzado': { pairs: 10, cols: 5, fails: 25 } // 25 fallos máx
        };
        let failLimit = 0;

        // Imágenes base (asegúrate de tenerlas en static/img/memory/)
        const baseImages = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png', '9.png', '10.png','11.jpg','12.jpg','13.jpg','14.jpg','15.jpg','16.jpg','17.jpg','18.jpg','19.jpg'];

        // --- Funcion de guardar Resultados
        async function saveGameResult(isWin) {

            // --- USA EL NUEVO 'getCookie' ---
            const csrfToken = getCookie('csrftoken');

            const dataToSend = {
                difficulty: difficulty,
                is_win: isWin,
                time_spent: timer,
                moves: moves,
                fails: fails
            };

            try {
                const response = await fetch('/save-game/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(dataToSend)
                });
                if (!response.ok) {
                    console.error('Error al guardar, pero el juego terminó de todos modos.');
                }
            } catch (error) {
                console.error('Error al guardar:', error);
            }
        }

        function startGame() {
            board.innerHTML = '';

            // Reiniciar todos los contadores
            moves = 0;
            fails = 0;
            pairsFound = 0;
            timer = 0;
            isGameOver = false;
            lockBoard = false;
            [firstCard, secondCard] = [null, null];
            cards = []; // Limpia el array de cartas

            // Actualiza la UI
            movesDisplay.textContent = '0';
            failsDisplay.textContent = '0';
            timerDisplay.textContent = '0s';
            pairsFoundDisplay.textContent = '0';

            const config = difficultySettings[difficulty];
            totalPairs = config.pairs;
            failLimit = config.fails;

            board.style.gridTemplateColumns = `repeat(${config.cols}, 1fr)`;
            
            totalPairsDisplay.textContent = totalPairs;
            
            let gameImages = baseImages.slice(0, totalPairs);
            let cardData = [...gameImages, ...gameImages]; // Duplicar para tener pares
            
            shuffle(cardData);
            
            cardData.forEach(imageName => {
                const card = document.createElement('div');
                card.classList.add('card');
                card.dataset.name = imageName;
                
                card.innerHTML = `
                    <div class="card-face card-front"></div>
                    <div class="card-face card-back" style="background-image: url('/static/img/memory/${imageName}')"></div>
                `;
                
                board.appendChild(card);
                cards.push(card);
            });

            addCardListeners();
            startTimer();
        }
        
        function addCardListeners() {
            cards.forEach(card => card.addEventListener('click', flipCard));
        }

        function shuffle(array) {
            let currentIndex = array.length, randomIndex;

            // Mientras queden elementos para barajar...
            while (currentIndex !== 0) {

                // Elegir un elemento restante...
                // Usamos NUESTRO generador con semilla
                randomIndex = Math.floor(seededRandom() * currentIndex);
                currentIndex--;

                // Y lo intercambiamos con el elemento actual.
                [array[currentIndex], array[randomIndex]] = [
                    array[randomIndex], array[currentIndex]];
            }
        }

        function startTimer() {
            timerInterval = setInterval(() => {
                timer++;
                timerDisplay.textContent = `${timer}s`;
            }, 1000);
        }

        function flipCard() {
            if (lockBoard || isGameOver) return;
            if (this === firstCard) return;

            // --- Audio de Flip ---
            if (!isMuted) {
                flipSound.currentTime = 0; // Reinicia el audio (para clics rápidos)
                flipSound.play();
            }
            // -------------------------

            this.classList.add('is-flipped');

            if (!hasFlippedCard) {
                // Primer click
                hasFlippedCard = true;
                firstCard = this;
                return;
            }

            // Segundo click
            secondCard = this;
            lockBoard = true;
            
            updateCounters();
            checkForMatch();
        }

        function updateCounters() {
            moves++;
            movesDisplay.textContent = moves;
        }

        function checkForMatch() {
            let isMatch = firstCard.dataset.name === secondCard.dataset.name;
            isMatch ? disableCards() : unflipCards();
        }

        function disableCards() {
            // Es un par
            firstCard.removeEventListener('click', flipCard);
            secondCard.removeEventListener('click', flipCard);
            
            pairsFound++;
            pairsFoundDisplay.textContent = pairsFound;
            
            resetBoard();
            checkWinCondition();
        }

        function unflipCards() {
            // No es un par
            fails++;
            failsDisplay.textContent = fails;

            if (fails >= failLimit) {
                endGame(false); // El jugador pierde
            }

            setTimeout(() => {
                firstCard.classList.remove('is-flipped');
                secondCard.classList.remove('is-flipped');
                resetBoard();
            }, 1000); // 1 segundo para memorizar
        }

        function resetBoard() {
            [hasFlippedCard, lockBoard] = [false, false];
            [firstCard, secondCard] = [null, null];
        }

        // Listener para compartir (VERSIÓN ROBUSTA)
        if (shareBtn) {
            shareBtn.addEventListener('click', () => {
                const url = new URL(window.location.href);
                url.searchParams.set('seed', gameSeed); 
                const textToCopy = url.toString();
                
                // Verificamos si la API moderna está disponible y segura
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(textToCopy).then(() => {
                        alert('¡Enlace copiado! Envíalo a un amigo.\nNo olvides iniciar sesion primero!');
                    }).catch(err => {
                        fallbackCopyTextToClipboard(textToCopy);
                    });
                } else {
                    // Si estamos en HTTP (tu caso actual), usamos el método antiguo
                    fallbackCopyTextToClipboard(textToCopy);
                }
            });
        }
        // Función auxiliar para copiar en entornos no seguros (HTTP)
        function fallbackCopyTextToClipboard(text) {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            
            // Evitar que el textarea sea visible
            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    alert('¡Enlace copiado! Envíalo a un amigo.\nNo olvides iniciar sesion primero!');
                } else {
                    prompt("Copia este enlace manualment:", text);
                }
            } catch (err) {
                prompt("Copia este enlace manualmente:", text);
            }
            
            document.body.removeChild(textArea);
        }

        resetBtn.addEventListener('click', () => {
            // Simplemente reinicia el juego. 
            // Esto es seguro porque 'startGame' ya limpia el tablero.
            isGameOver = true; // Marca el juego anterior como terminado
            clearInterval(timerInterval); // Detiene el timer anterior
            startGame(); // Inicia uno nuevo
        });

        muteBtn.addEventListener('click', () => {
            isMuted = !isMuted; // Invierte el estado
            if (isMuted) {
                muteIcon.classList.replace('bi-volume-up-fill', 'bi-volume-mute-fill');
            } else {
                muteIcon.classList.replace('bi-volume-mute-fill', 'bi-volume-up-fill');
            }
        });
        
        function checkWinCondition() {
            if (pairsFound === totalPairs) {
                clearInterval(timerInterval);
                //setTimeout(() => {
                //    alert(`¡Ganaste! \nMovimientos: ${moves} \nFallas: ${fails} \nTiempo: ${timer}s`);
                //    saveGameResult(true);
                //}, 500);
                endGame(true);
            }
        }
        
        function endGame(isWin) {
            if (isGameOver) return; // Evitar que se ejecute múltiples veces
            isGameOver = true;
            clearInterval(timerInterval);

            // Guardar el resultado en la BD (lo haremos asíncrono)
            saveGameResult(isWin);

            if (isWin) {
                // Lógica de Victoria
                if (!isMuted) winSound.play();
                modalTitle.textContent = "¡Felicidades! 🥳";
                modalBody.innerHTML = `
                    Completaste el reto.
                    <br><strong>Movimientos:</strong> ${moves}
                    <br><strong>Fallas:</strong> ${fails}
                    <br><strong>Tiempo:</strong> ${timer}s
                `;
            } else {
                // Lógica de Derrota
                if (!isMuted) loseSound.play();
                modalTitle.textContent = "¡Fin del Juego! 😢";
                modalBody.innerHTML = `
                    Te quedaste sin intentos.
                    <br><strong>Pares encontrados:</strong> ${pairsFound} / ${totalPairs}
                    <br><strong>Tiempo:</strong> ${timer}s
                `;
            }
            // NUEVO: Añadir listener al botón del modal para redirigir
            modalButton.addEventListener('click', () => {
                window.location.href = '/profile/'; // Redirigir al perfil al hacer clic
            });
            // Mostrar el modal
            endGameModal.show();

            // startGame();
        }
};

async function saveGameResult(isWin) {
        const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
        
        const dataToSend = {
            difficulty: difficulty,
            is_win: isWin,
            time_spent: timer,
            moves: moves,
            fails: fails
        };

        try {
            const response = await fetch('/save-game/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(dataToSend)
            });
            //if (response.ok) {
            //    window.location.href = '/profile/'; // Redirigir al perfil
            //}
            if (!response.ok) {
                console.error('Error al guardar, pero el juego terminó de todos modos.');
                }
            } catch (error) {
                console.error('Error al guardar:', error);
            }
        }

        // Iniciar el juego
        startGame();
    });
