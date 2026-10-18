import sys, os, time, threading
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import pyqtSignal
from scraper import Scraper, load_books, FIELDS
from sorting import ALGOS, get_value
from searching import MODES, linear_search, binary_search, composite_search

UI_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_window.ui")


class MainWindow(QWidget):
    progress_signal = pyqtSignal(int, int)
    done_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi(UI_FILE, self)              # loads the window you designed
        self.setWindowTitle("Book Explorer")
        self.scraper = None
        self.all_rows = load_books()
        self.shown_rows = self.all_rows
        self.fill_dropdowns()
        self.connect_buttons()
        self.progress_signal.connect(self.update_progress)
        self.done_signal.connect(self.scrape_finished)
        self.show_rows(self.shown_rows)

    # ---------- fill the empty dropdowns ----------
    def fill_dropdowns(self):
        self.sort_col.addItems(FIELDS)
        self.then_col.addItems(["(none)"] + FIELDS)
        self.algo_box.addItems(list(ALGOS.keys()))
        self.scope_box.addItems(["Full dataset", "Filtered results only"])
        self.s_col1.addItems(FIELDS)
        self.s_mode1.addItems(MODES)
        self.s_algo.addItems(["Linear", "Binary (exact match)"])
        self.op_box.addItems(["(none)", "AND", "OR", "NOT"])
        self.s_col2.addItems(FIELDS)
        self.s_mode2.addItems(MODES)

    # ---------- connect buttons to functions ----------
    def connect_buttons(self):
        self.start_btn.clicked.connect(self.start_scrape)
        self.pause_btn.clicked.connect(self.pause_scrape)
        self.resume_btn.clicked.connect(self.resume_scrape)
        self.stop_btn.clicked.connect(self.stop_scrape)
        self.sort_btn.clicked.connect(self.do_sort)
        self.bench_btn.clicked.connect(self.do_benchmark)
        self.search_btn.clicked.connect(self.do_search)
        self.reset_btn.clicked.connect(self.reset)

    # ---------- showing data ----------
    def show_rows(self, rows):
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(FIELDS))
        self.table.setHorizontalHeaderLabels(FIELDS)
        for i, row in enumerate(rows):
            for j, field in enumerate(FIELDS):
                self.table.setItem(i, j, QTableWidgetItem(str(row[field])))
        self.table.setUpdatesEnabled(True)
        self.count_label.setText(f"Showing {len(rows)} rows")

    # ---------- scraping ----------
    def start_scrape(self):
        self.scraper = Scraper()
        self.progress.setValue(0)
        threading.Thread(target=self.run_scraper, daemon=True).start()

    def run_scraper(self):
        self.scraper.run(self.progress_signal.emit)
        self.done_signal.emit()

    def update_progress(self, page, total):
        self.progress.setMaximum(total)
        self.progress.setValue(page)
        self.count_label.setText(f"{len(self.scraper.books)} books scraped")

    def pause_scrape(self):
        if self.scraper:
            self.scraper.paused = True

    def resume_scrape(self):
        if self.scraper:
            self.scraper.paused = False

    def stop_scrape(self):
        if self.scraper:
            self.scraper.stopped = True

    def scrape_finished(self):
        self.all_rows = load_books()
        self.shown_rows = self.all_rows
        self.show_rows(self.shown_rows)
        QMessageBox.information(self, "Done", "Scraping finished and saved to books.csv")

    # ---------- sorting ----------
    def get_key(self):
        c1 = self.sort_col.currentText()
        c2 = self.then_col.currentText()
        if c2 == "(none)":
            return lambda r: get_value(r, c1)
        return lambda r: (get_value(r, c1), get_value(r, c2))     # multi-level sort

    def get_scope_rows(self):
        if self.scope_box.currentIndex() == 0:
            return self.all_rows
        return self.shown_rows

    def do_sort(self):
        rows = self.get_scope_rows()
        name = self.algo_box.currentText()
        func, complexity, stable = ALGOS[name]
        self.info_label.setText("Sorting... please wait")
        QApplication.processEvents()
        start = time.time()
        result, comps, swaps = func(rows, self.get_key())
        ms = (time.time() - start) * 1000
        self.shown_rows = result
        self.show_rows(result)
        self.info_label.setText(f"{name}: {ms:.1f} ms | comparisons: {comps} | "
                                f"swaps: {swaps} | {complexity} | {stable}")

    def do_benchmark(self):
        rows = self.get_scope_rows()
        key = self.get_key()
        headers = ["Algorithm", "Time (ms)", "Comparisons", "Swaps", "Complexity", "Stable?"]
        self.bench_table.setColumnCount(len(headers))
        self.bench_table.setHorizontalHeaderLabels(headers)
        self.bench_table.setRowCount(len(ALGOS))
        for i, (name, (func, complexity, stable)) in enumerate(ALGOS.items()):
            self.info_label.setText(f"Benchmark running: {name}...")
            QApplication.processEvents()
            start = time.time()
            result, comps, swaps = func(rows, key)
            ms = (time.time() - start) * 1000
            values = [name, f"{ms:.1f}", comps, swaps, complexity, stable]
            for j, v in enumerate(values):
                self.bench_table.setItem(i, j, QTableWidgetItem(str(v)))
            QApplication.processEvents()
        self.info_label.setText("Benchmark finished")

    # ---------- searching ----------
    def do_search(self):
        rows = self.all_rows
        cond1 = (self.s_col1.currentText(), self.s_mode1.currentText(), self.s_text1.text())
        op = self.op_box.currentText()
        start = time.time()
        try:
            if op != "(none)":
                cond2 = (self.s_col2.currentText(), self.s_mode2.currentText(),
                         self.s_text2.text())
                result = composite_search(rows, cond1, op, cond2)
            elif self.s_algo.currentIndex() == 1:
                result = binary_search(rows, cond1[0], cond1[2])
            else:
                result = linear_search(rows, cond1)
        except ValueError:
            QMessageBox.warning(self, "Error", "This column needs a number for binary search.")
            return
        ms = (time.time() - start) * 1000
        self.shown_rows = result
        self.show_rows(result)
        self.info_label.setText(f"Search found {len(result)} rows in {ms:.2f} ms")

    def reset(self):
        self.shown_rows = self.all_rows
        self.show_rows(self.shown_rows)
        self.info_label.setText("")


app = QApplication.instance() or QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()