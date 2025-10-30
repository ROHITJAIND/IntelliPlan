"""
Module 1: Data Processing & Structuring
Handles CSV import, timings parsing, and course grouping
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class TimeBlock:
    """Represents a single time block (day, start_time, end_time)"""
    day: str
    start_time: str
    end_time: str

    def to_tuple(self) -> Tuple[str, str]:
        """Convert to (day, time) tuple for conflict checking"""
        return (self.day, self.start_time)


@dataclass
class Slot:
    """Represents a single course slot"""
    course_code: str
    course_name: str
    faculty_name: str
    slot_number: str
    credits: int
    time_blocks: List[TimeBlock]

    def to_dict(self):
        return {
            "course_code": self.course_code,
            "course_name": self.course_name,
            "faculty_name": self.faculty_name,
            "slot_number": self.slot_number,
            "credits": self.credits,
            "time_blocks": [asdict(tb) for tb in self.time_blocks],
        }


class TimingsParser:
    """Parse and standardize timing strings"""

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @staticmethod
    def parse_timings(timing_string: str) -> List[TimeBlock]:
        """
        Parse timing string like "Monday: 08:00 - 09:00, Tuesday: 09:00 - 10:00"
        into a list of TimeBlock objects.

        Args:
            timing_string: Raw timing string from CSV

        Returns:
            List of TimeBlock objects
        """
        if not timing_string or pd.isna(timing_string):
            return []

        time_blocks = []
        # Pattern: "Day: HH:MM - HH:MM"
        pattern = r"(\w+):\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})"

        matches = re.findall(pattern, timing_string)
        for day, start_time, end_time in matches:
            # Validate day
            if day not in TimingsParser.DAYS:
                print(f"Warning: Unknown day '{day}' in timing string: {timing_string}")
                continue

            # Validate time format
            if not TimingsParser._is_valid_time(start_time) or not TimingsParser._is_valid_time(end_time):
                print(f"Warning: Invalid time format in: {timing_string}")
                continue

            time_blocks.append(TimeBlock(day=day, start_time=start_time, end_time=end_time))

        return time_blocks

    @staticmethod
    def _is_valid_time(time_str: str) -> bool:
        """Validate time in HH:MM format"""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except ValueError:
            return False


class CSVDataImporter:
    """Import and validate CSV data"""

    REQUIRED_COLUMNS = ["COURSE_CODE", "COURSE_NAME", "FACULTY_NAME", "SLOT_NUMBER", "TIMINGS", "CREDITS"]

    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        """
        Load CSV file with validation.

        Args:
            file_path: Path to ENROLLMENT.csv

        Returns:
            Validated Pandas DataFrame
        """
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")

        # Validate columns
        missing_cols = set(CSVDataImporter.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Clean data
        df = CSVDataImporter._clean_data(df)

        # Remove rows with missing critical fields
        df = df.dropna(subset=["COURSE_CODE", "SLOT_NUMBER", "TIMINGS"])

        print(f"✓ Loaded {len(df)} records from CSV")
        return df

    @staticmethod
    def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data"""
        # Remove duplicate rows
        initial_count = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_count:
            print(f"  Removed {initial_count - len(df)} duplicate rows")

        # Trim whitespace from string columns
        str_columns = df.select_dtypes(include=['object']).columns
        for col in str_columns:
            df[col] = df[col].str.strip()

        # Convert CREDITS to numeric
        df["CREDITS"] = pd.to_numeric(df["CREDITS"], errors="coerce")

        return df


class CourseGrouper:
    """Group courses and slots into structured format"""

    @staticmethod
    def group_courses(df: pd.DataFrame) -> Dict[str, List[Slot]]:
        """
        Group DataFrame into nested structure by course code.

        Args:
            df: Validated DataFrame

        Returns:
            Dict mapping course_code -> List of Slot objects
        """
        grouped = {}

        for _, row in df.iterrows():
            course_code = row["COURSE_CODE"]
            course_name = row["COURSE_NAME"]
            faculty_name = row["FACULTY_NAME"]
            slot_number = row["SLOT_NUMBER"]
            credits = int(row["CREDITS"]) if pd.notna(row["CREDITS"]) else 0
            timings = row["TIMINGS"]

            # Parse timings
            time_blocks = TimingsParser.parse_timings(timings)

            # Create Slot object
            slot = Slot(
                course_code=course_code,
                course_name=course_name,
                faculty_name=faculty_name,
                slot_number=slot_number,
                credits=credits,
                time_blocks=time_blocks,
            )

            if course_code not in grouped:
                grouped[course_code] = []

            grouped[course_code].append(slot)

        print(f"✓ Grouped courses into {len(grouped)} unique course codes")
        return grouped

    @staticmethod
    def to_json(grouped: Dict[str, List[Slot]]) -> str:
        """Convert grouped data to JSON"""
        data = {
            course_code: [slot.to_dict() for slot in slots]
            for course_code, slots in grouped.items()
        }
        return json.dumps(data, indent=2)


# Main initialization function
def process_enrollment_data(csv_path: str) -> Dict[str, List[Slot]]:
    """
    Complete data processing pipeline.

    Args:
        csv_path: Path to ENROLLMENT.csv

    Returns:
        Grouped course data
    """
    print("🔄 Starting data processing pipeline...")

    # Step 1: Import and validate CSV
    df = CSVDataImporter.load_csv(csv_path)

    # Step 2: Group courses
    grouped_courses = CourseGrouper.group_courses(df)

    print("✓ Data processing complete!\n")
    return grouped_courses
