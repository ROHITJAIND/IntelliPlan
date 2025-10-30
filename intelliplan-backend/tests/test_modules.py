"""
Module 6: Unit and Integration Tests
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import modules
from app.modules.data_processor import (
    TimingsParser, TimeBlock, CSVDataImporter, CourseGrouper, Slot
)
from app.modules.scheduler import ConflictDetector, BacktrackingScheduler
from app.modules.nlp_filter import IntentDetector, ConstraintFilter, ConstraintIntent


class TestTimingsParser(unittest.TestCase):
    """Test Module 1: Timings Parser"""

    def test_parse_valid_timing(self):
        """Test parsing valid timing string"""
        timing_str = "Monday: 08:00 - 09:00, Wednesday: 10:00 - 11:00"
        blocks = TimingsParser.parse_timings(timing_str)

        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].day, "Monday")
        self.assertEqual(blocks[0].start_time, "08:00")
        self.assertEqual(blocks[1].day, "Wednesday")

    def test_parse_empty_timing(self):
        """Test parsing empty/None timing"""
        blocks = TimingsParser.parse_timings("")
        self.assertEqual(len(blocks), 0)

    def test_parse_invalid_day(self):
        """Test parsing invalid day"""
        timing_str = "InvalidDay: 08:00 - 09:00"
        blocks = TimingsParser.parse_timings(timing_str)
        self.assertEqual(len(blocks), 0)

    def test_is_valid_time(self):
        """Test time validation"""
        self.assertTrue(TimingsParser._is_valid_time("08:00"))
        self.assertTrue(TimingsParser._is_valid_time("23:59"))
        self.assertFalse(TimingsParser._is_valid_time("24:00"))
        self.assertFalse(TimingsParser._is_valid_time("invalid"))


class TestConflictDetector(unittest.TestCase):
    """Test Module 2: Conflict Detection"""

    def setUp(self):
        """Setup test fixtures"""
        self.time_block_1 = TimeBlock("Monday", "08:00", "09:00")
        self.time_block_2 = TimeBlock("Monday", "09:00", "10:00")
        self.time_block_3 = TimeBlock("Tuesday", "08:00", "09:00")

        self.slot_1 = Slot(
            course_code="19AI404",
            course_name="Analysis of Algorithms",
            faculty_name="Sasikala K",
            slot_number="4W2-2",
            credits=3,
            time_blocks=[self.time_block_1],
        )

        self.slot_2 = Slot(
            course_code="19AI409",
            course_name="Applied AI",
            faculty_name="Lavanya G",
            slot_number="4K1-1",
            credits=3,
            time_blocks=[self.time_block_2],  # Same day but different start time
        )

        self.slot_3 = Slot(
            course_code="19CE521",
            course_name="Air Pollution Engineering",
            faculty_name="Padma S",
            slot_number="3J1-1",
            credits=3,
            time_blocks=[self.time_block_3],  # Different day
        )

    def test_no_conflict_different_days(self):
        """Test no conflict when classes on different days"""
        has_conflict = ConflictDetector.check_conflict(self.slot_1, self.slot_3)
        self.assertFalse(has_conflict)

    def test_no_conflict_different_times_same_day(self):
        """Test no conflict when different times on same day"""
        has_conflict = ConflictDetector.check_conflict(self.slot_1, self.slot_2)
        self.assertFalse(has_conflict)

    def test_conflict_same_time(self):
        """Test conflict when same day and time"""
        slot_same = Slot(
            course_code="19ME533",
            course_name="3D Printing",
            faculty_name="Muthukumar V",
            slot_number="4C1-1",
            credits=4,
            time_blocks=[TimeBlock("Monday", "08:00", "09:00")],
        )
        has_conflict = ConflictDetector.check_conflict(self.slot_1, slot_same)
        self.assertTrue(has_conflict)

    def test_conflict_in_group(self):
        """Test conflict detection in group of slots"""
        has_conflict, pair = ConflictDetector.check_conflict_in_group(
            [self.slot_1, self.slot_3]
        )
        self.assertFalse(has_conflict)


class TestIntentDetector(unittest.TestCase):
    """Test Module 3: NLP Intent Detection"""

    def test_detect_avoid_day_monday(self):
        """Test detecting avoid day constraint"""
        constraints = IntentDetector.detect_intent("No classes on Monday")
        self.assertGreater(len(constraints), 0)
        self.assertEqual(constraints[0].intent, ConstraintIntent.AVOID_DAY)
        self.assertIn("Monday", constraints[0].entities.get("days", []))

    def test_detect_max_time(self):
        """Test detecting max time constraint"""
        constraints = IntentDetector.detect_intent("No classes after 1 PM")
        self.assertGreater(len(constraints), 0)
        found = any(c.intent == ConstraintIntent.MAX_TIME for c in constraints)
        self.assertTrue(found)

    def test_detect_multiple_days(self):
        """Test detecting multiple days to avoid"""
        constraints = IntentDetector.detect_intent("No classes on Monday or Friday")
        self.assertGreater(len(constraints), 0)
        days = constraints[0].entities.get("days", [])
        self.assertIn("Monday", days)
        self.assertIn("Friday", days)

    def test_extract_time_24hour(self):
        """Test time extraction to 24-hour format"""
        time_24 = IntentDetector._extract_time("14:30")
        self.assertEqual(time_24, "14:30")

    def test_extract_time_pm(self):
        """Test time extraction with PM"""
        time_24 = IntentDetector._extract_time("2 PM")
        self.assertEqual(time_24, "14:00")

    def test_extract_time_am(self):
        """Test time extraction with AM"""
        time_24 = IntentDetector._extract_time("8 AM")
        self.assertEqual(time_24, "08:00")


class TestConstraintFilter(unittest.TestCase):
    """Test Module 3: Constraint Filtering"""

    def setUp(self):
        """Setup test fixtures"""
        from app.modules.scheduler import TimeTableSchedule

        # Create test slots
        self.slot_monday = Slot(
            course_code="19AI404",
            course_name="Analysis of Algorithms",
            faculty_name="Sasikala K",
            slot_number="4W2-2",
            credits=3,
            time_blocks=[TimeBlock("Monday", "08:00", "09:00")],
        )

        self.slot_saturday = Slot(
            course_code="19AI409",
            course_name="Applied AI",
            faculty_name="Lavanya G",
            slot_number="4K1-1",
            credits=3,
            time_blocks=[TimeBlock("Saturday", "10:00", "11:00")],
        )

        # Create test schedules
        self.schedule_with_monday = TimeTableSchedule(
            slots=[self.slot_monday],
            course_codes=["19AI404"],
            total_credits=3,
        )

        self.schedule_with_saturday = TimeTableSchedule(
            slots=[self.slot_saturday],
            course_codes=["19AI409"],
            total_credits=3,
        )

    def test_filter_avoid_day_saturday(self):
        """Test filtering to avoid Saturday"""
        constraints = IntentDetector.detect_intent("No classes on Saturday")
        schedules = [self.schedule_with_monday, self.schedule_with_saturday]

        filtered = ConstraintFilter.apply_constraints(schedules, constraints)

        # Should only have Monday schedule
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].course_codes[0], "19AI404")


class TestBacktrackingScheduler(unittest.TestCase):
    """Test Module 2: Backtracking Scheduler"""

    def setUp(self):
        """Setup test fixtures"""
        # Mock grouped courses
        self.slot_1a = Slot("19AI404", "AOA", "Sasikala K", "4W2-2", 3,
                           [TimeBlock("Monday", "08:00", "09:00")])
        self.slot_1b = Slot("19AI404", "AOA", "Maha Lakshmi", "4W2-1", 3,
                           [TimeBlock("Tuesday", "08:00", "09:00")])

        self.slot_2a = Slot("19AI409", "Applied AI", "Lavanya G", "4K1-1", 3,
                           [TimeBlock("Monday", "13:00", "14:00")])
        self.slot_2b = Slot("19AI409", "Applied AI", "Saravanan N", "4K1-2", 3,
                           [TimeBlock("Wednesday", "08:00", "09:00")])

        self.grouped = {
            "19AI404": [self.slot_1a, self.slot_1b],
            "19AI409": [self.slot_2a, self.slot_2b],
        }

    def test_generate_single_course(self):
        """Test generating schedules for single course"""
        scheduler = BacktrackingScheduler(self.grouped)
        schedules = scheduler.generate_timetables(["19AI404"])

        # Should have 2 schedules (one per slot)
        self.assertEqual(len(schedules), 2)

    def test_generate_multiple_courses_no_conflict(self):
        """Test generating schedules for multiple courses without conflict"""
        scheduler = BacktrackingScheduler(self.grouped)
        schedules = scheduler.generate_timetables(["19AI404", "19AI409"])

        # Should have multiple valid combinations
        self.assertGreater(len(schedules), 0)

    def test_generate_invalid_course(self):
        """Test error on invalid course"""
        scheduler = BacktrackingScheduler(self.grouped)

        with self.assertRaises(ValueError):
            scheduler.generate_timetables(["INVALID"])


# ============ Integration Tests ============

class TestIntegrationDataPipeline(unittest.TestCase):
    """Integration test: End-to-end data pipeline"""

    def test_full_pipeline(self):
        """Test complete pipeline from parsing to grouping"""
        # Create mock CSV data
        mock_data = {
            "COURSE_CODE": ["19AI404", "19AI404"],
            "COURSE_NAME": ["Analysis of Algorithms", "Analysis of Algorithms"],
            "FACULTY_NAME": ["Sasikala K", "Maha Lakshmi"],
            "SLOT_NUMBER": ["4W2-2", "4W2-1"],
            "TIMINGS": [
                "Monday: 08:00 - 09:00, Monday: 09:00 - 10:00",
                "Tuesday: 08:00 - 09:00, Tuesday: 09:00 - 10:00"
            ],
            "CREDITS": [3, 3],
        }

        import pandas as pd
        df = pd.DataFrame(mock_data)

        # Test grouping
        grouped = CourseGrouper.group_courses(df)

        self.assertIn("19AI404", grouped)
        self.assertEqual(len(grouped["19AI404"]), 2)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
