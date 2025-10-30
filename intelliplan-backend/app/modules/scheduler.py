"""
Module 2: Core Scheduling Engine
Handles conflict detection, backtracking scheduler, and optimization
"""

from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from itertools import combinations, product
from .data_processor import Slot, TimeBlock


class ConflictDetector:
    """Detects scheduling conflicts between slots"""

    @staticmethod
    def check_conflict(slot_a: Slot, slot_b: Slot) -> bool:
        """
        Check if two slots have overlapping timings.

        Args:
            slot_a: First slot
            slot_b: Second slot

        Returns:
            True if conflict exists, False otherwise
        """
        if not slot_a.time_blocks or not slot_b.time_blocks:
            return False

        # Get all (day, start_time) pairs for both slots
        times_a = {(tb.day, tb.start_time) for tb in slot_a.time_blocks}
        times_b = {(tb.day, tb.start_time) for tb in slot_b.time_blocks}

        # Check for intersection
        return bool(times_a & times_b)

    @staticmethod
    def check_conflict_in_group(slots: List[Slot]) -> Tuple[bool, Optional[Tuple[Slot, Slot]]]:
        """
        Check if any pair of slots in a group conflicts.

        Args:
            slots: List of Slot objects

        Returns:
            Tuple (has_conflict, conflicting_pair)
        """
        for i in range(len(slots)):
            for j in range(i + 1, len(slots)):
                if ConflictDetector.check_conflict(slots[i], slots[j]):
                    return True, (slots[i], slots[j])
        return False, None


@dataclass
class TimeTableSchedule:
    """Represents a valid timetable schedule"""
    slots: List[Slot]
    course_codes: List[str]
    total_credits: int

    def to_dict(self):
        return {
            "slots": [slot.to_dict() for slot in self.slots],
            "course_codes": self.course_codes,
            "total_credits": self.total_credits,
        }


class BacktrackingScheduler:
    """Generate valid timetable combinations using backtracking"""

    def __init__(self, grouped_courses: Dict[str, List[Slot]]):
        """
        Initialize scheduler with grouped courses.

        Args:
            grouped_courses: Dict from data_processor.group_courses()
        """
        self.grouped_courses = grouped_courses
        self.memoization_cache: Dict[str, bool] = {}

    def generate_timetables(self, selected_courses: List[str]) -> List[TimeTableSchedule]:
        """
        Generate all valid (conflict-free) timetable combinations.

        Args:
            selected_courses: List of course codes to schedule

        Returns:
            List of valid TimeTableSchedule objects
        """
        # Validate input
        for course_code in selected_courses:
            if course_code not in self.grouped_courses:
                raise ValueError(f"Course {course_code} not found in data")

        # Get slot options for each course
        slot_options = [self.grouped_courses[code] for code in selected_courses]

        # Generate all combinations using backtracking
        valid_schedules = []
        self._backtrack(selected_courses, slot_options, 0, [], valid_schedules)

        return valid_schedules

    def _backtrack(
        self,
        selected_courses: List[str],
        slot_options: List[List[Slot]],
        course_index: int,
        current_selection: List[Slot],
        result: List[TimeTableSchedule],
    ):
        """
        Recursive backtracking function.

        Args:
            selected_courses: List of course codes
            slot_options: Available slots for each course
            course_index: Current course being processed
            current_selection: Currently selected slots
            result: List to collect valid schedules
        """
        # Base case: all courses processed
        if course_index == len(selected_courses):
            # Create a valid schedule
            total_credits = sum(slot.credits for slot in current_selection)
            schedule = TimeTableSchedule(
                slots=current_selection.copy(),
                course_codes=selected_courses.copy(),
                total_credits=total_credits,
            )
            result.append(schedule)
            return

        # Try each slot option for current course
        current_course = selected_courses[course_index]
        for slot in slot_options[course_index]:
            # Check if this slot conflicts with any already selected
            has_conflict = any(
                ConflictDetector.check_conflict(slot, selected_slot)
                for selected_slot in current_selection
            )

            if not has_conflict:
                # Prune early: check memoization
                cache_key = self._get_cache_key(current_selection + [slot])
                if cache_key not in self.memoization_cache:
                    # No prior conflict found with this combination
                    current_selection.append(slot)
                    self._backtrack(
                        selected_courses,
                        slot_options,
                        course_index + 1,
                        current_selection,
                        result,
                    )
                    current_selection.pop()
                    self.memoization_cache[cache_key] = False
                else:
                    # Known valid path from cache
                    current_selection.append(slot)
                    self._backtrack(
                        selected_courses,
                        slot_options,
                        course_index + 1,
                        current_selection,
                        result,
                    )
                    current_selection.pop()

    @staticmethod
    def _get_cache_key(slots: List[Slot]) -> str:
        """Generate cache key for a combination of slots"""
        return "|".join(f"{slot.course_code}-{slot.slot_number}" for slot in slots)

    def clear_cache(self):
        """Clear memoization cache"""
        self.memoization_cache.clear()


