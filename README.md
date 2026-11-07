# Smart Analytics & API Gateway

System przyjmuje transakcje, czyści je (ETL), ocenia jakość danych i udostępnia
przez API z logowaniem. W zestawie jest Node-RED do budowy własnego dashboardu.

## Uruchomienie (wymagany tylko Docker)

```bash
git clone https://github.com/maciek435/smart-analytics-gateway
cd smart-analytics-gateway
cp .env.example .env
```

Otwórz plik `.env` i uzupełnij puste pola:

- `POSTGRES_PASSWORD` – dowolne hasło (same litery i cyfry),
- `JWT_SECRET_KEY` – długi losowy ciąg (np. `openssl rand -hex 32`),
- `ADMIN_PASSWORD` – hasło do Twojego konta admina (opcjonalnie zmień `ADMIN_EMAIL`).

Start:

```bash
docker compose up -d --build
```

Pierwszy start trwa kilka minut. Gotowe, gdy działają:

- API i dokumentacja: http://localhost:8000/docs
- Node-RED: http://localhost:1880

## Pierwsze kroki w API

1. W http://localhost:8000/docs kliknij **Authorize** i zaloguj się danymi z `.env`
   (pole *username* = `ADMIN_EMAIL`).
2. `POST /api/v1/sources` – dodaj źródło, czyli firmę lub system, z którego
   przychodzą transakcje, np. `{"name": "Firma A"}`. W odpowiedzi dostaniesz
   jego `id` (potrzebne w kolejnych krokach). Listę źródeł zobaczysz w
   `GET /api/v1/sources`.
3. `POST /api/v1/users` – utwórz konto klienta: rola `client` i `source_id`
   źródła z kroku 2.
4. `POST /api/v1/ingest` – wyślij transakcje do źródła,
   `POST /api/v1/etl/run` – uruchom czyszczenie (bez niego dane nie pojawią się
   w statystykach).
5. Endpointy do dashboardu: `/api/v1/analytics/summary`,
   `/api/v1/analytics/timeseries`, `/api/v1/transactions`,
   `/api/v1/rejected-transactions`.

## Node-RED

Z poziomu Node-RED adres API to `http://api:8000` (nie `localhost`).
Logowanie: węzeł **http request**, metoda POST, URL `http://api:8000/api/v1/auth/login`,
body jako formularz (`username=...&password=...`). Z odpowiedzi weź `access_token`
i dodawaj go do kolejnych zapytań w nagłówku `Authorization: Bearer <token>`.
Token wygasa po 30 minutach.

## Przydatne komendy

```bash
docker compose logs -f api     # podgląd logów API
docker compose down            # zatrzymanie (dane zostają)
docker compose down -v         # zatrzymanie i USUNIĘCIE wszystkich danych
```

## Gdy coś nie działa

- *„Uzupelnij POSTGRES_PASSWORD...”* – brakuje wartości w pliku `.env`.
- *Port zajęty (8000 lub 1880)* – zamknij program, który go używa.
- *Zmieniłem hasło bazy w .env i nie działa* – baza pamięta pierwsze hasło;
  wykonaj `docker compose down -v` i uruchom ponownie.