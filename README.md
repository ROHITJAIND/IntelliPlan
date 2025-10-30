# IntelliPlan - AI-Powered Course Scheduler

A full-stack application that automates and optimizes course timetable creation for university students using AI-driven scheduling and NLP-based preference filtering.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)

## ✨ Features

### Module 1: Data Processing & Structuring
- ✅ CSV data import and validation
- ✅ Intelligent timings parser (converts string to structured format)
- ✅ Course grouping by course code and slot

### Module 2: Core Scheduling Engine
- ✅ Conflict detection between course slots
- ✅ Backtracking scheduler for generating valid combinations
- ✅ Performance optimization with memoization
- ✅ Schedule ranking based on criteria

### Module 3: AI-Powered NLP Filter
- ✅ Intent detection from natural language
- ✅ Constraint parsing (avoid days, time ranges, preferences)
- ✅ Intelligent timetable filtering
- ✅ Multi-constraint support

### Module 4: React Frontend
- ✅ Course selection UI with search
- ✅ Timetable grid visualization
- ✅ Natural language constraint input
- ✅ PDF export functionality

### Module 5: FastAPI Backend
- ✅ RESTful API endpoints
- ✅ Data caching for performance
- ✅ CORS support for frontend integration
- ✅ File upload capabilities

## 🏗️ Architecture

```
IntelliPlan/
├── intelliplan-backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app & endpoints
│   │   └── modules/
│   │       ├── data_processor.py # CSV import & parsing
│   │       ├── scheduler.py      # Conflict detection & scheduling
│   │       └── nlp_filter.py     # NLP intent & filtering
│   ├── tests/
│   │   └── test_modules.py       # Unit & integration tests
│   └── requirements.txt           # Python dependencies
│
├── intelliplan-frontend/          # React frontend
│   ├── src/
│   │   ├── components/           # Reusable React components
│   │   │   ├── CourseSelector.jsx
│   │   │   ├── TimetableGrid.jsx
│   │   │   ├── ConstraintInput.jsx
│   │   │   └── ExportModal.jsx
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.jsx               # Main app component
│   │   └── index.js              # Entry point
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── tailwind.config.js
│
└── ENROLLMENT.csv                 # Course data
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd intelliplan-backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

5. **Run the server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd intelliplan-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create .env file:**
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

4. **Start development server:**
   ```bash
   npm start
   ```
   App will open at `http://localhost:3000`

## 📖 Usage

### 1. Select Courses
- Browse available courses in the left sidebar
- Use search to find courses by code or name
- Click the "+" button to select courses
- View slot options for each course (faculty, timings)

### 2. Generate Timetables
- Click "Generate Timetables" button
- Optionally enable "Optimize Results" for ranked schedules
- System generates all valid conflict-free combinations

### 3. Apply Constraints
- Use natural language to filter results
- Examples:
  - "No classes on Saturday or Sunday"
  - "All classes before 1 PM"
  - "No classes between 12 to 2"
  - "Avoid consecutive classes"

### 4. Navigate & Export
- Use Previous/Next to browse timetables
- View course details and credits
- Click "Export as PDF" to save timetable

## 🔌 API Documentation

### Endpoints

#### 1. **GET /load_data**
Load and preprocess course data
```bash
curl http://localhost:8000/load_data
```

Response:
```json
{
  "status": "success",
  "total_courses": 5,
  "message": "Data loaded successfully"
}
```

#### 2. **GET /courses**
Get list of available courses
```bash
curl http://localhost:8000/courses
```

Response:
```json
{
  "courses": [
    {
      "course_code": "19AI404",
      "course_name": "Analysis of Algorithms",
      "credits": 3,
      "available_slots": 4,
      "slot_options": [...]
    }
  ],
  "count": 5
}
```

#### 3. **POST /generate**
Generate valid timetables
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "course_codes": ["19AI404", "19AI409"],
    "optimize": true
  }'
```

Response:
```json
{
  "status": "success",
  "count": 3,
  "timetables": [...],
  "optimized": true
}
```

#### 4. **POST /filter**
Apply NLP constraints to timetables
```bash
curl -X POST http://localhost:8000/filter \
  -H "Content-Type: application/json" \
  -d '{
    "schedules": [...],
    "constraint_text": "No classes on Saturday"
  }'
```

#### 5. **GET /stats**
Get system statistics
```bash
curl http://localhost:8000/stats
```

## 🧪 Testing

### Run Unit Tests

Backend:
```bash
cd intelliplan-backend
python -m pytest tests/test_modules.py -v
```

Tests cover:
- CSV parsing and validation
- Timings parsing
- Conflict detection
- Backtracking scheduler
- NLP intent detection
- Constraint filtering

### Run Specific Test
```bash
python -m pytest tests/test_modules.py::TestConflictDetector -v
```

## 🚢 Deployment

### Backend Deployment (Render/AWS Lambda)

1. **Prepare for deployment:**
   ```bash
   pip freeze > requirements.txt
   ```

2. **Create `Procfile`:**
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Deploy to Render:**
   - Connect GitHub repository
   - Set environment variables
   - Deploy from main branch

### Frontend Deployment (Vercel/Netlify)

1. **Build production bundle:**
   ```bash
   npm run build
   ```

2. **Deploy to Vercel:**
   ```bash
   npm install -g vercel
   vercel
   ```

3. **Configure environment:**
   - Set `REACT_APP_API_URL` to production API URL

## 📊 Example Workflow

```python
# Backend Python example
from app.modules.data_processor import process_enrollment_data
from app.modules.scheduler import BacktrackingScheduler
from app.modules.nlp_filter import IntentDetector, ConstraintFilter

# Load data
grouped_courses = process_enrollment_data('ENROLLMENT.csv')

# Create scheduler
scheduler = BacktrackingScheduler(grouped_courses)

# Generate timetables
schedules = scheduler.generate_timetables(['19AI404', '19AI409'])

# Parse constraint
constraints = IntentDetector.detect_intent('No classes on Saturday')

# Filter timetables
filtered = ConstraintFilter.apply_constraints(schedules, constraints)

print(f"Found {len(filtered)} valid schedules")
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/intelliplan/issues)
- Email: support@intelliplan.com

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Real-time collaboration
- [ ] Instructor availability checking
- [ ] Room allocation optimization
- [ ] Student feedback analytics
- [ ] Advanced ML-based recommendations

---

**Built with ❤️ for students by AI**
