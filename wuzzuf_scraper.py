import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from itertools import zip_longest

# ============ الإعدادات ============
BASE_URL = 'https://wuzzuf.net/search/jobs?q=python&start={}'
CSV_PATH = Path(__file__).resolve().parent / "data" / "wuzzuf_python_jobs.csv"
MAX_PAGES = None          # حط رقم لو عايز تحدد أقصى عدد صفحات، أو سيبها None
PAGE_LOAD_TIMEOUT = 20    # أقصى وقت انتظار لتحميل عنصر في الصفحة (بالثواني)
# =====================================

job_title = []
company_name = []
locations_name = []
job_skill = []
links = []
salary = []
responsibilities = []
date = []


def get_container(title_tag, max_up=6):
    """
    يطلع لفوق من عنوان الوظيفة (h2) خطوة خطوة لحد ما يلاقي
    العنصر الأب اللي بيحتوي على كل بيانات نفس كارت الوظيفة
    (بنتأكد إنه يحتوي على لينك اسم الشركة كمؤشر إننا في الكارت الصح).
    ده بيمنع اختلاط بيانات وظيفة بوظيفة تانية لو وظيفة ناقصها حقل.
    """
    node = title_tag
    for _ in range(max_up):
        if node.parent is None:
            break
        node = node.parent
        if node.find('a', {'class': 'css-ipsyv7'}):
            return node
    return title_tag.parent


def safe_text(tag, default="N/A"):
    return tag.get_text(strip=True) if tag else default


def wait_for_page(driver, css_selector, timeout=PAGE_LOAD_TIMEOUT):
    """ينتظر لحد ما عنصر معين يظهر في الصفحة، بدل استخدام sleep ثابت."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


# ============== إعداد المتصفح (مرة واحدة بس، مش جوه اللوب) ==============
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # ================= استخراج بيانات القوائم (صفحات النتائج) =================
    page_num = 0
    page_limit = None

    while True:
        try:
            driver.get(BASE_URL.format(page_num))
            wait_for_page(driver, "h2")

            soup = BeautifulSoup(driver.page_source, 'lxml')

            if page_limit is None:
                strong_tag = soup.find('strong')
                if strong_tag:
                    try:
                        page_limit = int(strong_tag.text.replace(',', '').strip())
                    except ValueError:
                        page_limit = 0
                else:
                    page_limit = 0

            if page_limit and page_num > page_limit // 15:
                print('pages ended')
                break

            if MAX_PAGES is not None and page_num >= MAX_PAGES:
                print('reached MAX_PAGES limit')
                break

            job_titles = soup.find_all('h2', {"class": "css-s5fwzh"})
            if not job_titles:
                print('no more jobs found, stopping')
                break

            for title_tag in job_titles:
                container = get_container(title_tag)

                # العنوان + اللينك
                job_title.append(safe_text(title_tag))
                a_tag = title_tag.find('a')
                href = a_tag.attrs.get('href', '') if a_tag else ''
                if href and not href.startswith('http'):
                    href = 'https://wuzzuf.net' + href
                links.append(href if href else "N/A")

                # باقي الحقول - كلها بتتقرأ من نفس الـ container عشان تفضل متزامنة
                company_tag = container.find('a', {'class': 'css-ipsyv7'})
                company_name.append(safe_text(company_tag))

                location_tag = container.find('span', {'class': 'css-16x61xq'})
                locations_name.append(safe_text(location_tag))

                skill_tag = container.find('div', {'class': 'css-1rhj4yg'})
                job_skill.append(safe_text(skill_tag))

                date_tag = (container.find('div', {'class': 'css-eg55jf'}) or
                            container.find('div', {'class': 'css-1jldrig'}))
                date_text = safe_text(date_tag).replace('-', '').strip()
                date.append(date_text if date_text else "N/A")

            print(f'page {page_num} done ({len(job_titles)} jobs)')
            page_num += 1

        except Exception as e:
            print('error occurred while scraping listing page:', e)
            break

    # ================= استخراج تفاصيل كل وظيفة (الراتب + المسؤوليات) =================
    for link in links:
        print("Opening:", link)

        res_text = "N/A"
        salary_text = "Not specified"

        try:
            driver.get(link)
            wait_for_page(driver, "body")

            soup = BeautifulSoup(driver.page_source, 'lxml')

            requirements = soup.find('div', {'dir': 'auto', 'class': 'css-1lqavbg'})
            if requirements and requirements.ul:
                items = [li.get_text(strip=True) for li in requirements.ul.find_all('li')]
                if items:
                    res_text = '| '.join(items)

            rows = soup.find_all('div', {'class': 'css-1ajx53j'})
            for row in rows:
                label = row.find('span', {'class': 'css-720fa0'})
                if label and 'Salary' in label.get_text():
                    value = row.find('span', {'class': 'css-iu2m7n'})
                    if value:
                        salary_text = value.get_text(" ", strip=True)
                    break

            print("Salary:", salary_text)

        except Exception as e:
            print("Error while opening job page:", e)

        # مهم جدًا: بنضيف قيمة لكل قائمة في كل الحالات (حتى لو فيه Error)
        # عشان طول كل القوائم يفضل متطابق مع عدد اللينكات
        responsibilities.append(res_text)
        salary.append(salary_text)

finally:
    driver.quit()

# ================= حفظ البيانات في ملف CSV =================
file_list = [job_title, company_name, date, locations_name, job_skill, links, salary, responsibilities]
exported = zip_longest(*file_list, fillvalue="N/A")

CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as my_file:
    wr = csv.writer(my_file)
    wr.writerow(['job_title', 'company_name', 'date', 'locations_name', 'job_skill', 'links', 'salary', 'responsibilities'])
    wr.writerows(exported)

print(f"Done. Saved {len(job_title)} jobs to {CSV_PATH}")