class ScheduleOptimizer:
    """Optimize and rank generated schedules"""

    @staticmethod
    def rank_schedules(
        schedules: List[TimeTableSchedule],
        criteria: Optional[Dict[str, any]] = None,
    ) -> List[TimeTableSchedule]:
        """
        Rank schedules based on optimization criteria.

        Args:
            schedules: List of generated schedules
            criteria: Dict with ranking preferences (e.g., {"prefer_morning": True, "max_gaps": 2})

        Returns:
            Sorted list of schedules by score (highest first)
        """
        if not criteria:
            criteria = {}

        def score_schedule(schedule: TimeTableSchedule) -> float:
            score = 0.0

            # Score 1: Fewer gaps between classes
            gaps = ScheduleOptimizer._calculate_gaps(schedule.slots)
            score += (10 - min(gaps, 10))  # Max 10 points

            # Score 2: Classes concentrated (prefer morning/early)
            if criteria.get("prefer_morning", False):
                early_score = ScheduleOptimizer._score_early_classes(schedule.slots)
                score += early_score  # Max 10 points

            # Score 3: Balanced days (fewer classes per day)
            day_balance = ScheduleOptimizer._score_day_distribution(schedule.slots)
            score += day_balance  # Max 10 points

            return score

        # Sort by score in descending order
        ranked = sorted(schedules, key=score_schedule, reverse=True)
        return ranked

    @staticmethod
    def _calculate_gaps(slots: List[Slot]) -> int:
        """Calculate total gap hours between classes"""
        # Simplified: count gaps within each day
        day_times: Dict[str, List[str]] = {}
        for slot in slots:
            for tb in slot.time_blocks:
                if tb.day not in day_times:
                    day_times[tb.day] = []
                day_times[tb.day].append(tb.start_time)

        total_gaps = 0
        for day, times in day_times.items():
            sorted_times = sorted(set(times))
            for i in range(len(sorted_times) - 1):
                gap = int(sorted_times[i + 1][:2]) - int(sorted_times[i][:2])
                if gap > 1:
                    total_gaps += gap - 1
        return total_gaps

    @staticmethod
    def _score_early_classes(slots: List[Slot]) -> float:
        """Score classes occurring earlier in the day"""
        early_count = 0
        for slot in slots:
            for tb in slot.time_blocks:
                hour = int(tb.start_time[:2])
                if hour < 12:  # Before noon
                    early_count += 1

        return min(early_count * 2, 10)

    @staticmethod
    def _score_day_distribution(slots: List[Slot]) -> float:
        """Score balanced distribution across days"""
        day_counts: Dict[str, int] = {}
        for slot in slots:
            for tb in slot.time_blocks:
                day_counts[tb.day] = day_counts.get(tb.day, 0) + 1

        # Prefer balanced distribution (not all classes on 2 days)
        if len(day_counts) > 1:
            return 5.0
        return 0.0
