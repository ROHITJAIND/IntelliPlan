# 🎯 IntelliPlan - Quick Reference Card

## ⚡ 60-Second Setup

```bash
# Option 1: Docker (Easiest)
docker-compose up --build
# Open: http://localhost:3000

# Option 2: Manual
cd intelliplan-backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python -m uvicorn app.main:app --reload

# Terminal 2:
cd intelliplan-frontend && npm install
echo "REACT_APP_API_URL=http://localhost:8000" > .env && npm start
# Open: http://localhost:3000
```

---

## 🔌 API Quick Reference

```bash
# Load data
curl http://localhost:8000/load_data

# Get courses
curl http://localhost:8000/courses

# Generate timetables
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"course_codes": ["19AI404"], "optimize": true}'

# Filter by constraint
curl -X POST http://localhost:8000/filter \
  -H "Content-Type: application/json" \
  -d '{"schedules": [], "constraint_text": "No classes on Saturday"}'

# System stats
curl http://localhost:8000/stats

# Interactive docs
open http://localhost:8000/docs
```

---

## 🧪 Testing

```bash
cd intelliplan-backend

# All tests
python -m pytest tests/test_modules.py -v

# Specific test
python -m pytest tests/test_modules.py::TestConflictDetector -v

# With coverage
python -m pytest tests/test_modules.py --cov=app.modules
```

---

## 💻 Python Module Usage

```python
# Import modules
from app.modules.data_processor import process_enrollment_data
from app.modules.scheduler import BacktrackingScheduler
from app.modules.nlp_filter import IntentDetector, ConstraintFilter

# 1. Load data
grouped = process_enrollment_data('ENROLLMENT.csv')

# 2. Create scheduler
scheduler = BacktrackingScheduler(grouped)

# 3. Generate timetables
schedules = scheduler.generate_timetables(['19AI404', '19AI409'])

# 4. Parse constraint
constraints = IntentDetector.detect_intent('No classes on Saturday')

# 5. Filter
filtered = ConstraintFilter.apply_constraints(schedules, constraints)

print(f"Found {len(filtered)} valid schedules")
```

---

## 🎨 React Component Usage

```jsx
import CourseSelector from './components/CourseSelector';
import TimetableGrid from './components/TimetableGrid';
import ConstraintInput from './components/ConstraintInput';

// Select courses
<CourseSelector 
  selectedCourses={selected}
  onCoursesSelected={setSelected}
/>

// Display timetable
<TimetableGrid
  timetable={timetable}
  currentIndex={index}
  totalCount={total}
  onPrevious={() => setIndex(index - 1)}
  onNext={() => setIndex(index + 1)}
/>

// Filter by constraint
<ConstraintInput
  timetables={timetables}
  onFilterApplied={handleFilter}
/>
```

---

## 📊 NLP Constraints Cheat Sheet

```
❌ No classes on Saturday
❌ No classes on Monday or Friday
⏰ All classes before 1 PM
⏰ No classes before 10 AM
🚫 No classes between 12 to 2 PM
☀️ Prefer morning classes
🔄 Avoid consecutive classes
🌙 No classes between 5 PM to 8 PM
```

---

## 📁 File Locations

| File | Location | Purpose |
|------|----------|---------|
| CSV Data | `/ENROLLMENT.csv` | Course data |
| Backend | `/intelliplan-backend/` | FastAPI app |
| Frontend | `/intelliplan-frontend/` | React app |
| Tests | `/tests/test_modules.py` | Test suite |
| Main App | `/app/main.py` | API endpoints |
| Data Parser | `/app/modules/data_processor.py` | CSV handling |
| Scheduler | `/app/modules/scheduler.py` | Scheduling logic |
| NLP | `/app/modules/nlp_filter.py` | Constraint parsing |

---

## ⚙️ Environment Setup

