"""
Module 5: FastAPI Backend
RESTful API endpoints for the IntelliPlan system
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path

from app.modules.data_processor import process_enrollment_data, CSVDataImporter
from app.modules.scheduler import BacktrackingScheduler
from app.modules.nlp_filter import IntentDetector, ConstraintFilter


# ============ Pydantic Models ============

class TimeBlockModel(BaseModel):
    day: str
    start_time: str
    end_time: str


class SlotModel(BaseModel):
    course_code: str
    course_name: str
    faculty_name: str
    slot_number: str
    credits: int
    time_blocks: List[TimeBlockModel]


class TimetableModel(BaseModel):
    slots: List[SlotModel]
    course_codes: List[str]
    total_credits: int


class CourseListResponse(BaseModel):
    courses: List[Dict[str, Any]]
    count: int


class GenerateRequest(BaseModel):
    course_codes: List[str]
    slot_preferences: Dict[str, List[str]] = {}  # courseCode -> [slotNumbers]


class FilterRequest(BaseModel):
    schedules: List[TimetableModel]
    constraint_text: str


class FilterResponse(BaseModel):
    filtered_timetables: List[TimetableModel]
    constraints_applied: List[Dict[str, Any]]
    count: int


# ============ FastAPI App Setup ============

app = FastAPI(
    title="IntelliPlan API",
    description="AI-Powered Course Scheduler",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Global State ============

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "ENROLLMENT.csv")
grouped_courses_cache = None
scheduler_instance = None


def load_data():
    """Load and cache course data"""
    global grouped_courses_cache, scheduler_instance

    if grouped_courses_cache is None:
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

        grouped_courses_cache = process_enrollment_data(DATA_FILE)
        scheduler_instance = BacktrackingScheduler(grouped_courses_cache)

    return grouped_courses_cache


# ============ API Endpoints ============

@app.get("/", tags=["Health"])
def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "message": "IntelliPlan API is running",
        "version": "1.0.0",
    }


@app.get("/load_data", tags=["Data"])
def load_enrollment_data():
    """
    Load and preprocess course data from ENROLLMENT.csv

    Returns:
        - courses: Dictionary mapping course_code to available slots
        - total_courses: Number of unique courses
    """
    try:
        grouped = load_data()

        return {
            "status": "success",
            "message": "Data loaded successfully",
            "total_courses": len(grouped),
            "data_file": DATA_FILE,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/courses", tags=["Data"], response_model=CourseListResponse)
def get_available_courses():
    """
    Get list of available courses and their slots

    Returns:
        - courses: List of course objects with available slots
        - count: Total number of unique courses
    """
    try:
        grouped = load_data()
        courses = []

        for course_code, slots in grouped.items():
            course_data = {
                "course_code": course_code,
                "course_name": slots[0].course_name if slots else "",
                "faculty_name": slots[0].faculty_name if slots else "",
                "credits": slots[0].credits if slots else 0,
                "available_slots": len(slots),
                "slots": [
                    {
                        "slot_number": slot.slot_number,
                        "time_blocks": [
                            {
                                "day": tb.day,
                                "start_time": tb.start_time,
                                "end_time": tb.end_time
                            }
                            for tb in slot.time_blocks
                        ],
                    }
                    for slot in slots
                ],
            }
            courses.append(course_data)

        return CourseListResponse(courses=courses, count=len(courses))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", tags=["Scheduling"], response_model=Dict[str, Any])
def generate_timetables(request: GenerateRequest):
    """
    Generate valid (conflict-free) timetable combinations for selected courses

    Request:
        - course_codes: List of course codes to schedule
        - optimize: Whether to rank schedules by optimization criteria
        - slot_preferences: Dict mapping course_code to list of preferred slot numbers

    Returns:
        - timetables: List of valid timetable combinations
        - count: Number of valid timetables found
        - optimized: Whether results are ranked
    """
    try:
        if not request.course_codes:
            raise HTTPException(status_code=400, detail="At least one course must be selected")

        grouped = load_data()
        
        # Filter slots based on preferences if provided
        if request.slot_preferences:
            filtered_grouped = {}
            for course_code in request.course_codes:
                if course_code in grouped:
                    all_slots = grouped[course_code]
                    
                    # If preferences exist for this course, filter to only those slots
                    if course_code in request.slot_preferences:
                        preferred_slot_numbers = request.slot_preferences[course_code]
                        filtered_slots = [
                            slot for slot in all_slots 
                            if slot.slot_number in preferred_slot_numbers
                        ]
                        
                        if filtered_slots:
                            filtered_grouped[course_code] = filtered_slots
                        else:
                            # If no slots match preferences, use all slots
                            filtered_grouped[course_code] = all_slots
                    else:
                        # No preference for this course, use all slots
                        filtered_grouped[course_code] = all_slots
            
            scheduler = BacktrackingScheduler(filtered_grouped)
        else:
            # No slot preferences, use scheduler with all slots
            scheduler = scheduler_instance or BacktrackingScheduler(grouped)

        # Generate all valid timetables
        schedules = scheduler.generate_timetables(request.course_codes)

        # Convert to response format
        timetables = [schedule.to_dict() for schedule in schedules]

        return {
            "status": "success",
            "count": len(timetables),
            "timetables": timetables,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/filter", tags=["NLP Filtering"], response_model=FilterResponse)
def filter_timetables(request: FilterRequest):
    """
    Apply NLP-based constraints to filter timetables

    Request:
        - schedules: List of timetables to filter
        - constraint_text: Natural language constraint (e.g., "No classes on Saturday")

    Returns:
        - filtered_timetables: Schedules matching the constraint
        - constraints_applied: Parsed constraints
        - count: Number of filtered timetables
    """
    try:
        if not request.schedules:
            raise HTTPException(status_code=400, detail="At least one timetable must be provided")

        if not request.constraint_text.strip():
            return FilterResponse(
                filtered_timetables=[s.dict() for s in request.schedules],
                constraints_applied=[],
                count=len(request.schedules),
            )

        # Detect intents from natural language
        constraints = IntentDetector.detect_intent(request.constraint_text)

        # Filter schedules
        filtered = ConstraintFilter.apply_constraints(request.schedules, constraints)

        # Convert constraints to serializable format
        constraints_info = [
            {
                "intent": c.intent.value,
                "entities": c.entities,
                "confidence": c.confidence,
            }
            for c in constraints
        ]

        return FilterResponse(
            filtered_timetables=[s.dict() for s in filtered],
            constraints_applied=constraints_info,
            count=len(filtered),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload_csv", tags=["Data"])
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a new CSV file to replace ENROLLMENT.csv

    Args:
        file: CSV file to upload

    Returns:
        - status: Upload status
        - message: Success/error message
    """
    try:
        global grouped_courses_cache, scheduler_instance

        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        # Save uploaded file
        save_path = os.path.join(os.path.dirname(DATA_FILE), file.filename)
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Invalidate cache
        grouped_courses_cache = None
        scheduler_instance = None

        # Reload data to validate
        load_data()

        return {
            "status": "success",
            "message": f"CSV file '{file.filename}' uploaded and loaded",
            "file_path": save_path,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Info"])
def get_system_stats():
    """
    Get system statistics

    Returns:
        - total_courses: Total unique courses in system
        - total_slots: Total course slots available
        - data_file: Path to current data file
    """
    try:
        grouped = load_data()

        total_slots = sum(len(slots) for slots in grouped.values())

        return {
            "total_courses": len(grouped),
            "total_slots": total_slots,
            "data_file": DATA_FILE,
            "status": "operational",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Error Handlers ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "status": "error",
        "detail": exc.detail,
        "status_code": exc.status_code,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
