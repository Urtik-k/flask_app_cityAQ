# AirQuality Dashboard

Aplikacja webowa do wyszukiwania, przechowywania i przeglądania historycznych danych o jakości powietrza w wybranych miastach. Dane pochodzą z [OpenAQ API](https://openaq.org), są zapisywane w lokalnej bazie danych i można je pobrać jako plik CSV.

## Opis projektu

Projekt powstał w ramach samodzielnej nauki języka Python i rozwijania umiejętności programistycznych. Jego celem jest praktyczne wykorzystanie zdobytej wiedzy poprzez stworzenie aplikacji integrującej zewnętrzne API, bazę danych i interfejs użytkownika.

## Funkcjonalności

- Wyszukiwanie danych na podstawie nazwy miasta i wybranego zakresu dat (do 1000 dni jednorazowo).
- Pobieranie pomiarów z OpenAQ API i zapisywanie ich w bazie danych.
- Sprawdzanie dostępności danych w bazie przed ponownym pobraniem z API. Do API trafia zapytanie tylko o dni, których jeszcze nie ma w bazie.
- Przeglądanie historii pomiarów z podziałem na miasta (`/history/`).
- Prezentowanie wyników w formie tabeli. Brak pomiaru jest oznaczany znakiem „-”.
- **Eksport danych miasta do pliku CSV** (przycisk „Pobierz plik .CSV” w widoku miasta), zawierający wszystkie zapisane w bazie pomiary dla tego miasta.
- Odporność na różne sposoby zapisu nazwy miasta: wielkość liter, nadmiarowe spacje i polskie znaki nie mają znaczenia. Wpisy „lodz”, „ŁÓDŹ” i „ Łódź ” trafiają do tego samego miasta „Łódź”.
- Czytelne komunikaty o błędach (brak klucza API, brak połączenia, nieznane miasto, niepoprawne daty). Formularz zachowuje wpisane dane. Jeśli część danych jest już w bazie, zostaje pokazana razem z ostrzeżeniem.

## Monitorowane zanieczyszczenia

- PM2.5 – pyły zawieszone o średnicy do 2,5 µm.
- PM10 – pyły zawieszone o średnicy do 10 µm.
- NO₂ – dwutlenek azotu.
- CO – tlenek węgla.
- O₃ – ozon.
- SO₂ – dwutlenek siarki.

## Wykorzystane technologie

| Technologia | Zastosowanie |
|---|---|
| Python | Logika aplikacji |
| Flask | Backend i obsługa routingu |
| SQLAlchemy, Flask-Migrate | Baza danych (SQLite), ORM i migracje |
| OpenAQ API | Źródło danych pomiarowych |
| Nominatim (OpenStreetMap) przez geopy | Zamiana nazwy miasta na współrzędne |
| python-dotenv | Wczytywanie konfiguracji z pliku `.env` |
| HTML, CSS, JavaScript | Interfejs użytkownika |
| Bootstrap | Elementy interfejsu |

## Jak to działa

1. Wpisujesz miasto i zakres dat w formularzu.
2. Aplikacja ujednolica nazwę miasta i sprawdza w bazie, których dni brakuje.
3. Dla brakujących dni nazwa miasta jest zamieniana na współrzędne (Nominatim), a następnie z OpenAQ pobierane są pomiary z czujników w promieniu 10 km. Dla każdego zanieczyszczenia wybierany jest najbliższy czujnik, który ma dane z podanego okresu.
4. Nowe pomiary są zapisywane w bazie. Ponowne wyszukanie tego samego dnia uzupełnia istniejący wpis, a nie tworzy duplikatu.
5. Wyniki są wyświetlane w tabeli. Można je pobrać jako plik CSV.

## Wymagania

- Python 3.12 (na tej wersji projekt był rozwijany).
- Konto na [explore.openaq.org](https://explore.openaq.org) i własny klucz API (zakładka Settings).
- Dostęp do internetu przy pobieraniu nowych danych. Dane już zapisane w bazie są dostępne bez niego.

## Uruchomienie projektu

1. Sklonuj repozytorium:

   ```bash
   git clone https://github.com/Urtik-k/flask_app_cityAQ.git
   cd flask_app_cityAQ
   ```

2. Utwórz środowisko wirtualne:

   ```bash
   python -m venv venv
   ```

3. Aktywuj środowisko wirtualne i zainstaluj zależności:

   ```bash
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

4. Skonfiguruj klucz API. W głównym folderze projektu (obok `app.py`) utwórz plik `.env`:

   ```
   OPENAQ_API_KEY=twoj_klucz
   SECRET_KEY=dowolny_losowy_ciag_znakow
   ```

   Plik `.env` jest w `.gitignore`, więc nie trafi do repozytorium. Nie wpisuj klucza na stałe w kodzie i nie udostępniaj tego pliku.

5. Utwórz tabele w bazie danych (przy pierwszym uruchomieniu):

   ```bash
   flask db upgrade
   ```

6. Uruchom aplikację:

   ```bash
   flask run
   ```

   Aplikacja będzie dostępna pod adresem `http://127.0.0.1:5000`.

## Strony aplikacji

| Adres | Opis |
|---|---|
| `/` | Formularz wyszukiwania i wyniki |
| `/history/` | Lista miast zapisanych w bazie |
| `/history/<miasto>/` | Wszystkie zapisane pomiary dla miasta |
| `/download/<miasto>` | Pobranie pomiarów miasta jako plik CSV |

## Plik CSV

Plik zawiera kolumny: `date`, `pm25`, `pm10`, `no2`, `co`, `o3`, `so2`. Wiersze są posortowane według daty, a brak pomiaru to puste pole.

- Separator to średnik, a separatorem dziesiętnym jest przecinek, dzięki czemu polski Excel otwiera plik od razu w osobnych kolumnach.
- Plik jest zapisany w UTF-8 z BOM, więc polskie znaki wyświetlają się poprawnie.
- Nazwa pliku to `air_quality_<miasto>.csv`.
- Jeśli potrzebujesz klasycznego CSV (przecinek i kropka), zmień `CSV_DELIMITER` i `CSV_DECIMAL` na początku pliku `file_handler.py`.

## Struktura projektu

```
app.py            tworzenie aplikacji Flask, konfiguracja
routes.py         adresy URL i obsługa żądań
file_handler.py   pobieranie danych z API, operacje na bazie, eksport CSV
models.py         model tabeli measurement
database.py       obiekt bazy danych
migrations/       migracje bazy (Alembic)
templates/        szablony HTML
static/           CSS, JavaScript, obrazy
instance/         lokalna baza SQLite (app_data.db)
.env              klucz API (tworzysz sam, nie jest w repozytorium)
```

## Ograniczenia

- Jednorazowo można pobrać maksymalnie 1000 dni.
- Aplikacja zapisuje same wartości pomiarów, bez jednostek. Jednostki zależą od czujnika i zanieczyszczenia.
- Dane pochodzą z czujników w promieniu 10 km od środka miasta. Dla małych miejscowości może ich nie być.
- Dane dla danego dnia i zanieczyszczenia mogą być niedostępne. W tabeli widać wtedy „-”.
- Usługa Nominatim jest darmowa i ma limity zapytań. Przy bardzo częstych wyszukiwaniach może na chwilę odmówić odpowiedzi.
- Pojedynczy dzień jest po zapisaniu traktowany jako gotowy. Dane uzupełnione później w OpenAQ nie zaktualizują się automatycznie.

## Rozwiązywanie problemów

| Objaw | Co sprawdzić |
|---|---|
| „Brak klucza API OpenAQ” | Czy plik `.env` leży obok `app.py`, nazywa się dokładnie `.env` (nie `.env.txt`) i zawiera `OPENAQ_API_KEY=...`. Po zmianie trzeba zrestartować serwer. |
| „Nie udało się pobrać danych z OpenAQ” | Czy klucz jest poprawny i aktywny oraz czy działa połączenie z internetem. |
| „Nie znaleziono miasta” | Pisownia nazwy. Spróbuj podać nazwę w innym zapisie, np. bez polskich znaków. |
| Błąd o braku tabeli `measurement` | Nie wykonano `flask db upgrade`. |
| Zmiany w modelu nie działają | Po zmianie `models.py` utwórz migrację (`flask db migrate`) i zastosuj ją (`flask db upgrade`). Przy pustej bazie możesz też usunąć `instance/app_data.db` i ponownie wykonać `flask db upgrade`. |
| CSV otwiera się w jednej kolumnie | Plik ma separator `;`. Jeśli Twój Excel używa przecinka, zmień ustawienia w `file_handler.py` (patrz sekcja „Plik CSV”). |

---

**Autor:** Urtik
