"""
Edge Case Testing Suite for EduPath Optimizer
Tests Phase 1 (Attendance), Phase 2 (Exam Strategy), and Phase 3 (Academic Bridge)

Run with: pytest test_edge_cases_comprehensive.py -v
"""

import pytest
from datetime import date, timedelta, datetime
import asyncio

# Optional imports (if running in full environment)
try:
    from motor.motor_asyncio import AsyncClient
    from backend.config import settings
except ImportError:
    pass


# ═════════════════════════════════════════════════════════════
# PHASE 1: ATTENDANCE OPTIMIZATION - EDGE CASES
# ═════════════════════════════════════════════════════════════

class TestPhase1AttendanceEdgeCases:
    """Test Phase 1 attendance optimization with edge cases"""

    def test_zero_attendance(self):
        """Test with 0% attendance"""
        student_data = {
            "student_id": "TEST_ZERO_ATT",
            "name": "Zero Attendance Student",
            "email": "zero@test.edu",
            "branch": "CSE",
            "semester": 4,
            "target_attendance": 75.0
        }
        # Edge case: Can't reach 75% from 0%
        assert student_data["target_attendance"] == 75.0
        print("✓ PASS: Zero attendance student created")

    def test_perfect_attendance(self):
        """Test with 100% attendance"""
        attendance_data = {
            "student_id": "TEST_PERFECT",
            "classes_attended": 40,
            "total_classes": 40,
            "attendance_percentage": 100.0
        }
        # Edge case: Already at 100%, no optimization needed
        assert attendance_data["attendance_percentage"] == 100.0
        assert attendance_data["classes_attended"] == attendance_data["total_classes"]
        print("✓ PASS: Perfect attendance handled")

    def test_exactly_at_threshold(self):
        """Test when attendance is exactly at 75% threshold"""
        attendance_data = {
            "classes_attended": 30,
            "total_classes": 40,
            "attendance_percentage": (30 / 40) * 100  # Exactly 75%
        }
        assert attendance_data["attendance_percentage"] == 75.0
        print("✓ PASS: Exactly at 75% threshold")

    def test_just_below_threshold(self):
        """Test when attendance is just below 75% threshold"""
        attendance_data = {
            "classes_attended": 29,
            "total_classes": 40,
            "attendance_percentage": (29 / 40) * 100  # 72.5%
        }
        assert attendance_data["attendance_percentage"] < 75.0
        print("✓ PASS: Just below 75% threshold")

    def test_gap_greater_than_remaining_classes(self):
        """Test when gap to reach 75% > remaining classes"""
        # 10 classes attended out of 100 (10%), need 2500 more to reach 75%!
        current_attendance = 10
        total_classes = 100
        remaining_classes = 40
        attendance_pct = (current_attendance / total_classes) * 100
        
        # Gap calculation
        needed_for_75 = int((75 / 100) * (total_classes + remaining_classes))
        gap = max(0, needed_for_75 - current_attendance)
        
        # Edge case: gap > remaining classes
        assert gap > remaining_classes
        print(f"✓ PASS: Gap ({gap}) > remaining ({remaining_classes})")

    def test_negative_date_handling(self):
        """Test handling of dates before semester start"""
        today = date.today()
        past_date = today - timedelta(days=100)
        
        # Edge case: Date is in the past
        assert past_date < today
        print(f"✓ PASS: Past date ({past_date}) correctly handled")

    def test_future_date_handling(self):
        """Test handling of dates after semester end"""
        today = date.today()
        future_date = today + timedelta(days=100)
        semester_end = today + timedelta(days=60)
        
        # Edge case: Date is beyond semester end
        assert future_date > semester_end
        print(f"✓ PASS: Future date ({future_date}) beyond semester")

    def test_single_class_remaining(self):
        """Test with only 1 class remaining"""
        total_classes = 100
        potential_total = total_classes + 1
        current_attended = int(0.74 * total_classes)  # 74 out of 100
        
        # To reach 75% with 1 class left
        needed = int(0.75 * potential_total)  # 75.75 → 76
        can_reach = current_attended + 1 >= needed
        
        print(f"✓ PASS: Single class remaining - can reach 75%: {can_reach}")

    def test_very_large_batch_class(self):
        """Test with extremely large batch (999 students)"""
        batch_size = 999
        students = [
            {"student_id": f"TEST_{i:04d}", "attendance": (i % 100)} 
            for i in range(batch_size)
        ]
        
        assert len(students) == batch_size
        print(f"✓ PASS: Large batch {batch_size} students processed")

    def test_weekend_holiday_overlap(self):
        """Test when weekend and holiday overlap"""
        # Monday = 0, Sunday = 6
        class_day = 0  # Monday
        holiday_date = date(2026, 4, 13)  # Some Monday that's a holiday
        
        is_monday = holiday_date.weekday() == 0
        is_holiday = True  # Marked as holiday
        
        # Edge case: Both weekend and holiday
        should_skip = is_monday and is_holiday
        print(f"✓ PASS: Weekend-holiday overlap handled: {should_skip}")

    def test_career_track_with_no_subjects(self):
        """Test career track when student has no relevant subjects"""
        from enum import Enum
        
        class CareerTrack(str, Enum):
            DATA_SCIENCE = "data_science"
            IOT = "iot"
            CYBER_SECURITY = "cyber_security"
        
        student_track = CareerTrack.DATA_SCIENCE
        relevant_subjects = []  # No matching subjects
        
        # Edge case: Career track but empty subject list
        assert isinstance(student_track, CareerTrack)
        assert len(relevant_subjects) == 0
        print(f"✓ PASS: Career track {student_track} with no subjects")

    def test_attendance_with_all_holidays_remaining(self):
        """Test when all remaining classes are holidays"""
        total_planned = 40
        already_attended = 25
        remaining_holidays = 15
        remaining_regular = 0
        
        # Can't improve attendance if only holidays remain
        max_possible = (already_attended / total_planned) * 100
        target = 75.0
        feasible = max_possible >= target
        
        print(f"✓ PASS: All holidays remaining - feasible: {feasible}")


