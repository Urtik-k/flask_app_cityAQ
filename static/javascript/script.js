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

    // Usuwanie pomiaru z tabeli z własnym oknem potwierdzenia
    const tableBody = document.querySelector(".custom-table tbody");
    const dialog = document.getElementById("confirm-dialog");

    if (tableBody && dialog) {
        const dateLabel = document.getElementById("confirm-date");
        const errorBox = document.getElementById("confirm-error");
        const yesButton = document.getElementById("confirm-yes");
        const noButton = document.getElementById("confirm-no");

        let pendingButton = null;   // kosz, który został kliknięty

        // Kliknięcie kosza tylko otwiera okno
        tableBody.addEventListener("click", (event) => {
            const deleteButton = event.target.closest(".delete-button");
            if (!deleteButton) return;

            pendingButton = deleteButton;
            dateLabel.textContent = deleteButton
                .closest("tr")
                .querySelector(".date-cell")
                .textContent.trim();

            errorBox.hidden = true;
            yesButton.disabled = false;
            noButton.disabled = false;

            dialog.showModal();
        });

        // Anuluj, klawisz Esc (obsługuje przeglądarka) i kliknięcie w tło zamykają okno
        noButton.addEventListener("click", () => dialog.close());

        dialog.addEventListener("click", (event) => {
            if (event.target === dialog) dialog.close();
        });

        dialog.addEventListener("close", () => {
            pendingButton = null;
        });

        // Potwierdź wysyła żądanie DELETE
        yesButton.addEventListener("click", async () => {
            if (!pendingButton) return;

            const deleteButton = pendingButton;
            const row = deleteButton.closest("tr");

            yesButton.disabled = true;
            noButton.disabled = true;

            try {
                const response = await fetch(deleteButton.dataset.url, {
                    method: "DELETE"
                });

                if (!response.ok) {
                    throw new Error(`Serwer odpowiedział kodem ${response.status}`);
                }

                row.remove();
                dialog.close();

                const remaining = tableBody.querySelectorAll("tr").length;
                const counter = document.getElementById("rows-count");
                if (counter) counter.textContent = remaining;

                // Brak wierszy -> odśwież stronę, żeby pokazać komunikat "Brak wyników"
                if (remaining === 0) window.location.reload();

            } catch (error) {
                console.error(error);
                errorBox.textContent = "Nie udało się usunąć wyniku. Spróbuj ponownie.";
                errorBox.hidden = false;
                yesButton.disabled = false;
                noButton.disabled = false;
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