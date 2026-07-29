# 🚀 Покроковий Гайд: Створення GitHub-репозиторію та Авто-деплой у Netlify

Цей гайд допоможе вам за **2 хвилини** створити новий репозиторій на GitHub, підключити його до проекту та налаштувати автоматичне оновлення сайту на Netlify через Telegram-бот!

---

## 📌 Крок 1: Створення нового репозиторію на GitHub

1. Зайдіть на сайт **[GitHub.com](https://github.com)** та увійдіть у свій акаунт.
2. У правому верхньому кутку натисніть плюс **`+`** -> **`New repository`** (або перейдіть на [github.com/new](https://github.com/new)).
3. Заповніть поля:
   - **Repository name:** `linettka-website` (або будь-яку зручну назву).
   - **Access:** Оберіть `Public` або `Private`.
   - ⚠️ **ВАЖЛИВО:** **НЕ ставте прапорці** на `Add a README file`, `Add .gitignore` або `Choose a license` (залиште репозиторій абсолютно порожнім!).
4. Натисніть зелену кнопку **`Create repository`**.

---

## 📌 Крок 2: Підключення репозиторію у терміналі Mac

Після створення репозиторію GitHub покаже посилання на ваш новий репозиторій вида:
`https://github.com/ВАШ_USERNAME/linettka-website.git`

Відкрийте Термінал і скопіюйте ці 4 команди (замінивши посилання на своє):

```bash
# 1. Створюємо основну гілку main
git branch -M main

# 2. Підключаємо створений репозиторій GitHub (вставте своє посилання)
git remote add origin https://github.com/ВАШ_USERNAME/linettka-website.git

# 3. Зберігаємо всі файли сайту
git add .
git commit -m "Initial commit linettka portfolio"

# 4. Відправляємо сайт на GitHub
git push -u origin main
```

---

## 📌 Крок 3: Підключення GitHub-репозиторію до Netlify (за 1 хвилин)

1. Зайдіть на **[app.netlify.com](https://app.netlify.com)**.
2. Натисніть **`Add new site`** -> **`Import an existing project`**.
3. Оберіть **`GitHub`** та авторизуйтесь.
4. У списку репозиторіїв виберіть ваш новий **`linettka-website`**.
5. Залиште стандартні налаштування (`Branch: main`, `Publish directory: .`) та натисніть **`Deploy linettka-website`**.

---

## 🎉 Все готово! Як це працює тепер:

Тепер щоразу, коли фотограф надсилає або видаляє фотографію у **Telegram-боті**:
1. Бот зберігає фото у WebP та оновлює `index.html`.
2. Бот робить `git push` на GitHub.
3. Netlify бачить зміни і за **5–10 секунд автоматично оновлює живий сайт у всьому світі!** 🌐✨
