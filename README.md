# Task Manager Agent

A smart bilingual task management agent built with Python, Flask, and Vanilla JavaScript, no heavy frameworks, no magic.

This project demonstrates the core logic of an agent in a simple and transparent way. It was built as a companion to a Medium article series about learning agents step by step.

**[English](#english) | [Türkçe](#türkçe)**

---

`<a name="english"></a>`

## Live Demo

Live demo: *(will be added after deployment)*

---

## What Makes This an Agent?

This project does not use CrewAI, LangChain, or OpenAI Agents SDK.

Instead, it demonstrates one key idea: **an agent is not just code that displays data, it is code that analyzes state and decides what to do next.**

```text
Collect task data
       ↓
Analyze priority and deadlines
       ↓
Detect overdue / urgent / high-priority tasks
       ↓
Generate recommendations
       ↓
Guide the user toward action
```

This loop runs on every request. The agent reads the current task list, evaluates conditions, and produces contextual recommendations, all in plain Python, no framework required.

---

## Features

- **Task Creation**: Add tasks with title, priority, and due date
- **Priority Management**: Low, medium, and high priority levels
- **Daily Report**: Total, completed, and pending task statistics
- **Rule-Based Recommendations**: Detects overdue tasks, today's tasks, high-priority items, and upcoming deadlines
- **Optional OpenAI Integration**: Enhances recommendations only when enabled and only for critical cases
- **Google Calendar Integration**: Opens a pre-filled Google Calendar event for each task (no OAuth required)
- **Bilingual Interface**: Turkish and English UI with localStorage persistence
- **Filtering**: All, pending, completed, high-priority views
- **Responsive Design**: Works on desktop and mobile

---

## Recommendation System

The recommendation system has two layers.

### Layer 1: Rule-Based (Always Active)

Works without any API key. The agent reads the task list and produces human-readable recommendation cards:

- Overdue task alerts
- Today's task reminders
- High-priority flags
- Upcoming deadline warnings

These are generated through structured rule logic and templates in `agent.py` not by a language model.

Example output:

```text
It would be best to focus on "Project presentation" first.
This task is due today, so completing it early will reduce pressure.
After that, continue with remaining tasks based on priority.
```

### Layer 2: Optional OpenAI (Conditional)

The app calls OpenAI only if:

- `USE_OPENAI_RECOMMENDATIONS=true`
- `OPENAI_API_KEY` is set
- A critical condition exists (overdue task or upcoming deadline)

This keeps API costs near zero for normal usage.

---

## Tech Stack

**Backend:** Python 3, Flask, Flask-CORS, Gunicorn, optional OpenAI API

**Frontend:** HTML5, CSS3, Vanilla JavaScript (no frameworks)

**Storage:** JSON file (`gorevler.json`)

---

## Local Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd task-manager-agent
```

### 2. Create and Activate a Virtual Environment

**Windows PowerShell:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File

**Rule-based mode (no API key needed):**

```env
USE_OPENAI_RECOMMENDATIONS=false
FLASK_DEBUG=true
PORT=5000
```

**With optional OpenAI:**

```env
OPENAI_API_KEY=your_openai_api_key_here
USE_OPENAI_RECOMMENDATIONS=true
FLASK_DEBUG=true
PORT=5000
```

> OpenAI is fully optional. The app works without it.

### 5. Run

```bash
python app.py
```

Open `http://localhost:5000`

---

## Deploy to Render

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `gunicorn app:app`

**Environment Variables:**

```text
USE_OPENAI_RECOMMENDATIONS=false
```

Or add `OPENAI_API_KEY` and set `USE_OPENAI_RECOMMENDATIONS=true` for the optional layer.

---

## Project Structure

```text
task-manager-agent/
├── frontend/
│   ├── index.html      # Main page
│   ├── style.css       # Responsive styling
│   └── script.js       # UI logic and API communication
├── agent.py            # GorevYoneticisiAgent class
├── app.py              # Flask API server (8 endpoints)
├── gorevler.json       # Task storage
├── requirements.txt
└── .gitignore
```

---

## API Endpoints

| Method | Endpoint                        | Description           |
| ------ | ------------------------------- | --------------------- |
| GET    | `/api/health`                 | Health check          |
| GET    | `/api/gorevler`               | Fetch all tasks       |
| POST   | `/api/gorevler`               | Create a task         |
| PUT    | `/api/gorevler/{id}`          | Mark as completed     |
| DELETE | `/api/gorevler/{id}`          | Delete a task         |
| GET    | `/api/rapor`                  | Daily report          |
| GET    | `/api/oneriler?lang=en`       | Agent recommendations |
| GET    | `/api/gorevler/{id}/calendar` | Google Calendar event |

---

## Data Persistence Note

Tasks are stored in a JSON file. This is intentional for simplicity and learning.

For production use, migrate to PostgreSQL, SQLite with persistent disk, Supabase, Firebase, or MongoDB.

On Render, the JSON file resets on each redeploy.

---

## Links

**Live Demo:** [https://taskmanageragent.onrender.com/](https://taskmanageragent.onrender.com/)

---

---

`<a name="türkçe"></a>`

# Görev Yöneticisi Agent

Python, Flask ve Vanilla JavaScript ile geliştirilmiş akıllı, iki dilli bir görev yöneticisi, ağır framework'ler yok, sihir yok.

Bu proje, bir Medium makale serisinin parçası olarak geliştirildi. Amaç: agent mantığını, framework'lere bağımlı kalmadan, sade Python ile göstermek.

---

## Canlı Demo

Canlı demo: [https://taskmanageragent.onrender.com/](https://taskmanageragent.onrender.com/)

---

## Bu Neden Bir Agent?

Proje CrewAI, LangChain veya OpenAI Agents SDK kullanmıyor.

Burada gösterilmek istenen tek temel fikir şu: **Bir agent, yalnızca veri gösteren kod değildir, mevcut durumu analiz edip bir sonraki adıma karar veren koddur.**

```text
Görev verisi topla
       ↓
Öncelik ve tarihleri analiz et
       ↓
Gecikmiş / acil / yüksek öncelikli görevleri tespit et
       ↓
Öneriler üret
       ↓
Kullanıcıyı eyleme yönlendir
```

Bu döngü her istekte çalışır. Agent, görev listesini okur, koşulları değerlendirir ve bağlamsal öneriler üretir, sade Python, framework gerektirmez.

---

## Özellikler

- **Görev Oluşturma**: Başlık, öncelik ve tarih ile görev ekle
- **Öncelik Yönetimi**: Düşük, orta, yüksek seviyeleri
- **Günlük Rapor**: Toplam, tamamlanan, bekleyen görev istatistikleri
- **Kural Tabanlı Öneriler**: Gecikmiş görevler, bugünkü görevler, yaklaşan tarihler
- **İsteğe Bağlı OpenAI**: Yalnızca etkinleştirildiğinde ve yalnızca kritik durumlarda çalışır
- **Google Takvim Entegrasyonu**: Her görev için OAuth gerektirmeden önceden doldurulmuş etkinlik açar
- **İki Dilli Arayüz**: Türkçe ve İngilizce, tercih tarayıcıda saklanır
- **Filtreleme**: Tümü, bekleyen, tamamlanan, yüksek öncelikli görünümleri
- **Responsive Tasarım**: Masaüstü ve mobil uyumlu

---

## Öneri Sistemi

### Katman 1: Kural Tabanlı (Her Zaman Aktif)

API anahtarı gerekmez. Agent, görev listesini okuyarak insan okunabilir öneri kartları üretir:

- Gecikmiş görev uyarıları
- Bugünkü görev hatırlatıcıları
- Yüksek öncelik bayrakları
- Yaklaşan son tarih uyarıları

Bunlar `agent.py` içindeki kural mantığı ve şablonlarla oluşturulur, bir dil modeli tarafından değil.

Örnek çıktı:

```text
Bugün önce "Proje sunumu"na odaklanmak en iyi tercih olacaktır.
Bu görev bugün son tarihine ulaşıyor, erken tamamlamak baskıyı azaltır.
Ardından kalan görevlere öncelik sırasına göre devam edebilirsin.
```

### Katman 2: İsteğe Bağlı OpenAI

Uygulama OpenAI'yi yalnızca şu koşullar sağlandığında çağırır:

- `USE_OPENAI_RECOMMENDATIONS=true`
- `OPENAI_API_KEY` tanımlı
- Gecikmiş görev veya yaklaşan son tarih gibi kritik bir durum var

Normal kullanımda API maliyeti neredeyse sıfır kalır.

---

## Teknolojiler

**Backend:** Python 3, Flask, Flask-CORS, Gunicorn, isteğe bağlı OpenAI API

**Frontend:** HTML5, CSS3, Vanilla JavaScript (framework yok)

**Depolama:** JSON dosyası (`gorevler.json`)

---

## Yerel Kurulum

### 1. Repoyu Klonla

```bash
git clone <repo-url>
cd task-manager-agent
```

### 2. Sanal Ortam Oluştur ve Aktif Et

**Windows PowerShell:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 4. `.env` Dosyası Oluştur

**Kural tabanlı mod (API anahtarı gerekmez):**

```env
USE_OPENAI_RECOMMENDATIONS=false
FLASK_DEBUG=true
PORT=5000
```

**OpenAI ile birlikte:**

```env
OPENAI_API_KEY=openai_api_anahtarin
USE_OPENAI_RECOMMENDATIONS=true
FLASK_DEBUG=true
PORT=5000
```

### 5. Çalıştır

```bash
python app.py
```

`http://localhost:5000` adresini aç.

---

## Render'a Deploy

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `gunicorn app:app`

**Ortam Değişkenleri:**

```text
USE_OPENAI_RECOMMENDATIONS=false
```

OpenAI için `OPENAI_API_KEY` ekle ve `USE_OPENAI_RECOMMENDATIONS=true` yap.

---

## Proje Yapısı

```text
task-manager-agent/
├── frontend/
│   ├── index.html      # Ana sayfa
│   ├── style.css       # Responsive stil
│   └── script.js       # UI mantığı ve API iletişimi
├── agent.py            # GorevYoneticisiAgent sınıfı
├── app.py              # Flask API sunucusu (8 endpoint)
├── gorevler.json       # Görev depolama
├── requirements.txt
└── .gitignore
```

---

## Veri Kalıcılığı Notu

Görevler JSON dosyasında saklanır. Bu, öğrenme amacıyla bilinçli bir seçimdir.

Render'da her yeniden deploy'da dosya sıfırlanır. Üretim için PostgreSQL, Supabase, Firebase veya MongoDB tercih edilmelidir.

---

## Bağlantılar

**Medium Makale:** *(eklenecek)*

**Canlı Demo:** *(deployment sonrası eklenecek)*
