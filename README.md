# 🕸️ Wuzzuf Jobs Scraper: Python Job Market Data Collection

A web scraper that collects **Python job listings from [Wuzzuf](https://wuzzuf.net)** (a leading job board in Egypt and the Middle East) and saves them as a clean CSV dataset ready for analysis.

It uses **Selenium** to load the pages like a real browser (the site renders content with JavaScript and runs a bot check) and **BeautifulSoup** to parse the HTML.

## 📌 Overview
| | |
|---|---|
| **Source** | wuzzuf.net search results for "python" |
| **Tools** | Python, Selenium, webdriver-manager, BeautifulSoup (lxml), csv |
| **Output** | `data/wuzzuf_python_jobs.csv`: 99 job listings, 8 columns |

## 🔍 How It Works
1. **Opens one Chrome session** and loops through the search result pages until there are no more jobs.
2. **Waits for elements** with `WebDriverWait` instead of fixed `sleep()` calls, so it is faster and more reliable.
3. **Parses each job card** for title, company, location, posting date, skills, and link.
   - Each field is read from **the same card container** as its title, so data from one job can never shift onto another job when a field is missing.
4. **Visits every job page** to collect the **salary** and the **requirements** list.
5. **Keeps all lists the same length** even when a page fails (it records `N/A` instead), then writes everything to CSV with `utf-8-sig` encoding so Arabic text opens correctly in Excel.

## 📄 Dataset Columns
| Column | Description |
|---|---|
| `job_title` | Job title |
| `company_name` | Hiring company |
| `date` | How long ago the job was posted |
| `locations_name` | City and country |
| `job_skill` | Job type, work mode, experience level, and skill tags |
| `links` | Link to the job page |
| `salary` | Salary (or "Confidential") |
| `responsibilities` | Requirements from the job page |

## 📊 What the Collected Data Shows
From the 99 listings in this snapshot:
- **92%** of the jobs are in **Egypt**, mostly in Cairo and New Cairo.
- Work mode: **62 on-site**, **22 hybrid**, **15 remote**.
- **76** ask for experienced candidates and only **16** are entry level.
- Salary is hidden ("Confidential") in about **70%** of the listings.
- Most requested skills besides Python: **SQL**, **AI**, **JavaScript**, **Machine Learning**, **Git**, and **AWS**.

> This is a one-time snapshot, so the numbers will change on every run.

## ▶️ How to Run
Requires Google Chrome.
```bash
pip install -r requirements.txt
python wuzzuf_scraper.py
```
A Chrome window opens and the scraper works through the pages; the CSV is saved to `data/`. To scrape a different keyword, change `q=python` in `BASE_URL`, and set `MAX_PAGES` to limit the number of pages.

> **Note:** websites change their HTML over time. If the scraper stops finding jobs, the CSS class names in the script need updating. Please scrape responsibly: keep the volume small and respect the website's terms of use.

## 📁 Project Structure
```
├── wuzzuf_scraper.py
├── requirements.txt
└── data/
    └── wuzzuf_python_jobs.csv
```

## 👤 Author
**Waseem Mahmoud** · [LinkedIn](https://www.linkedin.com/in/waseem-mahmoud-a34154213) · [GitHub](https://github.com/waseemalali)