```bash
# Backend .env
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000

# Frontend .env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📚 Documentation Files

| File | Content | Read Time |
|------|---------|-----------|
| IMPLEMENTATION_SUMMARY.md | Overview & status | 5 min |
| README.md | Features & usage | 10 min |
| SETUP_GUIDE.md | Setup instructions | 15 min |
| ARCHITECTURE.md | Technical details | 20 min |
| DOCUMENTATION_INDEX.md | Navigation guide | 5 min |

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Build specific service
docker-compose build backend
docker-compose build frontend
```

---

## 🔧 Troubleshooting Commands

```bash
# Check if ports are available
lsof -i :8000    # Backend
lsof -i :3000    # Frontend

# Kill process on port
kill -9 <PID>

# Clear Docker cache
docker system prune

# Check Python version
python --version

# Check Node version
node --version

# List installed packages (Python)
pip list

# List installed packages (Node)
npm list --depth=0
```

---

## 📊 API Response Examples

### Generate Timetables
```json
{
  "status": "success",
  "count": 3,
  "timetables": [
    {
      "slots": [...],
      "course_codes": ["19AI404", "19AI409"],
      "total_credits": 6
    }
  ],
  "optimized": true
}
```

### Filter Response
```json
{
  "filtered_timetables": [...],
  "constraints_applied": [
    {
      "intent": "avoid_day",
      "entities": {"days": ["Saturday"]},
      "confidence": 0.9
    }
  ],
  "count": 2
}
```

---

## 🎯 Common Workflows

### Workflow 1: Generate & Export
1. Select courses
2. Click "Generate Timetables"
3. Click "Export as PDF"

### Workflow 2: Filter Results
1. Select courses
2. Generate timetables
3. Type constraint: "No classes on Saturday"
4. Click "Apply Filter"

### Workflow 3: Browse Options
1. Generate timetables
2. Use Previous/Next buttons
3. Compare different options
4. Export preferred one

---

## 🧮 Algorithm Complexity

| Algorithm | Time | Space | Best For |
|-----------|------|-------|----------|
| CSV Parse | O(n) | O(n) | Large datasets |
| Conflict Check | O(1) | O(1) | Fast lookup |
| Generate Schedules | O(n^m) | O(m) | 5-10 courses |
| Filter Constraints | O(t*s) | O(t) | 100s of schedules |

---

## 📈 Performance Tips

```python
# Cache results if generating multiple times
scheduler = BacktrackingScheduler(grouped)
schedules = scheduler.generate_timetables(courses)

# Rank high-quality options first
ranked = ScheduleOptimizer.rank_schedules(schedules)

# Use constraints early to reduce search space
constraints = IntentDetector.detect_intent(user_input)
filtered = ConstraintFilter.apply_constraints(schedules, constraints)
```

---

## 🚀 Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables set
- [ ] Docker images built
- [ ] docker-compose.yml configured
- [ ] API URL updated in frontend
- [ ] CORS origins configured
- [ ] Database (optional) migrated
- [ ] SSL certificates installed
- [ ] Monitoring setup
- [ ] Backups configured

---

## 🆘 Help Resources

| Issue | Solution |
|-------|----------|
| Port already in use | Use different port or kill process |
| API not responding | Check if backend is running |
| No courses showing | Verify ENROLLMENT.csv exists |
| CORS errors | Check REACT_APP_API_URL |
| Tests failing | Reinstall requirements |
| PDF export fails | Check browser console |

---

## 📱 Supported Browsers

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 🔐 Security Notes

- [ ] Use HTTPS in production
- [ ] Set ALLOWED_ORIGINS properly
- [ ] Validate all user inputs
- [ ] Use environment variables for secrets
- [ ] Enable CORS only when needed
- [ ] Implement authentication (if needed)

---

## 📞 Support Links

- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **GitHub Issues:** [Create issue]
- **Email:** support@intelliplan.com

---

## ✅ Ready to Go!

```bash
# 1. Clone/Download
cd ENROLLMENT

# 2. Start
docker-compose up --build

# 3. Open
open http://localhost:3000

# 4. Enjoy!
# Select courses → Generate → Filter → Export
```

---

**For detailed help, see DOCUMENTATION_INDEX.md**

*Created: October 28, 2025*
