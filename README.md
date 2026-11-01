# AirQuality Dashboard

Aplikacja webowa umożliwiająca wyszukiwanie, przechowywanie i przeglądanie historycznych danych dotyczących jakości powietrza w wybranych miastach.

## Opis projektu

Projekt powstał w ramach samodzielnej nauki języka Python oraz rozwijania umiejętności programistycznych. Jego celem jest praktyczne wykorzystanie zdobytej wiedzy poprzez stworzenie aplikacji webowej integrującej zewnętrzne API, bazę danych oraz interfejs użytkownika.

Aplikacja pobiera dane dotyczące jakości powietrza z OpenAQ API, zapisuje je w bazie danych i umożliwia ich późniejsze przeglądanie.

## Funkcjonalności

- Wyszukiwanie danych na podstawie nazwy miasta.
- Wybór zakresu dat dla pomiarów.
- Pobieranie danych z OpenAQ API.
- Przechowywanie pomiarów w bazie danych.
- Sprawdzanie dostępności danych w bazie przed ponownym pobraniem ich z API.
- Przeglądanie historii pomiarów z podziałem na miasta.
- Prezentowanie wyników w formie tabeli.

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
| SQLAlchemy | Obsługa bazy danych i ORM |
| OpenAQ API | Źródło danych pomiarowych |
| HTML | Struktura stron |
| CSS | Stylizacja interfejsu |
| JavaScript | Interakcje po stronie użytkownika |
| Bootstrap | Elementy interfejsu |

## Uruchomienie projektu

1. Sklonuj repozytorium:

   ```bash
   git clone ADRES_REPOZYTORIUM
   cd NAZWA_PROJEKTU
   ```

2. Utwórz środowisko wirtualne:

   ```bash
   python -m venv venv
   ```

3. Aktywuj środowisko wirtualne i zainstaluj zależności:

   ```bash
   pip install -r requirements.txt
   ```

4. Skonfiguruj klucz API w pliku file_handler.py.

5. Uruchom aplikację:

   ```bash
   flask run
   ```
---

**Autor:** Urtik
