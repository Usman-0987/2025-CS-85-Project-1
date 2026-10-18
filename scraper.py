import requests, csv, time

FIELDS = ["title", "author", "year", "editions", "language", "publisher", "subject", "pages"]
URL = "https://openlibrary.org/search.json"
API_FIELDS = "title,author_name,first_publish_year,edition_count,language,publisher,subject,number_of_pages_median"


def first(value):
    """API gives lists. Take the first item as text."""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return value if value is not None else ""


class Scraper:
    def __init__(self, total_pages=160):     
        self.total_pages = total_pages
        self.paused = False
        self.stopped = False
        self.books = []

    def run(self, on_progress):
        for page in range(1, self.total_pages + 1):
            while self.paused and not self.stopped:    
                time.sleep(0.2)
            if self.stopped:                       
                break
            try:
                params = {"q": "fiction", "limit": 100, "page": page, "fields": API_FIELDS}
                data = requests.get(URL, params=params, timeout=60,
                                    headers={"User-Agent": "cs200-student-project"}).json()
                if not data.get("docs"):
                 print("Empty reply:", str(data)[:200])
            except Exception as e:
                print("Error on page", page, e)
                continue
            for d in data.get("docs", []):
                self.books.append({
                    "title": d.get("title", ""),
                    "author": first(d.get("author_name")),
                    "year": d.get("first_publish_year", 0),
                    "editions": d.get("edition_count", 0),
                    "language": first(d.get("language")),
                    "publisher": first(d.get("publisher")),
                    "subject": first(d.get("subject")),
                    "pages": d.get("number_of_pages_median", 0),
                })
            on_progress(page, self.total_pages)
            time.sleep(0.3)                           
        self.save()

    def save(self):
        with open("books.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(self.books)


def load_books():
    try:
        with open("books.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        return []
    for r in rows:
        for col in ["year", "editions", "pages"]:
            try:
                r[col] = int(float(r[col]))
            except ValueError:
                r[col] = 0
    return rows


if __name__ == "__main__":
    s = Scraper(total_pages=160)       
    s.run(lambda page, total: print(f"page {page}/{total}, books: {len(s.books)}")) 

