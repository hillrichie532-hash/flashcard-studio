# 🎴 Flashcard Studio

**Turn a spreadsheet of words into printable, double-sided PDF flashcards — in seconds.**

*Built for language learners who want paper, not another screen.*

---

## ✨ Why this exists

Digital flashcard apps are great — until you want to actually **touch** the cards, cut them out, and study without a phone in your hand.

Flashcard Studio takes a plain list of words and their translations and generates a print-ready, double-sided PDF. Front = word. Back = meaning. Cut along the lines. Start learning.

No accounts. No cloud. No browser extensions. Just a Python script and a PDF.

---

## 📸 Screenshot

![Flashcard Studio screenshot](screenshot.png)

---

## 🚀 Features

- **Flexible input** — Load `.txt`, `.csv`, or `.xlsx` files
- **Custom mapping** — Choose which column goes on the front, which on the back
- **Full-page grid** — Set cards per row and per column
- **Independent font sizing** — Front and back sizes tuned separately
- **Live preview** — Scroll to zoom, drag to pan, click a card to inspect
- **Print-ready output** — Clean PDF with mirrored backs for double-sided printing
- **Unicode-native** — Chinese, Japanese, Korean, Vietnamese all render correctly

---

## ⚡ How to use

### Step 1 — Download

Click the green **Code** button at the top of this page → **Download ZIP**. Unzip the folder.

### Step 2 — Launch

Double-click **`run.sh`**.

- First time: it asks for your password and installs everything automatically.
- Every time after: it just opens the app.

### Step 3 — Make flashcards

1. Click **Browse** and pick your list file.
2. Choose which column is the front and which is the back.
3. Set how many cards per row and column.
4. Click **Generate PDF**.
5. Print double-sided, cut along the lines, study.

---

## 📄 Input file format

Two columns — front word and back meaning. Extra columns are ignored.

Tab-separated `.txt` file:
