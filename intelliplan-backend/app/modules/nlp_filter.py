"""
Module 3: AI-Powered NLP Filter
Intent detection and constraint-based timetable filtering
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from .scheduler import TimeTableSchedule
from .data_processor import TimeBlock


class ConstraintIntent(Enum):
    """Supported constraint intents"""
    AVOID_DAY = "avoid_day"
    AVOID_TIME_BLOCK = "avoid_time_block"
    MAX_TIME = "max_time"
    MIN_TIME = "min_time"
    PREFER_MORNING = "prefer_morning"
    AVOID_CONSECUTIVE = "avoid_consecutive"
    NO_CLASSES_BETWEEN = "no_classes_between"
    UNKNOWN = "unknown"


@dataclass
class Constraint:
    """Represents an extracted constraint"""
    intent: ConstraintIntent
    entities: Dict[str, any]
    raw_text: str
    confidence: float = 0.8


class IntentDetector:
    """NLP-based intent detection from natural language"""

    # Pattern definitions for various constraints
    PATTERNS = {
        ConstraintIntent.AVOID_DAY: [
            r"no\s+class(?:es)?\s+on\s+(\w+(?:\s+or\s+\w+)*)",
            r"avoid\s+(\w+(?:\s+or\s+\w+)*)",
            r"(?:not\s+on|skip)\s+(\w+(?:\s+or\s+\w+)*)",
        ],
        ConstraintIntent.MAX_TIME: [
            r"(?:no\s+classes?|all\s+classes?)\s+after\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)",
            r"(?:end|finish)\s+(?:before|by)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)",
        ],
        ConstraintIntent.MIN_TIME: [
            r"(?:no\s+class|all\s+classes?)\s+before\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)",
            r"start\s+(?:from|after)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)",
        ],
        ConstraintIntent.NO_CLASSES_BETWEEN: [
            r"no\s+class(?:es)?\s+(?:from|between)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)\s+(?:to|and)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)",
        ],
        ConstraintIntent.PREFER_MORNING: [
            r"(?:all|only)\s+morning\s+classes?",
            r"prefer\s+morning",
        ],
        ConstraintIntent.AVOID_CONSECUTIVE: [
            r"no\s+(?:back\s+to\s+back|consecutive|continuous)\s+classes?",
            r"avoid\s+(?:back\s+to\s+back|consecutive)",
        ],
    }

    DAYS_MAPPING = {
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday",
        "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "weekend": ["Saturday", "Sunday"],
    }

    @staticmethod
    def detect_intent(text: str) -> List[Constraint]:
        """
        Detect intent(s) and entities from user input text.

        Args:
            text: User's natural language input

        Returns:
            List of Constraint objects
        """
        constraints = []
        text_lower = text.lower().strip()

        # Try each intent pattern
        for intent, patterns in IntentDetector.PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    # Extract entities based on intent
                    entities = IntentDetector._extract_entities(intent, matches, text_lower)
                    constraint = Constraint(
                        intent=intent,
                        entities=entities,
                        raw_text=text,
                        confidence=0.9 if entities else 0.5,
                    )
                    constraints.append(constraint)
                    break

        # If no specific intent matched, return unknown
        if not constraints:
            constraints.append(Constraint(
                intent=ConstraintIntent.UNKNOWN,
                entities={"raw_input": text},
                raw_text=text,
                confidence=0.0,
            ))

        return constraints

    @staticmethod
    def _extract_entities(intent: ConstraintIntent, matches: List, text: str) -> Dict[str, any]:
        """Extract specific entities based on intent"""
        entities = {}

        if intent == ConstraintIntent.AVOID_DAY:
            days_str = matches[0].lower()
            # Handle "or" separated days
            day_list = re.split(r'\s+or\s+', days_str)
            days = []
            for day in day_list:
                day = day.strip()
                if day in IntentDetector.DAYS_MAPPING:
                    mapped = IntentDetector.DAYS_MAPPING[day]
                    if isinstance(mapped, list):
                        days.extend(mapped)
                    else:
                        days.append(mapped)
            entities["days"] = days

        elif intent == ConstraintIntent.MAX_TIME:
            time_str = IntentDetector._extract_time(matches[0])
            entities["max_time"] = time_str

        elif intent == ConstraintIntent.MIN_TIME:
            time_str = IntentDetector._extract_time(matches[0])
            entities["min_time"] = time_str

        elif intent == ConstraintIntent.NO_CLASSES_BETWEEN:
            if len(matches[0]) >= 2:
                start_time = IntentDetector._extract_time(matches[0][0])
                end_time = IntentDetector._extract_time(matches[0][1])
                entities["start_time"] = start_time
                entities["end_time"] = end_time

        elif intent == ConstraintIntent.PREFER_MORNING:
            entities["is_morning"] = True

        elif intent == ConstraintIntent.AVOID_CONSECUTIVE:
            entities["avoid_consecutive"] = True

        return entities

    @staticmethod
    def _extract_time(time_str: str) -> str:
        """Convert various time formats to 24-hour HH:MM format"""
        time_str = time_str.strip().lower()

        # Handle AM/PM format
        is_pm = "pm" in time_str
        is_am = "am" in time_str
        time_str = re.sub(r'\s*(am|pm|a\.m|p\.m)', '', time_str).strip()

        # Parse time
        if ":" in time_str:
            parts = time_str.split(":")
            hour, minute = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        else:
            hour = int(time_str)
            minute = 0

        # Convert to 24-hour format
        if is_pm and hour != 12:
            hour += 12
        elif is_am and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute:02d}"


class ConstraintFilter:
    """Apply constraints to filter timetables"""

    @staticmethod
    def apply_constraints(
        schedules: List[TimeTableSchedule],
        constraints: List[Constraint],
    ) -> List[TimeTableSchedule]:
        """
        Filter timetables based on extracted constraints.

        Args:
            schedules: List of valid timetables
            constraints: List of Constraint objects

        Returns:
            Filtered list of timetables matching all constraints
        """
        if not constraints:
            return schedules

        filtered = schedules
        for constraint in constraints:
            if constraint.intent == ConstraintIntent.UNKNOWN:
                continue

            filtered = ConstraintFilter._apply_single_constraint(filtered, constraint)

        return filtered

    @staticmethod
    def _apply_single_constraint(
        schedules: List[TimeTableSchedule],
        constraint: Constraint,
    ) -> List[TimeTableSchedule]:
        """Apply a single constraint to filter schedules"""
        result = []

        for schedule in schedules:
            if ConstraintFilter._schedule_matches_constraint(schedule, constraint):
                result.append(schedule)

        return result

    @staticmethod
    def _schedule_matches_constraint(schedule: TimeTableSchedule, constraint: Constraint) -> bool:
        """Check if a schedule matches a constraint"""
        intent = constraint.intent
        entities = constraint.entities

        if intent == ConstraintIntent.AVOID_DAY:
            avoid_days = set(entities.get("days", []))
            for slot in schedule.slots:
                for tb in slot.time_blocks:
                    if tb.day in avoid_days:
                        return False
            return True

        elif intent == ConstraintIntent.MAX_TIME:
            max_time = entities.get("max_time")
            for slot in schedule.slots:
                for tb in slot.time_blocks:
                    if tb.start_time > max_time:
                        return False
            return True

        elif intent == ConstraintIntent.MIN_TIME:
            min_time = entities.get("min_time")
            for slot in schedule.slots:
                for tb in slot.time_blocks:
                    if tb.start_time < min_time:
                        return False
            return True

        elif intent == ConstraintIntent.NO_CLASSES_BETWEEN:
            start_time = entities.get("start_time")
            end_time = entities.get("end_time")
            for slot in schedule.slots:
                for tb in slot.time_blocks:
                    if start_time <= tb.start_time <= end_time:
                        return False
            return True

        elif intent == ConstraintIntent.PREFER_MORNING:
            morning_classes = 0
            for slot in schedule.slots:
                for tb in slot.time_blocks:
                    hour = int(tb.start_time[:2])
                    if hour < 12:
                        morning_classes += 1
            return morning_classes >= len(schedule.slots) * 0.6  # At least 60% morning

        elif intent == ConstraintIntent.AVOID_CONSECUTIVE:
            # Check for back-to-back classes in the same day
            day_times: Dict[str, List[str]] = {}
            for slot in schedule.slots:
                for tb in slot.time_blocks:
                    if tb.day not in day_times:
                        day_times[tb.day] = []
                    day_times[tb.day].append(tb.start_time)

            for day, times in day_times.items():
                sorted_times = sorted(set(times))
                for i in range(len(sorted_times) - 1):
                    if int(sorted_times[i + 1][:2]) - int(sorted_times[i][:2]) == 1:
                        return False  # Found consecutive hour
            return True

        return True
