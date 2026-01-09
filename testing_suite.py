"""
Performance testing and metrics collection for gesture recognition system
Run this to evaluate system performance against project requirements
"""

import time
import json
from datetime import datetime
from collections import defaultdict
import numpy as np

def numpy_converter(obj):
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

class GestureMetricsCollector:
    """Collects and analyzes gesture recognition performance"""
    
    def __init__(self):
        self.metrics = {
            'detections': [],
            'false_positives': [],
            'latencies': [],
            'confidence_scores': [],
            'gesture_types': defaultdict(int),
            'errors': [],
            'session_start': time.time()
        }
        
        self.requirements = {
            'target_latency_ms': 200,
            'min_confidence': 0.7,
            'max_false_positive_rate': 0.05,
            'min_accuracy': 0.90
        }
    
    def log_detection(self, gesture_type, confidence, latency_ms, was_correct=True):
        """Log a gesture detection event"""
        self.metrics['detections'].append({
            'timestamp': time.time(),
            'gesture': gesture_type,
            'confidence': confidence,
            'latency_ms': latency_ms,
            'correct': was_correct
        })
        
        self.metrics['confidence_scores'].append(confidence)
        self.metrics['latencies'].append(latency_ms)
        self.metrics['gesture_types'][gesture_type] += 1
        
        if not was_correct:
            self.metrics['false_positives'].append({
                'gesture': gesture_type,
                'confidence': confidence,
                'timestamp': time.time()
            })
    
    def log_error(self, error_type, details):
        """Log an error event"""
        self.metrics['errors'].append({
            'timestamp': time.time(),
            'type': error_type,
            'details': details
        })
    
    def get_accuracy(self):
        """Calculate overall accuracy"""
        if not self.metrics['detections']:
            return 0.0
        
        correct = sum(1 for d in self.metrics['detections'] if d['correct'])
        total = len(self.metrics['detections'])
        return correct / total
    
    def get_false_positive_rate(self):
        """Calculate false positive rate"""
        if not self.metrics['detections']:
            return 0.0
        
        return len(self.metrics['false_positives']) / len(self.metrics['detections'])
    
    def get_average_latency(self):
        """Calculate average detection latency"""
        if not self.metrics['latencies']:
            return 0.0
        return np.mean(self.metrics['latencies'])
    
    def get_average_confidence(self):
        """Calculate average confidence score"""
        if not self.metrics['confidence_scores']:
            return 0.0
        return np.mean(self.metrics['confidence_scores'])
    
    def get_p95_latency(self):
        """Get 95th percentile latency"""
        if not self.metrics['latencies']:
            return 0.0
        return np.percentile(self.metrics['latencies'], 95)
    
    def check_requirements(self):
        """Check if system meets performance requirements"""
        results = {
            'latency': {
                'target': self.requirements['target_latency_ms'],
                'actual': self.get_average_latency(),
                'passed': self.get_average_latency() <= self.requirements['target_latency_ms']
            },
            'confidence': {
                'target': self.requirements['min_confidence'],
                'actual': self.get_average_confidence(),
                'passed': self.get_average_confidence() >= self.requirements['min_confidence']
            },
            'false_positive_rate': {
                'target': self.requirements['max_false_positive_rate'],
                'actual': self.get_false_positive_rate(),
                'passed': self.get_false_positive_rate() <= self.requirements['max_false_positive_rate']
            },
            'accuracy': {
                'target': self.requirements['min_accuracy'],
                'actual': self.get_accuracy(),
                'passed': self.get_accuracy() >= self.requirements['min_accuracy']
            }
        }
        
        return results
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        session_duration = time.time() - self.metrics['session_start']
        req_check = self.check_requirements()
        
        report = {
            'summary': {
                'session_duration_minutes': session_duration / 60,
                'total_detections': len(self.metrics['detections']),
                'total_errors': len(self.metrics['errors']),
                'gestures_per_minute': len(self.metrics['detections']) / (session_duration / 60)
            },
            'performance': {
                'accuracy': f"{self.get_accuracy() * 100:.2f}%",
                'avg_latency_ms': f"{self.get_average_latency():.1f}ms",
                'p95_latency_ms': f"{self.get_p95_latency():.1f}ms",
                'avg_confidence': f"{self.get_average_confidence():.3f}",
                'false_positive_rate': f"{self.get_false_positive_rate() * 100:.2f}%"
            },
            'gesture_distribution': dict(self.metrics['gesture_types']),
            'requirements_check': req_check,
            'all_requirements_met': all(v['passed'] for v in req_check.values())
        }
        
        return report
    
    def print_report(self):
        """Print formatted performance report"""
        report = self.generate_report()
        
        print("\n" + "="*70)
        print("GESTURE RECOGNITION SYSTEM - PERFORMANCE REPORT")
        print("="*70)
        
        print("\n📊 SESSION SUMMARY")
        print("-" * 70)
        print(f"Duration: {report['summary']['session_duration_minutes']:.1f} minutes")
        print(f"Total Detections: {report['summary']['total_detections']}")
        print(f"Gestures/Minute: {report['summary']['gestures_per_minute']:.1f}")
        print(f"Errors: {report['summary']['total_errors']}")
        
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 70)
        for metric, value in report['performance'].items():
            print(f"{metric.replace('_', ' ').title()}: {value}")
        
        print("\n🎯 REQUIREMENTS VALIDATION")
        print("-" * 70)
        for req, data in report['requirements_check'].items():
            status = "✅ PASS" if data['passed'] else "❌ FAIL"
            print(f"{req.replace('_', ' ').title()}: {status}")
            print(f"  Target: {data['target']}, Actual: {data['actual']:.2f}")
        
        print("\n📈 GESTURE DISTRIBUTION")
        print("-" * 70)
        for gesture, count in sorted(report['gesture_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / report['summary']['total_detections']) * 100
            print(f"{gesture}: {count} ({percentage:.1f}%)")
        
        print("\n" + "="*70)
        if report['all_requirements_met']:
            print("✅ ALL REQUIREMENTS MET - SYSTEM READY FOR DEPLOYMENT")
        else:
            print("⚠️  SOME REQUIREMENTS NOT MET - FURTHER OPTIMIZATION NEEDED")
        print("="*70 + "\n")
    
    def save_report(self, filename="gesture_performance_report.json"):
        report = {
            "session_summary": {
                "duration_minutes": self.duration_minutes,
                "total_detections": self.total_detections,
                "gestures_per_minute": self.gestures_per_minute,
                "errors": len(self.errors)
            },
            "metrics": self.metrics,
            "requirements_status": self.requirements_status,
            "gesture_stats": self.gesture_counts
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=numpy_converter)
            print(f"\nReport saved successfully to {filename}")
        except Exception as e:
            print(f"\nFailed to save report: {e}")


class LivePerformanceMonitor:
    """Real-time performance monitoring dashboard"""
    
    def __init__(self):
        self.window_size = 50  # Last N detections
        self.recent_latencies = []
        self.recent_confidences = []
        self.recent_accuracy = []
    
    def update(self, latency_ms, confidence, was_correct):
        """Update with new detection data"""
        self.recent_latencies.append(latency_ms)
        self.recent_confidences.append(confidence)
        self.recent_accuracy.append(1 if was_correct else 0)
        
        # Keep only recent window
        if len(self.recent_latencies) > self.window_size:
            self.recent_latencies.pop(0)
            self.recent_confidences.pop(0)
            self.recent_accuracy.pop(0)
    
    def get_status(self):
        """Get current performance status"""
        if not self.recent_latencies:
            return "No data yet"
        
        avg_latency = np.mean(self.recent_latencies)
        avg_confidence = np.mean(self.recent_confidences)
        avg_accuracy = np.mean(self.recent_accuracy)
        
        status = []
        
        # Latency check
        if avg_latency < 100:
            status.append("🟢 Latency: Excellent")
        elif avg_latency < 200:
            status.append("🟡 Latency: Good")
        else:
            status.append("🔴 Latency: Poor")
        
        # Confidence check
        if avg_confidence > 0.8:
            status.append("🟢 Confidence: High")
        elif avg_confidence > 0.6:
            status.append("🟡 Confidence: Medium")
        else:
            status.append("🔴 Confidence: Low")
        
        # Accuracy check
        if avg_accuracy > 0.95:
            status.append("🟢 Accuracy: Excellent")
        elif avg_accuracy > 0.85:
            status.append("🟡 Accuracy: Good")
        else:
            status.append("🔴 Accuracy: Poor")
        
        return " | ".join(status)


# Example usage for integration testing
def run_sample_test():
    """Run a sample test session"""
    print("Starting sample test session...")
    collector = GestureMetricsCollector()
    monitor = LivePerformanceMonitor()
    
    # Simulate 100 gesture detections
    gestures = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                'SELECT', 'SCROLL_UP', 'SCROLL_DOWN', 'SWIPE_LEFT', 'SWIPE_RIGHT']
    
    for i in range(100):
        gesture = np.random.choice(gestures)
        confidence = float(np.random.uniform(0.6, 0.98)) 
        latency = float(np.random.uniform(50, 180))
        correct = bool(np.random.random() > 0.05)
        
        collector.log_detection(gesture, confidence, latency, correct)
        monitor.update(latency, confidence, correct)
        
        if i % 20 == 0:
            print(f"\nDetection {i+1}: {monitor.get_status()}")
        
        time.sleep(0.05)  # Simulate real-time
    
    # Add some errors
    collector.log_error("camera_disconnect", "Brief camera dropout")
    collector.log_error("low_lighting", "Confidence dropped below threshold")
    
    # Generate final report
    print("\n\nGenerating final report...\n")
    collector.print_report()
    collector.save_report()


if __name__ == "__main__":
    run_sample_test()
