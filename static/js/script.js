// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.getElementById('menuIcon');
    const navLinksContainer = document.getElementById('navLinksContainer');

    if (menuIcon && navLinksContainer) {
        menuIcon.addEventListener('click', function() {
            // Alterna a classe 'open' no ícone (para animação do X)
            menuIcon.classList.toggle('open');
            // Alterna a classe 'open' no container de links (para exibir/ocultar)
            navLinksContainer.classList.toggle('open');
        });

        // Fechar o menu quando um link é clicado (útil para Single Page Apps ou para melhor UX)
        const navLinks = navLinksContainer.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Atraso para permitir que a navegação do link ocorra antes do fechamento visual
                setTimeout(() => {
                    menuIcon.classList.remove('open');
                    navLinksContainer.classList.remove('open');
                }, 100); 
            });
        });
    }

    // Script para pré-preencher a data com a data atual
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        dateInput.value = `${year}-${month}-${day}`;
    }
});
