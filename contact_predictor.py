import time
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os

class SmartContactPredictor:
    """
    Intelligent contact prediction system based on:
    - Time of day patterns
    - Day of week patterns
    - Call frequency and recency
    - Location context (if available)
    - Call duration patterns
    """
    
    def __init__(self, data_file='contact_patterns.json'):
        self.data_file = data_file
        self.call_history = defaultdict(list)  # {contact: [(timestamp, duration, context), ...]}
        self.time_patterns = defaultdict(lambda: defaultdict(int))  # {contact: {hour: count}}
        self.day_patterns = defaultdict(lambda: defaultdict(int))  # {contact: {weekday: count}}
        self.location_patterns = defaultdict(lambda: defaultdict(int))  # {contact: {location: count}}
        
        self.load_patterns()
    
    def load_patterns(self):
        """Load historical patterns from disk"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.call_history = defaultdict(list, data.get('history', {}))
                    self.time_patterns = defaultdict(lambda: defaultdict(int), data.get('time', {}))
                    self.day_patterns = defaultdict(lambda: defaultdict(int), data.get('day', {}))
                    self.location_patterns = defaultdict(lambda: defaultdict(int), data.get('location', {}))
            except Exception as e:
                print(f"Warning: Could not load patterns: {e}")
    
    def save_patterns(self):
        """Save patterns to disk"""
        try:
            data = {
                'history': dict(self.call_history),
                'time': {k: dict(v) for k, v in self.time_patterns.items()},
                'day': {k: dict(v) for k, v in self.day_patterns.items()},
                'location': {k: dict(v) for k, v in self.location_patterns.items()}
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save patterns: {e}")
    
    def log_call(self, contact, duration=0, location=None):
        """Log a call event to build patterns"""
        now = time.time()
        dt = datetime.fromtimestamp(now)
        
        # Record call
        self.call_history[contact].append({
            'timestamp': now,
            'duration': duration,
            'location': location,
            'hour': dt.hour,
            'weekday': dt.weekday()
        })
        
        # Update patterns
        self.time_patterns[contact][dt.hour] += 1
        self.day_patterns[contact][dt.weekday()] += 1
        if location:
            self.location_patterns[contact][location] += 1
        
        # Limit history size
        if len(self.call_history[contact]) > 100:
            self.call_history[contact] = self.call_history[contact][-100:]
        
        self.save_patterns()
    
    def calculate_recency_score(self, contact):
        """Score based on how recently contact was called"""
        if contact not in self.call_history or not self.call_history[contact]:
            return 0.0
        
        calls = self.call_history[contact]
        most_recent = max(call['timestamp'] for call in calls)
        
        # Decay function: more recent = higher score
        hours_ago = (time.time() - most_recent) / 3600
        if hours_ago < 1:
            return 1.0
        elif hours_ago < 24:
            return 0.8
        elif hours_ago < 168:  # 1 week
            return 0.5
        else:
            return 0.2
    
    def calculate_frequency_score(self, contact):
        """Score based on call frequency"""
        if contact not in self.call_history:
            return 0.0
        
        calls = self.call_history[contact]
        
        # Recent frequency (last 30 days)
        thirty_days_ago = time.time() - (30 * 24 * 3600)
        recent_calls = [c for c in calls if c['timestamp'] > thirty_days_ago]
        
        if not recent_calls:
            return 0.0
        
        # Normalize: cap at 10 calls/month = score 1.0
        return min(1.0, len(recent_calls) / 10.0)
    
    def calculate_time_pattern_score(self, contact):
        """Score based on time-of-day patterns"""
        if contact not in self.time_patterns:
            return 0.0
        
        current_hour = datetime.now().hour
        patterns = self.time_patterns[contact]
        
        if not patterns:
            return 0.0
        
        # Check current hour and adjacent hours
        score = 0.0
        for offset in [-1, 0, 1]:
            hour = (current_hour + offset) % 24
            score += patterns.get(hour, 0)
        
        # Normalize by total calls
        total_calls = sum(patterns.values())
        return score / total_calls if total_calls > 0 else 0.0
    
    def calculate_day_pattern_score(self, contact):
        """Score based on day-of-week patterns"""
        if contact not in self.day_patterns:
            return 0.0
        
        current_day = datetime.now().weekday()
        patterns = self.day_patterns[contact]
        
        if not patterns:
            return 0.0
        
        day_score = patterns.get(current_day, 0)
        total_calls = sum(patterns.values())
        
        return day_score / total_calls if total_calls > 0 else 0.0
    
    def calculate_location_score(self, contact, current_location=None):
        """Score based on location patterns"""
        if not current_location or contact not in self.location_patterns:
            return 0.0
        
        patterns = self.location_patterns[contact]
        location_calls = patterns.get(current_location, 0)
        total_calls = sum(patterns.values())
        
        return location_calls / total_calls if total_calls > 0 else 0.0
    
    def calculate_duration_score(self, contact):
        """Score based on call duration (longer calls = more important contact)"""
        if contact not in self.call_history:
            return 0.0
        
        calls = self.call_history[contact]
        if not calls:
            return 0.0
        
        avg_duration = sum(c['duration'] for c in calls) / len(calls)
        
        # Normalize: 5+ minute calls = score 1.0
        return min(1.0, avg_duration / 300.0)
    
    def predict_top_contacts(self, n=10, current_location=None, favorites=None):
        """
        Predict the most likely contacts to be called right now
        
        Returns: List of (contact, score, breakdown) tuples
        """
        if favorites is None:
            favorites = []
        
        all_contacts = set(self.call_history.keys())
        scores = []
        
        for contact in all_contacts:
            # Calculate component scores
            recency = self.calculate_recency_score(contact)
            frequency = self.calculate_frequency_score(contact)
            time_pattern = self.calculate_time_pattern_score(contact)
            day_pattern = self.calculate_day_pattern_score(contact)
            location = self.calculate_location_score(contact, current_location)
            duration = self.calculate_duration_score(contact)
            
            # Weighted combination
            weights = {
                'recency': 0.25,
                'frequency': 0.20,
                'time_pattern': 0.20,
                'day_pattern': 0.15,
                'location': 0.10,
                'duration': 0.10
            }
            
            final_score = (
                recency * weights['recency'] +
                frequency * weights['frequency'] +
                time_pattern * weights['time_pattern'] +
                day_pattern * weights['day_pattern'] +
                location * weights['location'] +
                duration * weights['duration']
            )
            
            # Boost favorites
            if contact in favorites:
                final_score *= 1.5
            
            breakdown = {
                'recency': recency,
                'frequency': frequency,
                'time_pattern': time_pattern,
                'day_pattern': day_pattern,
                'location': location,
                'duration': duration
            }
            
            scores.append((contact, final_score, breakdown))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:n]
    
    def get_statistics(self, contact):
        """Get detailed statistics for a contact"""
        if contact not in self.call_history:
            return None
        
        calls = self.call_history[contact]
        
        return {
            'total_calls': len(calls),
            'avg_duration': sum(c['duration'] for c in calls) / len(calls),
            'most_common_hour': max(self.time_patterns[contact].items(), 
                                   key=lambda x: x[1])[0] if self.time_patterns[contact] else None,
            'most_common_day': max(self.day_patterns[contact].items(),
                                  key=lambda x: x[1])[0] if self.day_patterns[contact] else None,
            'last_call': max(c['timestamp'] for c in calls)
        }
    
    def explain_prediction(self, contact):
        """Generate human-readable explanation of why a contact is suggested"""
        if contact not in self.call_history:
            return "No history available"
        
        stats = self.get_statistics(contact)
        explanations = []
        
        # Recency
        hours_ago = (time.time() - stats['last_call']) / 3600
        if hours_ago < 24:
            explanations.append(f"Called recently ({int(hours_ago)}h ago)")
        
        # Frequency
        if stats['total_calls'] > 10:
            explanations.append(f"Frequently called ({stats['total_calls']} times)")
        
        # Time pattern
        current_hour = datetime.now().hour
        if stats['most_common_hour'] is not None:
            if abs(current_hour - stats['most_common_hour']) <= 1:
                explanations.append(f"Usually called around this time")
        
        # Day pattern
        current_day = datetime.now().weekday()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if stats['most_common_day'] == current_day:
            explanations.append(f"Often called on {days[current_day]}s")
        
        return " • ".join(explanations) if explanations else "Based on your history"


# Example usage and testing
if __name__ == "__main__":
    predictor = SmartContactPredictor('test_patterns.json')
    
    # Simulate some call history
    print("Simulating call patterns...")
    
    # Morning work calls
    for i in range(5):
        predictor.log_call("Boss", duration=300, location="office")
    
    # Evening friend calls
    for i in range(8):
        predictor.log_call("Best Friend", duration=1200, location="home")
    
    # Occasional family calls
    for i in range(3):
        predictor.log_call("Mom", duration=600, location="home")
    
    print("\nPredicting top contacts:")
    predictions = predictor.predict_top_contacts(n=5, current_location="home", 
                                                 favorites=["Mom"])
    
    for contact, score, breakdown in predictions:
        print(f"\n{contact}: {score:.3f}")
        print(f"  {predictor.explain_prediction(contact)}")
        print(f"  Breakdown: {breakdown}")
