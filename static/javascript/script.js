document.addEventListener("DOMContentLoaded", () => {

    // Obsługa zakresu dat
    const startDate = document.getElementById("start_date");
    const endDate = document.getElementById("end_date");

    if (startDate && endDate) {

        startDate.addEventListener("change", () => {
            endDate.min = startDate.value;

            if (endDate.value && endDate.value < startDate.value) {
                endDate.value = startDate.value;
            }
        });

        endDate.addEventListener("change", () => {
            startDate.max = endDate.value;

            if (startDate.value && startDate.value > endDate.value) {
                startDate.value = endDate.value;
            }
        });
    }

    // Animacja przycisku wyszukiwania
    const form = document.getElementById("search-form");
    const button = document.getElementById("submit-button");

    if (form && button) {
        form.addEventListener("submit", () => {
            button.disabled = true;
            button.innerHTML = "<span>Pobieranie danych...</span><span>⏳</span>";
            button.style.opacity = "0.7";
        });
    }

    // Pojawianie się elementów
    const animatedElements = document.querySelectorAll(
        ".hero, .form-card, .table-card, .empty-state"
    );

    animatedElements.forEach((element, index) => {
        element.style.opacity = "0";
        element.style.transform = "translateY(15px)";

        setTimeout(() => {
            element.style.transition = "opacity 0.6s ease, transform 0.6s ease";
            element.style.opacity = "1";
            element.style.transform = "translateY(0)";
        }, 100 + index * 120);
    });

});