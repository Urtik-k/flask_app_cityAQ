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
    // Usuwanie pomiaru z tabeli (jeden listener na całą tabelę)
    const tableBody = document.querySelector(".custom-table tbody");

    if (tableBody) {
        tableBody.addEventListener("click", async (event) => {
            const deleteButton = event.target.closest(".delete-button");
            if (!deleteButton) return;

            const row = deleteButton.closest("tr");
            const dateText = row.querySelector(".date-cell").textContent.trim();

            if (!confirm(`Usunąć pomiar z dnia ${dateText}?`)) return;

            deleteButton.disabled = true;

            try {
                const response = await fetch(deleteButton.dataset.url, {
                    method: "DELETE"
                });

                if (!response.ok) {
                    throw new Error(`Serwer odpowiedział kodem ${response.status}`);
                }

                row.remove();

                const remaining = tableBody.querySelectorAll("tr").length;
                const counter = document.getElementById("rows-count");
                if (counter) counter.textContent = remaining;

                // Brak wierszy -> odśwież stronę, żeby pokazać komunikat "Brak wyników"
                if (remaining === 0) window.location.reload();

            } catch (error) {
                console.error(error);
                deleteButton.disabled = false;
                alert("Nie udało się usunąć pomiaru. Spróbuj ponownie.");
            }
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