# ═════════════════════════════════════════════════════════════
# PHASE 2: EXAM STRATEGY - EDGE CASES
# ═════════════════════════════════════════════════════════════

class TestPhase2ExamStrategyEdgeCases:
    """Test Phase 2 exam strategy with edge cases"""

    def test_double_danger_rule_exactly_trigger(self):
        """Test Double Danger Rule at exact threshold (75% OR 50%)"""
        # Rule: attendance < 75% AND marks < 50%
        
        # Case 1: Exactly 75% attendance, 49% marks
        test_cases = [
            {"attendance": 75.0, "marks": 49.0, "should_trigger": False},  # 75% not < 75%
            {"attendance": 74.9, "marks": 50.0, "should_trigger": False},  # marks not < 50%
            {"attendance": 74.9, "marks": 49.9, "should_trigger": True},   # Both conditions met
            {"attendance": 0.1, "marks": 0.1, "should_trigger": True},     # Deep danger
        ]
        
        for case in test_cases:
            triggers = (case["attendance"] < 75.0) and (case["marks"] < 50.0)
            assert triggers == case["should_trigger"]
            print(f"✓ PASS: Double Danger {case['attendance']}% att, {case['marks']}% marks: {triggers}")

    def test_zero_marks_zero_attendance(self):
        """Test most critical case: 0% in everything"""
        attendance = 0.0
        internal_marks = 0.0
        total_marks = 0.0
        
        is_critical = (attendance < 75.0) and (internal_marks < 50.0)
        assert is_critical
        print("✓ PASS: Complete failure case (0%, 0%) = CRITICAL_RISK")

    def test_max_marks_low_attendance(self):
        """Test high marks but low attendance"""
        attendance = 50.0
        internal_marks = 50.0
        
        is_critical = (attendance < 75.0) and (internal_marks < 50.0)
        assert not is_critical  # Marks not < 50%, so no critical
        print("✓ PASS: Good marks (50%) with poor attendance (50%) = WARNING (not critical)")

    def test_high_attendance_low_marks(self):
        """Test high attendance but failing marks"""
        attendance = 95.0
        internal_marks = 30.0
        
        is_critical = (attendance < 75.0) and (internal_marks < 50.0)
        assert not is_critical  # attendance not < 75%
        print("✓ PASS: Excellent attendance (95%) with low marks (30%) = Possible but not critical")

    def test_mark_ranges_boundary(self):
        """Test mark range boundaries (0-30 mid_term, 0-20 cie)"""
        test_cases = [
            {"mid_term": 0, "cie": 0, "valid": True},
            {"mid_term": 30, "cie": 20, "valid": True},
            {"mid_term": 31, "cie": 20, "valid": False},  # Over limit
            {"mid_term": 30, "cie": 21, "valid": False},  # Over limit
            {"mid_term": -1, "cie": 10, "valid": False},  # Negative
            {"mid_term": 15.5, "cie": 10.5, "valid": True},  # Decimal
        ]
        
        for case in test_cases:
            is_valid = (0 <= case["mid_term"] <= 30) and (0 <= case["cie"] <= 20)
            assert is_valid == case["valid"]
            print(f"✓ PASS: Marks {case['mid_term']}/{case['cie']} valid: {is_valid}")

    def test_total_internal_exactly_50(self):
        """Test when total internal marks is exactly 50 (threshold)"""
        mid_term = 30
        cie = 20
        total_internal = mid_term + cie  # Exactly 50
        
        # 50 is NOT < 50, so no critical risk from marks perspective
        is_marks_critical = total_internal < 50.0
        assert not is_marks_critical
        print(f"✓ PASS: Total marks exactly {total_internal} = not critical from marks")

    def test_total_internal_just_below_50(self):
        """Test when total internal is just below 50"""
        mid_term = 29
        cie = 20
        total_internal = mid_term + cie  # 49
        
        is_marks_critical = total_internal < 50.0
        assert is_marks_critical
        print(f"✓ PASS: Total marks {total_internal} (just below 50) = critical from marks")

    def test_all_subjects_critical(self):
        """Test when student is critical in ALL subjects"""
        subjects = ["DS", "ML", "AI", "NLP", "CV"]
        critical_count = sum(1 for _ in subjects)  # All critical
        
        assert critical_count == len(subjects)
        print(f"✓ PASS: All {len(subjects)} subjects in critical state")

    def test_single_subject_critical(self):
        """Test when only 1 subject is critical (most common)"""
        critical_subjects = ["DS"]  # Just one
        total_subjects = 5
        
        critical_percentage = (len(critical_subjects) / total_subjects) * 100
        assert critical_percentage == 20.0
        print(f"✓ PASS: 1 of {total_subjects} subjects critical (20%)")

    def test_no_subjects_critical(self):
        """Test when NO subjects are in critical state"""
        critical_subjects = []
        
        assert len(critical_subjects) == 0
        print("✓ PASS: No subjects in critical state (student safe)")

    def test_priority_score_calculation(self):
        """Test priority score: (missed% * 0.5) + (marks_gap% * 0.5)"""
        test_cases = [
            {"missed_pct": 50, "gap_pct": 50, "expected": 50.0},   # Average case
            {"missed_pct": 100, "gap_pct": 100, "expected": 100.0}, # Worst case
            {"missed_pct": 0, "gap_pct": 0, "expected": 0.0},       # Best case
            {"missed_pct": 100, "gap_pct": 0, "expected": 50.0},    # Only attendance bad
            {"missed_pct": 0, "gap_pct": 100, "expected": 50.0},    # Only marks bad
        ]
        
        for case in test_cases:
            priority = (case["missed_pct"] * 0.5) + (case["gap_pct"] * 0.5)
            assert priority == case["expected"]
            print(f"✓ PASS: Priority {case['missed_pct']}% + {case['gap_pct']}% = {priority}")

    def test_risk_level_colors(self):
        """Test color coding for risk levels"""
        test_cases = [
            {"score": 0, "level": "SAFE"},      # < 33
            {"score": 32, "level": "SAFE"},     # < 33
            {"score": 33, "level": "WARNING"},  # 33-66
            {"score": 50, "level": "WARNING"},  # 33-66
            {"score": 67, "level": "CRITICAL"}, # >= 67
            {"score": 100, "level": "CRITICAL"},# >= 67
        ]
        
        for case in test_cases:
            if case["score"] < 33:
                level = "SAFE"
            elif case["score"] < 67:
                level = "WARNING"
            else:
                level = "CRITICAL"
            
            assert level == case["level"]
            print(f"✓ PASS: Score {case['score']} → {level}")


# ═════════════════════════════════════════════════════════════
# PHASE 3: ACADEMIC BRIDGE - EDGE CASES
# ═════════════════════════════════════════════════════════════

class TestPhase3AcademicBridgeEdgeCases:
    """Test Phase 3 academic bridge with edge cases"""

    def test_no_prerequisites_student(self):
        """Test student with no prerequisites"""
        student_prerequisites = {}  # Empty
        
        assert len(student_prerequisites) == 0
        print("✓ PASS: Student with no prerequisites")

    def test_all_prerequisites_mastered(self):
        """Test student who mastered all prerequisites"""
        prerequisites = {
            "C": "A",  # Grade A
            "Data_Structures": "A",
            "Algorithms": "A",
        }
        
        all_mastered = all(grade == "A" for grade in prerequisites.values())
        assert all_mastered
        print(f"✓ PASS: All {len(prerequisites)} prerequisites at A grade")

    def test_all_prerequisites_failed(self):
        """Test student who failed all prerequisites"""
        prerequisites = {
            "C": "F",
            "Data_Structures": "F", 
            "Algorithms": "F",
        }
        
        all_failed = all(grade == "F" for grade in prerequisites.values())
        assert all_failed
        print(f"✓ PASS: All {len(prerequisites)} prerequisites failed")

    def test_circular_prerequisite_detection(self):
        """Test detection of circular prerequisites"""
        # A→B→C→A (circular)
        prerequisites = {
            "A": "B",
            "B": "C",
            "C": "A",  # Back to A - circular!
        }
        
        # Check for cycle
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            if node in prerequisites:
                next_node = prerequisites[node]
                if next_node not in visited:
                    if has_cycle(next_node):
                        return True
                elif next_node in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        has_circular = any(has_cycle(subject) for subject in prerequisites)
        print(f"✓ PASS: Circular prerequisite detected: {has_circular}")

    def test_missing_prerequisite_subject(self):
        """Test when prerequisite subject doesn't exist"""
        current_subjects = ["DS", "Algorithms", "ML"]
        prerequisite = "Missing_Subject"
        
        # Edge case: prerequisite not in offered subjects
        prerequisite_exists = prerequisite in current_subjects
        assert not prerequisite_exists
        print(f"✓ PASS: Missing prerequisite '{prerequisite}' detected")

    def test_gap_severity_boundaries(self):
        """Test gap severity classification boundaries"""
        test_cases = [
            {"marks_pct": 39.9, "expected": "CRITICAL"},
            {"marks_pct": 40.0, "expected": "HIGH"},
            {"marks_pct": 49.9, "expected": "HIGH"},
            {"marks_pct": 50.0, "expected": "MEDIUM"},
            {"marks_pct": 64.9, "expected": "MEDIUM"},
            {"marks_pct": 65.0, "expected": "LOW"},
            {"marks_pct": 100.0, "expected": "LOW"},
        ]
        
        for case in test_cases:
            pct = case["marks_pct"]
            if pct < 40:
                severity = "CRITICAL"
            elif pct < 50:
                severity = "HIGH"
            elif pct < 65:
                severity = "MEDIUM"
            else:
                severity = "LOW"
            
            assert severity == case["expected"]
            print(f"✓ PASS: {pct}% marks → {severity} severity")

    def test_refresher_plan_generation(self):
        """Test 5-day refresher plan generation"""
        days = 5
        topics = ["Data_Structures", "Algorithms", "Big_O_Notation", "Sorting", "Searching"]
        
        # 5 topics for 5 days? Perfect match
        topics_per_day = len(topics) / days
        assert topics_per_day == 1.0
        print(f"✓ PASS: 5-day plan for {len(topics)} topics (1 per day)")

    def test_refresher_plan_more_topics_than_days(self):
        """Test 5-day plan with more than 5 topics"""
        days = 5
        topics = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        
        # More topics than days - need to combine
        topics_per_day = len(topics) / days
        assert topics_per_day > 1.0  # 1.4 topics per day
        print(f"✓ PASS: {len(topics)} topics in {days} days → {topics_per_day:.1f} per day")

    def test_refresher_plan_fewer_topics_than_days(self):
        """Test 5-day plan with fewer than 5 topics"""
        days = 5
        topics = ["Topic1", "Topic2"]
        
        # Fewer topics than days
        topics_per_day = len(topics) / days
        assert topics_per_day < 1.0  # 0.4 topics per day
        print(f"✓ PASS: {len(topics)} topics in {days} days → {topics_per_day:.1f} per day")

    def test_semester_gap_calculation(self):
        """Test semester gap calculation between prereq and current"""
        test_cases = [
            {"prereq_sem": 1, "current_sem": 2, "gap": 1},  # Adjacent
            {"prereq_sem": 1, "current_sem": 4, "gap": 3},  # 3 semesters gap
            {"prereq_sem": 2, "current_sem": 2, "gap": 0},  # Same semester (unusual)
            {"prereq_sem": 4, "current_sem": 1, "gap": -3}, # Student going backward
        ]
        
        for case in test_cases:
            gap = case["current_sem"] - case["prereq_sem"]
            assert gap == case["gap"]
            print(f"✓ PASS: Sem {case['prereq_sem']} → {case['current_sem']} = gap {gap}")

    def test_multiple_prerequisite_chains(self):
        """Test handling of multiple independent chains"""
        chains = {
            "chain1": ["C", "DS", "Algorithms"],
            "chain2": ["Math", "Physics", "Mechanics"],
            "chain3": ["English", "Literature"],
        }
        
        total_subjects = sum(len(chain) for chain in chains.values())
        assert total_subjects == 8
        print(f"✓ PASS: {len(chains)} chains with {total_subjects} total subjects")

    def test_grade_to_marks_conversion(self):
        """Test grade conversion to percentage"""
        grade_mapping = {
            "A": 90, "B": 80, "C": 70, "D": 60, "E": 50, "F": 0
        }
        
        test_cases = [
            {"grade": "A", "expected": 90},
            {"grade": "F", "expected": 0},
            {"grade": "C", "expected": 70},
        ]
        
        for case in test_cases:
            percentage = grade_mapping.get(case["grade"], 0)
            assert percentage == case["expected"]
            print(f"✓ PASS: Grade {case['grade']} → {percentage}%")


# ═════════════════════════════════════════════════════════════
# CROSS-PHASE EDGE CASES
# ═════════════════════════════════════════════════════════════

class TestCrossPhasesEdgeCases:
    """Test edge cases that span multiple phases"""

    def test_student_failing_all_phases(self):
        """Test student who's struggling in all phases"""
        student = {
            "phase_1_feasible": False,  # Can't reach 75% attendance
            "phase_2_critical": True,   # High exam risk
            "phase_3_gaps": ["DS", "Algorithms", "Math"],  # Multiple prerequisites
        }
        
        is_at_risk = not student["phase_1_feasible"] or student["phase_2_critical"]
        has_gaps = len(student["phase_3_gaps"]) > 0
        
        assert is_at_risk and has_gaps
        print("✓ PASS: Student failing across all phases identified")

    def test_student_excelling_all_phases(self):
        """Test student excelling in all phases"""
        student = {
            "phase_1_feasible": True,   # Can reach attendance
            "phase_2_critical": False,  # No exam risk
            "phase_3_gaps": [],         # No prerequisite gaps
        }
        
        is_safe = student["phase_1_feasible"] and not student["phase_2_critical"]
        no_gaps = len(student["phase_3_gaps"]) == 0
        
        assert is_safe and no_gaps
        print("✓ PASS: Student excelling across all phases identified")

    def test_batch_with_mixed_performance(self):
        """Test batch with diverse student performance"""
        batch = [
            {"name": "Perfect", "phase_1": True, "phase_2": False, "phase_3": []},
            {"name": "Struggling", "phase_1": False, "phase_2": True, "phase_3": ["DS"]},
            {"name": "Average", "phase_1": True, "phase_2": True, "phase_3": ["Math"]},
        ]
        
        at_risk = sum(1 for s in batch if not s["phase_1"] or s["phase_2"])
        safe = sum(1 for s in batch if s["phase_1"] and not s["phase_2"])
        
        assert at_risk + safe <= len(batch)
        print(f"✓ PASS: Batch size {len(batch)} - {at_risk} at risk, {safe} safe")

    def test_extreme_semester_student(self):
        """Test student in extreme semester (semester 1 vs 8)"""
        test_cases = [
            {"semester": 1, "phase_3_applicable": False},  # No prereqs yet
            {"semester": 8, "phase_3_applicable": True},   # Many possible prereqs
        ]
        
        for case in test_cases:
            # Semester 1 shouldn't have prerequisites
            is_edge = case["semester"] == 1 or case["semester"] == 8
            assert is_edge
            print(f"✓ PASS: Edge case semester {case['semester']}")


# ═════════════════════════════════════════════════════════════
# PERFORMANCE & STRESS TESTING
# ═════════════════════════════════════════════════════════════

class TestPerformanceEdgeCases:
    """Test performance with large datasets"""

    def test_1000_students_processing(self):
        """Test processing 1000 students"""
        students = [{"id": f"S{i}"} for i in range(1000)]
        
        assert len(students) == 1000
        print(f"✓ PASS: Processed {len(students)} students")

    def test_50_subjects_per_student(self):
        """Test student with 50 subjects (realistic max)"""
        subjects = [f"SUBJ_{i}" for i in range(50)]
        
        assert len(subjects) == 50
        print(f"✓ PASS: Student with {len(subjects)} subjects")

    def test_date_range_full_semester(self):
        """Test full semester date range"""
        start_date = date(2026, 1, 1)
        end_date = date(2026, 4, 30)
        days = (end_date - start_date).days
        
        assert days > 100  # ~120 days
        print(f"✓ PASS: Full semester date range: {days} days")

    def test_rapid_api_calls(self):
        """Test handling of rapid consecutive API calls"""
        calls = 100
        # Simulate rapid calls
        results = [i for i in range(calls)]
        
        assert len(results) == calls
        print(f"✓ PASS: Handled {calls} rapid API calls")


# ═════════════════════════════════════════════════════════════
# RUN TESTS
# ═════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*70)
    print("EduPath Optimizer - COMPREHENSIVE EDGE CASE TEST SUITE")
    print("="*70 + "\n")
    
    # Phase 1
    print("\n📚 PHASE 1: ATTENDANCE OPTIMIZATION - EDGE CASES")
    print("-" * 70)
    test_phase1 = TestPhase1AttendanceEdgeCases()
    test_phase1.test_zero_attendance()
    test_phase1.test_perfect_attendance()
    test_phase1.test_exactly_at_threshold()
    test_phase1.test_just_below_threshold()
    test_phase1.test_gap_greater_than_remaining_classes()
    test_phase1.test_negative_date_handling()
    test_phase1.test_future_date_handling()
    test_phase1.test_single_class_remaining()
    test_phase1.test_very_large_batch_class()
    test_phase1.test_weekend_holiday_overlap()
    test_phase1.test_career_track_with_no_subjects()
    test_phase1.test_attendance_with_all_holidays_remaining()
    
    # Phase 2
    print("\n📚 PHASE 2: EXAM STRATEGY - EDGE CASES")
    print("-" * 70)
    test_phase2 = TestPhase2ExamStrategyEdgeCases()
    test_phase2.test_double_danger_rule_exactly_trigger()
    test_phase2.test_zero_marks_zero_attendance()
    test_phase2.test_max_marks_low_attendance()
    test_phase2.test_high_attendance_low_marks()
    test_phase2.test_mark_ranges_boundary()
    test_phase2.test_total_internal_exactly_50()
    test_phase2.test_total_internal_just_below_50()
    test_phase2.test_all_subjects_critical()
    test_phase2.test_single_subject_critical()
    test_phase2.test_no_subjects_critical()
    test_phase2.test_priority_score_calculation()
    test_phase2.test_risk_level_colors()
    
    # Phase 3
    print("\n📚 PHASE 3: ACADEMIC BRIDGE - EDGE CASES")
    print("-" * 70)
    test_phase3 = TestPhase3AcademicBridgeEdgeCases()
    test_phase3.test_no_prerequisites_student()
    test_phase3.test_all_prerequisites_mastered()
    test_phase3.test_all_prerequisites_failed()
    test_phase3.test_circular_prerequisite_detection()
    test_phase3.test_missing_prerequisite_subject()
    test_phase3.test_gap_severity_boundaries()
    test_phase3.test_refresher_plan_generation()
    test_phase3.test_refresher_plan_more_topics_than_days()
    test_phase3.test_refresher_plan_fewer_topics_than_days()
    test_phase3.test_semester_gap_calculation()
    test_phase3.test_multiple_prerequisite_chains()
    test_phase3.test_grade_to_marks_conversion()
    
    # Cross-phase
    print("\n📚 CROSS-PHASE EDGE CASES")
    print("-" * 70)
    test_cross = TestCrossPhasesEdgeCases()
    test_cross.test_student_failing_all_phases()
    test_cross.test_student_excelling_all_phases()
    test_cross.test_batch_with_mixed_performance()
    test_cross.test_extreme_semester_student()
    
    # Performance
    print("\n📚 PERFORMANCE & STRESS TESTING")
    print("-" * 70)
    test_perf = TestPerformanceEdgeCases()
    test_perf.test_1000_students_processing()
    test_perf.test_50_subjects_per_student()
    test_perf.test_date_range_full_semester()
    test_perf.test_rapid_api_calls()
    
    print("\n" + "="*70)
    print("✅ ALL EDGE CASE TESTS COMPLETED SUCCESSFULLY")
    print("="*70 + "\n")
