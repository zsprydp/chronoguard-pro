import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class TimeSlot:
    start_time: datetime
    end_time: datetime
    provider_id: str
    appointments: List[Dict]
    capacity: int = 1
    buffer_minutes: int = 0


@dataclass
class OptimizationResult:
    original_schedule: Dict
    optimized_schedule: Dict
    changes: List[Dict]
    predicted_revenue_gain: float
    optimization_score: float
    recommendations: List[str]


class ScheduleOptimizer:
    """
    Advanced schedule optimization engine using constraint programming
    and revenue maximization algorithms
    """
    
    def __init__(self, practice_settings: Dict):
        self.max_overbook_percentage = practice_settings.get('max_overbook_percentage', 0.15)
        self.min_no_show_threshold = practice_settings.get('min_no_show_threshold', 0.10)
        self.buffer_time_minutes = practice_settings.get('buffer_time_minutes', 5)
        self.optimization_strategy = practice_settings.get('strategy', 'balanced')
        
    def optimize_daily_schedule(
        self,
        appointments: List[Dict],
        no_show_predictions: Dict[str, float],
        provider_schedules: Dict[str, Dict]
    ) -> OptimizationResult:
        """
        Optimize a daily schedule based on no-show predictions
        """
        logger.info(f"Optimizing schedule for {len(appointments)} appointments")
        
        # Group appointments by provider and time slot
        time_slots = self._create_time_slots(appointments, provider_schedules)
        
        # Calculate optimal overbooking for each slot
        optimized_slots = self._optimize_time_slots(time_slots, no_show_predictions)
        
        # Generate schedule changes
        changes = self._generate_schedule_changes(time_slots, optimized_slots)
        
        # Calculate metrics
        revenue_gain = self._calculate_revenue_impact(time_slots, optimized_slots)
        optimization_score = self._calculate_optimization_score(optimized_slots)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(optimized_slots, no_show_predictions)
        
        return OptimizationResult(
            original_schedule=self._slots_to_dict(time_slots),
            optimized_schedule=self._slots_to_dict(optimized_slots),
            changes=changes,
            predicted_revenue_gain=revenue_gain,
            optimization_score=optimization_score,
            recommendations=recommendations
        )
    
    def _create_time_slots(
        self,
        appointments: List[Dict],
        provider_schedules: Dict[str, Dict]
    ) -> List[TimeSlot]:
        """
        Create time slots from appointments and provider schedules
        """
        slots = []
        
        for provider_id, schedule in provider_schedules.items():
            # Parse provider working hours
            start_time = datetime.strptime(schedule['start'], '%H:%M')
            end_time = datetime.strptime(schedule['end'], '%H:%M')
            slot_duration = schedule.get('slot_duration', 30)
            
            # Create slots for the day
            current_time = start_time
            while current_time < end_time:
                slot_end = current_time + timedelta(minutes=slot_duration)
                
                # Find appointments in this slot
                slot_appointments = [
                    apt for apt in appointments
                    if apt['provider_id'] == provider_id
                    and apt['scheduled_time'] >= current_time
                    and apt['scheduled_time'] < slot_end
                ]
                
                slots.append(TimeSlot(
                    start_time=current_time,
                    end_time=slot_end,
                    provider_id=provider_id,
                    appointments=slot_appointments,
                    capacity=1,
                    buffer_minutes=self.buffer_time_minutes
                ))
                
                current_time = slot_end
        
        return slots
    
    def _optimize_time_slots(
        self,
        time_slots: List[TimeSlot],
        no_show_predictions: Dict[str, float]
    ) -> List[TimeSlot]:
        """
        Optimize each time slot based on no-show predictions
        """
        optimized_slots = []
        
        for slot in time_slots:
            # Calculate expected no-shows in this slot
            expected_no_shows = sum(
                no_show_predictions.get(apt['id'], 0.1)
                for apt in slot.appointments
            )
            
            # Determine optimal capacity
            if expected_no_shows >= self.min_no_show_threshold:
                # Calculate safe overbooking level
                overbook_count = self._calculate_overbook_count(
                    slot,
                    expected_no_shows,
                    no_show_predictions
                )
                
                # Create optimized slot
                optimized_slot = TimeSlot(
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    provider_id=slot.provider_id,
                    appointments=slot.appointments,
                    capacity=slot.capacity + overbook_count,
                    buffer_minutes=slot.buffer_minutes
                )
            else:
                optimized_slot = slot
            
            optimized_slots.append(optimized_slot)
        
        return optimized_slots
    
    def _calculate_overbook_count(
        self,
        slot: TimeSlot,
        expected_no_shows: float,
        no_show_predictions: Dict[str, float]
    ) -> int:
        """
        Calculate safe overbooking count for a slot
        """
        if self.optimization_strategy == 'aggressive':
            # More aggressive overbooking for higher revenue
            overbook_factor = 1.2
        elif self.optimization_strategy == 'conservative':
            # Conservative approach to minimize wait times
            overbook_factor = 0.8
        else:  # balanced
            overbook_factor = 1.0
        
        # Base calculation
        base_overbook = int(expected_no_shows * overbook_factor)
        
        # Apply maximum constraint
        max_overbook = int(len(slot.appointments) * self.max_overbook_percentage)
        
        # Consider slot criticality (morning/evening slots might be more critical)
        hour = slot.start_time.hour
        if hour < 10 or hour > 16:
            # Reduce overbooking for edge hours
            base_overbook = int(base_overbook * 0.7)
        
        return min(base_overbook, max_overbook)
    
    def _generate_schedule_changes(
        self,
        original: List[TimeSlot],
        optimized: List[TimeSlot]
    ) -> List[Dict]:
        """
        Generate list of specific changes between original and optimized schedules
        """
        changes = []
        
        for orig_slot, opt_slot in zip(original, optimized):
            if opt_slot.capacity > orig_slot.capacity:
                changes.append({
                    'type': 'overbook_added',
                    'time_slot': orig_slot.start_time.isoformat(),
                    'provider_id': orig_slot.provider_id,
                    'additional_capacity': opt_slot.capacity - orig_slot.capacity,
                    'reason': 'High no-show probability detected'
                })
            
            # Check for suggested buffer adjustments
            if opt_slot.buffer_minutes != orig_slot.buffer_minutes:
                changes.append({
                    'type': 'buffer_adjusted',
                    'time_slot': orig_slot.start_time.isoformat(),
                    'provider_id': orig_slot.provider_id,
                    'new_buffer': opt_slot.buffer_minutes,
                    'old_buffer': orig_slot.buffer_minutes
                })
        
        return changes
    
    def _calculate_revenue_impact(
        self,
        original: List[TimeSlot],
        optimized: List[TimeSlot]
    ) -> float:
        """
        Calculate predicted revenue gain from optimization
        """
        # Average appointment value (this should come from practice data)
        avg_appointment_value = 150.0
        
        # Calculate additional capacity
        original_capacity = sum(slot.capacity for slot in original)
        optimized_capacity = sum(slot.capacity for slot in optimized)
        additional_slots = optimized_capacity - original_capacity
        
        # Estimate fill rate for additional slots
        fill_rate = 0.7  # Assume 70% of overbooked slots will be filled
        
        # Calculate revenue gain
        revenue_gain = additional_slots * avg_appointment_value * fill_rate
        
        return revenue_gain
    
    def _calculate_optimization_score(self, optimized_slots: List[TimeSlot]) -> float:
        """
        Calculate overall optimization quality score
        """
        scores = []
        
        for slot in optimized_slots:
            # Utilization score
            utilization = len(slot.appointments) / max(slot.capacity, 1)
            utilization_score = min(utilization, 1.0)
            
            # Balance score (avoid too much overbooking)
            overbook_ratio = (slot.capacity - 1) / max(len(slot.appointments), 1)
            balance_score = 1.0 - min(overbook_ratio, 1.0)
            
            # Combined score
            slot_score = (utilization_score * 0.6 + balance_score * 0.4)
            scores.append(slot_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _generate_recommendations(
        self,
        optimized_slots: List[TimeSlot],
        no_show_predictions: Dict[str, float]
    ) -> List[str]:
        """
        Generate actionable recommendations
        """
        recommendations = []
        
        # Find high-risk patients
        high_risk_patients = [
            apt_id for apt_id, prob in no_show_predictions.items()
            if prob > 0.4
        ]
        
        if high_risk_patients:
            recommendations.append(
                f"Send additional reminders to {len(high_risk_patients)} high-risk patients"
            )
        
        # Check for underutilized slots
        underutilized = [
            slot for slot in optimized_slots
            if len(slot.appointments) == 0
        ]
        
        if underutilized:
            recommendations.append(
                f"Consider opening {len(underutilized)} empty slots for same-day bookings"
            )
        
        # Suggest optimal reminder timing
        morning_slots = [
            slot for slot in optimized_slots
            if slot.start_time.hour < 12
        ]
        
        if morning_slots:
            recommendations.append(
                "Send morning appointment reminders by 6 PM the day before"
            )
        
        return recommendations
    
    def _slots_to_dict(self, slots: List[TimeSlot]) -> Dict:
        """
        Convert time slots to dictionary format
        """
        schedule = defaultdict(list)
        
        for slot in slots:
            schedule[slot.provider_id].append({
                'start_time': slot.start_time.isoformat(),
                'end_time': slot.end_time.isoformat(),
                'appointments': slot.appointments,
                'capacity': slot.capacity,
                'buffer_minutes': slot.buffer_minutes
            })
        
        return dict(schedule)
    
    def suggest_reschedule(
        self,
        cancelled_appointment: Dict,
        available_slots: List[TimeSlot],
        patient_preferences: Dict
    ) -> List[Dict]:
        """
        Suggest optimal reschedule times for a cancelled appointment
        """
        suggestions = []
        
        # Patient's preferred times
        preferred_hours = patient_preferences.get('preferred_hours', [9, 10, 11, 14, 15])
        preferred_days = patient_preferences.get('preferred_days', [1, 2, 3, 4, 5])
        
        for slot in available_slots:
            if len(slot.appointments) < slot.capacity:
                # Calculate score for this slot
                score = 0
                
                # Time preference score
                if slot.start_time.hour in preferred_hours:
                    score += 2
                
                # Day preference score
                if slot.start_time.weekday() in preferred_days:
                    score += 1
                
                # Availability score (prefer less crowded slots)
                occupancy = len(slot.appointments) / slot.capacity
                score += (1 - occupancy) * 1.5
                
                suggestions.append({
                    'slot': slot,
                    'time': slot.start_time,
                    'score': score,
                    'provider_id': slot.provider_id
                })
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        return [{
            'time': s['time'].isoformat(),
            'provider_id': s['provider_id'],
            'confidence': s['score'] / 5.0  # Normalize to 0-1
        } for s in suggestions[:3]]