# Cyanide

**Cyanide** to honeypot SSH i Telnet o wysokiej interakcji, zaprojektowany do zwodzenia i analizowania zachowań atakujących. Łączy w sobie realistyczną emulację systemu plików Linux, zaawansowaną symulację komend oraz hybrydowy silnik ML do wykrywania anomalii.

---

## 🌟 Główne Funkcje

### 🧠 Realistyczna Emulacja
*   **Wieloprotokołowość**: Obsługa SSH (`asyncssh`) i Telnet na niestandardowych portach (domyślnie 2222/2223).
*   **Dynamiczny VFS**: W pełni funkcjonalny system plików Linux w pamięci, ładowany z profili YAML. Zmiany są zachowywane w ramach sesji.
*   **Zaawansowany Shell**: Obsługa potoków (`|`), przekierowań (`>`, `>>`), logiki (`&&`, `||`) i zmiennych środowiskowych.
*   **Anti-Fingerprinting**:
    *   **Network Jitter**: Losowe opóźnienia odpowiedzi (50-300ms).
    *   **Profile OS**: Realistyczne maskowanie jako **Ubuntu**, **Debian** lub **CentOS** z dynamicznymi listami procesów (`ps`), plikami `/proc` i historycznymi znacznikami czasu systemu plików.

### 🛡️ Hybrydowy System Wykrywania
Cyanide wykorzystuje 3-warstwowy silnik do identyfikacji zagrożeń:
1.  **Detektor Anomalii ML**: Sieć neuronowa (autoenkoder) wykrywa nietypowe struktury komend.
2.  **Silnik Reguł**: Sygnatury Regex dla znanych ataków (`wget`, `curl | bash`).
3.  **Analizator Kontekstu**: Analiza semantyczna dostępu do plików (`/etc/shadow`) i reputacji IP.

### 📊 Informatyka Śledcza i Logowanie
*   **Nagrywanie TTY**: Pełny zapis sesji kompatybilny z `scriptreplay`.
*   **Logi JSON**: Szczegółowe zdarzenia dla ELK/Splunk.
*   **Biometria Klawiatury**: Analiza rytmu pisania.
*   **Kwarantanna**: Automatyczna izolacja pobranego malware (`wget`).
*   **VirusTotal**: Automatyczne skanowanie plików w kwarantannie.

---

## 📚 Dokumentacja Techniczna

Projekt Cyanide posiada rozbudowaną dokumentację techniczną podzieloną na moduły funkcjonalne. Zapraszamy do naszego **[Centrum Dokumentacji (Documentation Hub)](../index.md)**.

| Sekcja | Opis |
|:---|:---|
| 🏛️ **[Architektura Rdzenia](../core/index.md)** | Mechanika silnika, [konfiguracja](../core/configuration.md) i skalowanie. |
| 📁 **[Silnik VFS](../vfs/index.md)** | Warstwa wirtualnego systemu plików i mapowanie profili OS. |
| 🌐 **[Sieć i Proxy](../networking/index.md)** | Architektura MiTM-proxy i sieciowa anty-forensyka. |
| 🧠 **[Analityka i ML](../ml-analytics/index.md)** | Wewnętrzne działanie systemu wykrywania zagrożeń. |
| 🧪 **[Testy](../tests/index.md)** | Opis stosu testowego i metryki pokrycia kodu. |
| 🔧 **[Utrzymanie](../tooling/index.md)** | Forensyka, odtwarzacz TTY i skrypty monitorujące. |

---

## 🚀 Wdrożenie

**Zaleca się uruchamianie jako kontener Docker.**

### 🐳 Docker Compose

```bash
# 1. Uruchom pełny stos (Honeypot + MailHog + Jaeger)
docker-compose -f deployments/docker/docker-compose.yml up --build -d

# 2. Monitoruj logi
docker-compose -f deployments/docker/docker-compose.yml logs -f cyanide

# 3. Zatrzymaj
docker-compose -f deployments/docker/docker-compose.yml down
```

### 🔧 Konfiguracja

Konfiguracja odbywa się przez pliki **YAML** w `configs/`:

| Plik | Przeznaczenie |
|------|---------------|
| `configs/app.yaml` | Główna konfiguracja (porty, timeouty, ML). |
| `configs/profiles/*.yaml` | Profile OS. Definiują strukturę systemu plików i metadane. |
| `configs/fs.yaml` | (Opcjonalnie) Niestandardowy szablon systemu plików. |

**Zmienne środowiskowe** w `docker-compose.yml` nadpisują ustawienia z `app.yaml`.

---

## 🛠️ Zarządzanie i Narzędzia

Skrypty w `scripts/management/` pomagają zarządzać honeypotem:

| Skrypt | Komenda | Opis |
|--------|---------|------|
| **Stats** | `python3 scripts/management/stats.py` | Statystyki w czasie rzeczywistym (uptime, sesje). |
| **Replay** | `scriptreplay <timing> <log>` | Odtwarzanie sesji TTY (pliki w `var/log/cyanide/tty/`). |

---

## ⚠️ Ostrzeżenie
Oprogramowanie służy **wyłącznie do celów edukacyjnych i badawczych**. Uruchamianie honeypota wiąże się z ryzykiem. Autor nie ponosi odpowiedzialności za szkody.
