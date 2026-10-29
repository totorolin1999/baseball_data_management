# ⚾ 棒球數據管理系統 (Baseball Data Management System)

一個基於 **Django** 與 **Microsoft SQL Server** 開發的棒球數據管理與統計分析平台。本系統專為棒球隊伍、教練及聯賽管理者設計，提供盃賽管理、賽程安排、球隊陣容管理，以及詳盡的球員打擊與投球數據記錄與維護功能。

---

## 📌 目錄 (Table of Contents)

- [功能特色](#-功能特色-features)
- [技術架構](#-技術架構-tech-stack)
- [系統需求](#-系統需求-prerequisites)
- [快速開始](#-快速開始-getting-started)
  - [1. 複製專案](#1-複製專案)
  - [2. 建立與啟動虛擬環境](#2-建立與啟動虛擬環境)
  - [3. 安裝相依套件](#3-安裝相依套件)
  - [4. 資料庫設定](#4-資料庫設定)
  - [5. 資料庫遷移](#5-資料庫遷移)
  - [6. 建立超級使用者 (可選)](#6-建立超級使用者-可選)
  - [7. 啟動伺服器](#7-啟動伺服器)
- [資料庫結構與關聯](#-資料庫結構與關聯-database-schema)
- [專案結構](#-專案結構-project-structure)
- [授權與聲明](#-授權與聲明-license)

---

## ✨ 功能特色 (Features)

### 1. 🔐 使用者驗證系統
- 提供教練與隊伍管理者的註冊、登入與登出機制。
- 支援資料隔離，各使用者可管理自身球隊與賽事資訊。

### 2. 🏆 盃賽與賽程管理 (Cup & Game Management)
- **盃賽建立與維護**：支援多盃賽同時進行，提供完整的 CRUD（新增、檢視、編輯、刪除）操作。
- **比賽場次設定**：可於指定盃賽內建立賽事，記錄主隊、客隊與比賽狀態。

### 3. 👥 球隊與球員陣容 (Team & Player Roster)
- **球隊管理**：管理主隊 (Home Team) 與客隊 (Away Team) 名單。
- **球員登錄**：記錄球員資料並與隊伍綁定。

### 4. 📊 棒球進階數據追蹤 (Baseball Statistics)
- **打者數據 (Batting Stats)**：
  - 打席 (PA)、一壘安打 (1B)、二壘安打 (2B)、三壘安打 (3B)、全壘打 (HR)
  - 打點 (RBI)、四壞保送 (BB)、故意四壞 (IBB)、觸身球 (HBP)
  - 被三振 (SO)、犧牲短打 (SH)、犧牲飛球 (SF)
  - 棒次與守備位置設定
- **投手數據 (Pitching Stats)**：
  - 投球局數 (IP)、自責分 (ER)
  - 被安打（1B / 2B / 3B / HR）
  - 保送數 (BB / IBB / HBP)、奪三振 (SO)、被犧牲打 (SF)

---

## 🛠 技術架構 (Tech Stack)

- **後端框架**：[Django 4.1](https://www.djangoproject.com/) (Python)
- **資料庫**：[Microsoft SQL Server](https://www.microsoft.com/sql-server)
  - 驅動套件：`mssql-django`、`pyodbc` (ODBC Driver 17 for SQL Server)
- **前端介面**：
  - HTML5 / CSS3 / JavaScript
  - [Bootstrap 4](https://getbootstrap.com/)
  - [django-crispy-forms](https://django-crispy-forms.readthedocs.io/)
- **樣板引擎**：Django Templates

---

## 📋 系統需求 (Prerequisites)

在運行本專案前，請確認您的環境已安裝：
1. **Python 3.9+**
2. **Microsoft SQL Server** (本機 Express 版本或遠端執行個體)
3. **ODBC Driver 17 for SQL Server**（[微軟官方下載連結](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)）

---

## 🚀 快速開始 (Getting Started)

### 1. 複製專案
```bash
git clone https://github.com/totorolin1999/baseball_data_management.git
cd baseball_data_management
```

### 2. 建立與啟動虛擬環境

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 4. 資料庫設定

在 SQL Server Management Studio (SSMS) 或命令列中建立資料庫：
```sql
CREATE DATABASE baseballdb;
```

請檢查 `baseball_data_management/settings.py` 中的 `DATABASES` 設定：
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'baseballdb',
        'USER': '',                    # 若使用 SQL 驗證請填寫
        'PASSWORD': '',                # 若使用 SQL 驗證請填寫
        'HOST': 'localhost\\SQLEXPRESS',# 您的 SQL Server 執行個體名稱
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'isolation_level': 'READ UNCOMMITTED',
        }
    }
}
```

### 5. 資料庫遷移
執行 Django 遷移以建立所有必要的資料表：
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 建立超級使用者 (可選)
```bash
python manage.py createsuperuser
```

### 7. 啟動伺服器
```bash
python manage.py runserver
```
伺服器啟動後，請於瀏覽器開啟：[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🗄 資料庫結構與關聯 (Database Schema)

本系統的核心實體關係如下：

```
User (使用者)
 ├── Cup (盃賽)
 │    └── Game (比賽)
 │         ├── Batting (打擊紀錄，透過 Player 與 Team 關聯)
 │         └── Pitching (投球紀錄，透過 Player 與 Team 關聯)
 └── Team (球隊)
      ├── Team_Cup (球隊參加的盃賽)
      ├── Team_Game (球隊參與的比賽)
      └── Team_Player (球隊成員)
```

- **Player (球員)**：跨球隊與比賽的全域球員實體，經由關聯表參與比賽並記錄成績。
- **Batting / Pitching**：多對多中介關聯表，記錄每場比賽中各球員的細節攻守數據。

---

## 📁 專案結構 (Project Structure)

```text
baseball_data_management/
├── baseball_data_management/    # Django 專案設定目錄
│   ├── settings.py              # 專案組態設定 (資料庫、App、中介軟體)
│   ├── urls.py                  # 頂層路由設定
│   └── wsgi.py                  # WSGI 伺服器入口
├── management/                  # 核心功能 App (盃賽、比賽、數據管理)
│   ├── admin.py                 # 後台管理設定
│   ├── forms.py                 # 表單定義
│   ├── models.py                # 資料庫模型定義
│   ├── urls.py                  # 業務路由
│   └── views.py                 # 視圖邏輯與數據處理
├── user/                        # 使用者驗證 App
│   ├── forms.py                 # 註冊與登入表單
│   └── views.py                 # 帳號視圖處理
├── templates/                   # 前端 HTML 樣板
│   ├── dashboard/               # 盃賽、球隊、數據各功能畫面
│   ├── partials/                # 共用導航列、頁尾與基礎底板
│   └── user/                    # 註冊與登入畫面
├── static/                      # 靜態資源 (CSS, SVG, 圖片)
├── manage.py                    # Django 命令列工具
└── requirements.txt             # 專案相依套件清單
```

---

## 📄 授權與聲明 (License)

本專案供學習與管理使用。如有任何改進建議或問題回報，歡迎提交 Issue 或 Pull Request！
