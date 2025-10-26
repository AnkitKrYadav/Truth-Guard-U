# Truth-Guard

Truth-Guard is a web application that provides real-time trending news and fact-checked claims. Built with a modern React frontend and a Flask backend, it integrates a SQLite database to store news articles and categories. The platform allows users to explore trending topics, filter by categories, and view key statistics at a glance.

---

## Features

- **Trending News:** Displays the latest trending articles from the database.
- **Category Filters:** Filter news by categories such as Politics, Health, Tech, and Entertainment.
- **Statistics Widgets:** Shows key metrics like total trending news, verified claims, and category-wise counts.
- **Responsive Design:** Works on both desktop and mobile screens.
- **API Integration:** Frontend fetches data from backend API endpoints.
- **Easy Deployment:** Ready for hosting on platforms like Render or other free hosting services.

---

## Project Structure

```text
Truth-Guard/
├─ Backend/
│  ├─ app.py              # Flask backend server
│  ├─ requirements.txt    # Python dependencies
│  ├─ news.db             # SQLite database
│  ├─ routes/
│  │  ├─ fetch_news.py
│  │  └─ verify_news.py
│  └─ utils/
│     ├─ fact_check.py
│     ├─ langchain_agent.py
│     └─ news_api.py
├─ database/
│  ├─ connection.py
│  ├─ database.py         # Script to create DB and insert sample data
│  └─ news.db
└─ Frontend/
   └─ react-app/
      ├─ package.json
      ├─ src/
      │  ├─ App.js
      │  ├─ pages/
      │  │  ├─ Dashboard.jsx
      │  │  ├─ Trending.jsx
      │  │  └─ Verify.jsx
      │  └─ components/
      │     ├─ NewsCard.jsx
      │     └─ StatsWidget.jsx
````

---

## Installation

### Backend

1. Navigate to the backend folder:

```bash
cd Backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Flask server:

```bash
python app.py
```

The backend runs on `http://127.0.0.1:5000/`.

---

### Frontend

1. Navigate to the frontend folder:

```bash
cd Frontend/react-app
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

The frontend runs on `http://localhost:3000/` and fetches data from the backend API.

---

## API Endpoints

* `GET /api/trending` – Returns all trending news articles.
* `GET /api/categories` – Returns all available news categories.

---

## Deployment

* The project can be deployed on **Render**, **Vercel**, or other free hosting platforms.
* Ensure both frontend and backend are deployed and frontend points to the correct backend URL.

---

## Screenshots

**Dashboard**
![Dashboard](docs/screenshots/dashboard.png)

**Trending Page**
![Trending](docs/screenshots/trending.png)

---

## Technologies Used

* **Frontend:** React, Tailwind CSS, Axios, React Router
* **Backend:** Flask, SQLite, Flask-CORS
* **Tools:** VS Code, Postman

---

## Future Improvements

* Integrate real-time news APIs for dynamic updates.
* Implement user authentication and personalized news feed.
* Enhance fact-checking using AI integrations.
* Add analytics dashboard for user activity.

---

## License

MIT License © 2025

---

## Author

Uday
Engineering Student & Developer