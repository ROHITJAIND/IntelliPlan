# 🚀 IntelliPlan - Complete Setup Guide

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Prerequisites:**
   - Docker & Docker Compose installed

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

---

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd intelliplan-backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

   Backend runs on: **http://localhost:8000**

#### Frontend Setup (in new terminal)

1. **Navigate to frontend:**
   ```bash
   cd intelliplan-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

4. **Start development server:**
   ```bash
   npm start
   ```

   Frontend runs on: **http://localhost:3000**

---

## 📚 Data File

The system uses `ENROLLMENT.csv` in the root directory with columns:
- `COURSE_CODE` - Course identifier (e.g., 19AI404)
- `COURSE_NAME` - Full course name
- `FACULTY_NAME` - Instructor name
- `SLOT_NUMBER` - Slot identifier
- `TIMINGS` - Time blocks (e.g., "Monday: 08:00 - 09:00, ...")
- `CREDITS` - Course credits

Example:
```
19AI404,Analysis of Algorithms,Sasikala K,4W2-2,"Monday: 08:00 - 09:00, Saturday: 13:00 - 14:00",3
```

---

## 🧪 Testing

### Run Tests
```bash
cd intelliplan-backend
python -m pytest tests/test_modules.py -v
```

### Run Specific Test Suite
```bash
# Test timings parser
python -m pytest tests/test_modules.py::TestTimingsParser -v

# Test conflict detection
python -m pytest tests/test_modules.py::TestConflictDetector -v

# Test NLP intent detection
python -m pytest tests/test_modules.py::TestIntentDetector -v
```

---

## 🔍 API Testing

### Using cURL

1. **Load data:**
   ```bash
   curl http://localhost:8000/load_data
   ```

2. **Get courses:**
   ```bash
   curl http://localhost:8000/courses
   ```

3. **Generate timetables:**
   ```bash
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"course_codes": ["19AI404", "19AI409"], "optimize": true}'
   ```

4. **Filter timetables:**
   ```bash
   curl -X POST http://localhost:8000/filter \
     -H "Content-Type: application/json" \
     -d '{
       "schedules": [],
       "constraint_text": "No classes on Saturday"
     }'
   ```

### Using FastAPI Interactive Docs
Visit: **http://localhost:8000/docs**

Swagger UI allows you to:
- Test all endpoints interactively
- View request/response schemas
- Download API specifications

---

## 🎯 NLP Constraint Examples

| Constraint | Effect |
|-----------|--------|
| "No classes on Saturday" | Filters out schedules with Saturday classes |
| "No classes on Monday or Friday" | Avoids Mon & Fri |
| "All classes before 1 PM" | Max time filter (13:00) |
| "No classes before 10 AM" | Min time filter (10:00) |
| "No classes between 12 to 2" | Avoid 12:00-14:00 block |
| "Prefer morning classes" | Scores morning schedules higher |
| "Avoid consecutive classes" | Prevents back-to-back classes |

---

## 📊 Workflow Example

### Frontend
1. User selects courses (19AI404, 19AI409)
2. Clicks "Generate Timetables"
3. System shows 3 valid combinations
4. User applies constraint: "No classes on Saturday"
5. Results filtered to 2 combinations
6. User exports selected timetable as PDF

### Backend Processing
```
CSV Load
   ↓
Parse Timings
   ↓
Group by Course Code
   ↓
Generate Combinations (Backtracking)
   ↓
Check Conflicts
   ↓
Rank by Criteria
   ↓
Apply NLP Constraints
   ↓
Return Filtered Results
```

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process and retry
kill -9 <PID>
```

### CORS errors in frontend
- Backend should have CORS enabled (it does by default)
- Verify `REACT_APP_API_URL` in `.env`
- Restart frontend after env changes

### No courses showing
- Verify `ENROLLMENT.csv` exists in root directory
- Check CSV format matches expected columns
- Run `/load_data` endpoint to validate

### PDF export not working
- Check browser console for errors
- Ensure html2canvas and jsPDF are installed
- Try exporting a simple timetable first

---

## 📦 Production Deployment

### Using Docker

**Build images:**
```bash
docker build -t intelliplan-backend ./intelliplan-backend
docker build -t intelliplan-frontend ./intelliplan-frontend
```

**Push to registry:**
```bash
docker tag intelliplan-backend your-registry/intelliplan-backend:latest
docker push your-registry/intelliplan-backend:latest
```

### Deploy to AWS

1. **Elastic Container Service (ECS):**
   - Create task definitions for backend & frontend
   - Set environment variables
   - Configure load balancer

2. **RDS for database (if needed):**
   ```bash
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/intelliplan
   ```

### Deploy to Render

**Backend:**
1. Push code to GitHub
2. Connect GitHub repo to Render
3. Create Web Service
4. Set environment variables
5. Deploy

**Frontend:**
1. Build: `npm run build`
2. Deploy to Vercel/Netlify
3. Set `REACT_APP_API_URL`

---

## 📈 Performance Optimization

### Caching
- Course data is cached after first load
- Clear cache when uploading new CSV

### Database Indexes (if using database)
```sql
CREATE INDEX idx_course_code ON courses(course_code);
CREATE INDEX idx_slot_number ON slots(slot_number);
```

### Frontend Optimization
- Code splitting enabled by default
- Lazy loading for components
- Memoization in TimetableGrid

---

## 🤝 Development Tips

### Adding New Constraints

1. **Add to `ConstraintIntent` enum:**
   ```python
   class ConstraintIntent(Enum):
       MY_NEW_CONSTRAINT = "my_new_constraint"
   ```

2. **Add pattern to `IntentDetector.PATTERNS`**

3. **Implement entity extraction**

4. **Add filter logic in `_schedule_matches_constraint`**

### Adding New API Endpoint

```python
@app.post("/new_endpoint", tags=["Category"])
def new_endpoint(request: RequestModel):
    """Endpoint description"""
    try:
        result = process_data()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📝 Environment Variables

### Backend (.env)
```
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

---

## 🔗 Useful Links

- **FastAPI Docs:** http://localhost:8000/docs
- **React Docs:** https://react.dev
- **Tailwind CSS:** https://tailwindcss.com
- **Pandas Docs:** https://pandas.pydata.org

---

## ❓ FAQ

**Q: Can I use a different CSV file?**
A: Yes! Use the `/upload_csv` endpoint or replace `ENROLLMENT.csv`

**Q: How many courses can I select?**
A: No hard limit, but more courses = exponentially more combinations

**Q: Can constraints be combined?**
A: Yes! The system handles multiple constraints intelligently

**Q: Is the generated timetable saved?**
A: Currently no, but you can export as PDF for your records

**Q: How do I run this on a Mac vs Windows?**
A: All commands work on both. Path separators handled automatically.

---

## 📞 Support

For issues:
1. Check this guide first
2. Review API documentation
3. Run tests to validate setup
4. Check browser/server logs
5. Open GitHub issue with details

---

**Happy scheduling! 📚✨**
