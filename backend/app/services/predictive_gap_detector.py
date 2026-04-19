"""
Predictive Gap Detection System

Uses time-series forecasting and ML to predict knowledge gaps
before they occur. Analyzes:
- Search query patterns
- Disease outbreak trends
- Research publication velocity
- Clinical trial pipelines
- Seasonal patterns
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class TrendPrediction:
    """Predicted trend for a knowledge area"""
    topic: str
    current_demand: float
    predicted_demand: float
    confidence: float
    trend_direction: str  # increasing, decreasing, stable
    predicted_peak_date: Optional[datetime]
    urgency_score: float
    recommended_action: str


@dataclass
class KnowledgeForecast:
    """Forecast for knowledge base needs"""
    timestamp: datetime
    emerging_topics: List[TrendPrediction]
    declining_topics: List[TrendPrediction]
    critical_gaps: List[TrendPrediction]
    seasonal_patterns: Dict[str, Any]


class TimeSeriesForecaster:
    """Simple time-series forecasting for query trends"""

    def __init__(self, window_size: int = 7):
        self.window_size = window_size
        self.data: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)

    def add_point(self, topic: str, value: float, timestamp: datetime = None) -> None:
        """Add data point"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.data[topic].append((timestamp, value))

    def forecast(self, topic: str, days_ahead: int = 7) -> Optional[Dict[str, Any]]:
        """Forecast future values using exponential smoothing"""
        points = self.data.get(topic, [])

        if len(points) < self.window_size:
            return None

        # Sort by timestamp
        points = sorted(points, key=lambda x: x[0])
        values = [p[1] for p in points]

        # Exponential smoothing with trend
        alpha = 0.3  # Smoothing factor
        beta = 0.1   # Trend smoothing

        smoothed = values[0]
        trend = 0

        for value in values[1:]:
            prev_smoothed = smoothed
            smoothed = alpha * value + (1 - alpha) * (smoothed + trend)
            trend = beta * (smoothed - prev_smoothed) + (1 - beta) * trend

        # Forecast
        forecast_values = []
        current = smoothed
        for _ in range(days_ahead):
            current += trend
            forecast_values.append(max(0, current))

        # Calculate confidence (based on data variability)
        variance = np.var(values[-30:]) if len(values) >= 30 else np.var(values)
        confidence = max(0, 1 - variance / (np.mean(values) ** 2 + 1))

        return {
            "current_value": values[-1],
            "forecast_values": forecast_values,
            "trend": trend,
            "confidence": float(confidence),
            "predicted_value": forecast_values[-1] if forecast_values else values[-1]
        }

    def detect_seasonality(self, topic: str) -> Dict[str, Any]:
        """Detect seasonal patterns in topic queries"""
        points = self.data.get(topic, [])

        if len(points) < 60:  # Need at least 2 months of data
            return {"detected": False, "reason": "insufficient_data"}

        # Group by day of week
        by_weekday = defaultdict(list)
        for ts, value in points:
            by_weekday[ts.weekday()].append(value)

        weekday_avg = {d: np.mean(v) for d, v in by_weekday.items()}

        # Group by month (for seasonality)
        by_month = defaultdict(list)
        for ts, value in points:
            by_month[ts.month].append(value)

        month_avg = {m: np.mean(v) for m, v in by_month.items()}

        # Detect if there's significant variation
        weekday_std = np.std(list(weekday_avg.values()))
        month_std = np.std(list(month_avg.values()))

        return {
            "detected": weekday_std > 0.1 or month_std > 0.1,
            "weekday_pattern": weekday_avg,
            "monthly_pattern": month_avg,
            "weekday_strength": float(weekday_std),
            "monthly_strength": float(month_std)
        }


class PredictiveGapDetector:
    """
    Predicts knowledge gaps before they occur.
    """

    def __init__(self, storage_dir: str = "data/knowledge_base"):
        self.storage_dir = storage_dir
        self.forecaster = TimeSeriesForecaster(window_size=7)

        # Trend analysis
        self.topic_velocity: Dict[str, List[float]] = defaultdict(list)
        self.emerging_signals: Dict[str, Any] = {}

        # Disease surveillance
        self.disease_trends: Dict[str, Any] = {}
        self.seasonal_diseases = {
            "influenza": {"peak_months": [12, 1, 2], "preparation_months": [10, 11]},
            "allergies": {"peak_months": [3, 4, 5], "preparation_months": [2]},
            "heat_stroke": {"peak_months": [6, 7, 8], "preparation_months": [5]},
            "common_cold": {"peak_months": [11, 12, 1, 2], "preparation_months": [10]},
            "gastroenteritis": {"peak_months": [12, 1], "preparation_months": [11]},
        }

        # Research velocity tracking
        self.publication_velocity: Dict[str, List[Tuple[datetime, int]]] = defaultdict(list)

        # Load historical data
        self._load_data()

    def _load_data(self) -> None:
        """Load historical data from storage"""
        data_path = os.path.join(self.storage_dir, "predictive_data.json")
        if os.path.exists(data_path):
            try:
                with open(data_path, "r") as f:
                    data = json.load(f)
                    self.disease_trends = data.get("disease_trends", {})
                    self.emerging_signals = data.get("emerging_signals", {})
            except Exception as e:
                logger.warning(f"[PREDICT] Failed to load data: {e}")

    def _save_data(self) -> None:
        """Save data to storage"""
        os.makedirs(self.storage_dir, exist_ok=True)
        data_path = os.path.join(self.storage_dir, "predictive_data.json")
        try:
            with open(data_path, "w") as f:
                json.dump({
                    "disease_trends": self.disease_trends,
                    "emerging_signals": self.emerging_signals,
                    "last_updated": datetime.utcnow().isoformat()
                }, f, default=str)
        except Exception as e:
            logger.error(f"[PREDICT] Failed to save data: {e}")

    def record_query(self, query: str, results_count: int, timestamp: datetime = None) -> None:
        """Record a search query for trend analysis"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Extract topic from query (simplified)
        topic = self._extract_topic(query)

        # Record in forecaster
        demand_score = 1.0 if results_count == 0 else max(0, 1 - results_count / 10)
        self.forecaster.add_point(topic, demand_score, timestamp)

        # Track velocity
        self.topic_velocity[topic].append(demand_score)
        if len(self.topic_velocity[topic]) > 30:
            self.topic_velocity[topic] = self.topic_velocity[topic][-30:]

    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query"""
        query_lower = query.lower()

        # Disease keywords
        diseases = [
            "diabetes", "hypertension", "asthma", "depression", "anxiety",
            "cancer", "heart", "kidney", "liver", "stroke", "covid",
            "flu", "influenza", "pneumonia", "arthritis", "migraine",
            "alzheimer", "dementia", "copd", "sepsis", "uti"
        ]

        for disease in diseases:
            if disease in query_lower:
                return disease

        # Medication keywords
        medications = [
            "metformin", "lisinopril", "atorvastatin", "insulin",
            "albuterol", "sertraline", "omeprazole", "amoxicillin"
        ]

        for med in medications:
            if med in query_lower:
                return med

        # Return general category
        return "general"

    def predict_gaps(self, days_ahead: int = 14) -> KnowledgeForecast:
        """
        Predict knowledge gaps for the next N days.
        """
        emerging = []
        declining = []
        critical = []
        seasonal = {}

        now = datetime.utcnow()

        # Analyze each tracked topic
        for topic in list(self.forecaster.data.keys()):
            forecast = self.forecaster.forecast(topic, days_ahead)
            if not forecast:
                continue

            # Calculate trend
            trend = forecast["trend"]
            current = forecast["current_value"]
            predicted = forecast["predicted_value"]

            # Determine direction
            if trend > 0.1:
                direction = "increasing"
            elif trend < -0.1:
                direction = "decreasing"
            else:
                direction = "stable"

            # Calculate urgency
            urgency = self._calculate_urgency(topic, current, predicted, trend)

            # Determine recommended action
            action = self._recommend_action(topic, direction, urgency, predicted)

            prediction = TrendPrediction(
                topic=topic,
                current_demand=current,
                predicted_demand=predicted,
                confidence=forecast["confidence"],
                trend_direction=direction,
                predicted_peak_date=now + timedelta(days=days_ahead) if direction == "increasing" else None,
                urgency_score=urgency,
                recommended_action=action
            )

            if direction == "increasing" and urgency > 0.6:
                emerging.append(prediction)
                if urgency > 0.8:
                    critical.append(prediction)
            elif direction == "decreasing":
                declining.append(prediction)

        # Detect seasonal patterns
        seasonal = self._analyze_seasonal_patterns()

        # Sort by urgency
        emerging.sort(key=lambda x: x.urgency_score, reverse=True)
        critical.sort(key=lambda x: x.urgency_score, reverse=True)

        return KnowledgeForecast(
            timestamp=now,
            emerging_topics=emerging[:10],
            declining_topics=declining[:5],
            critical_gaps=critical[:5],
            seasonal_patterns=seasonal
        )

    def _calculate_urgency(self, topic: str, current: float,
                          predicted: float, trend: float) -> float:
        """Calculate urgency score for a topic"""
        # Base urgency on trend magnitude
        urgency = min(abs(trend) * 5, 1.0)

        # Boost if predicted demand is high
        if predicted > 0.7:
            urgency = min(urgency + 0.3, 1.0)

        # Boost if current is already high (ongoing gap)
        if current > 0.5:
            urgency = min(urgency + 0.2, 1.0)

        # Check seasonal relevance
        current_month = datetime.utcnow().month
        if topic in self.seasonal_diseases:
            prep_months = self.seasonal_diseases[topic]["preparation_months"]
            if current_month in prep_months:
                urgency = min(urgency + 0.4, 1.0)

        return urgency

    def _recommend_action(self, topic: str, direction: str,
                         urgency: float, predicted: float) -> str:
        """Recommend action based on prediction"""
        if urgency > 0.8:
            return f"CRITICAL: Immediate knowledge acquisition needed for {topic}"
        elif urgency > 0.6:
            return f"HIGH: Schedule knowledge update for {topic} within 48 hours"
        elif direction == "increasing":
            return f"MEDIUM: Monitor {topic} trend and prepare resources"
        elif direction == "decreasing":
            return f"LOW: {topic} interest declining - consider archiving"
        else:
            return f"NORMAL: Maintain current knowledge level for {topic}"

    def _analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """Analyze seasonal disease patterns"""
        current_month = datetime.utcnow().month
        upcoming_peaks = []

        for disease, pattern in self.seasonal_diseases.items():
            peak_months = pattern["peak_months"]
            prep_months = pattern["preparation_months"]

            # Check if we should prepare
            if current_month in prep_months:
                peak = min(peak_months)
                months_until = (peak - current_month) % 12
                upcoming_peaks.append({
                    "disease": disease,
                    "months_until_peak": months_until,
                    "preparation_recommended": True,
                    "urgency": 0.9 if months_until <= 1 else 0.7
                })

        return {
            "current_month": current_month,
            "upcoming_seasonal_outbreaks": sorted(upcoming_peaks, key=lambda x: x["months_until_peak"]),
            "diseases_tracked": len(self.seasonal_diseases)
        }

    def detect_emerging_diseases(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect emerging diseases from news/research sources.
        """
        emerging = []

        for source in sources:
            name = source.get("name", "").lower()
            mentions = source.get("mentions", 0)
            velocity = source.get("velocity", 0)

            # High velocity indicates emergence
            if velocity > 5 or mentions > 100:
                risk_score = min((velocity * 0.1) + (mentions * 0.001), 1.0)

                emerging.append({
                    "disease": name,
                    "mention_count": mentions,
                    "velocity": velocity,
                    "risk_score": risk_score,
                    "status": "emerging" if risk_score > 0.7 else "monitoring",
                    "recommendation": f"Prepare knowledge base for {name} - rapid growth detected"
                })

        return sorted(emerging, key=lambda x: x["risk_score"], reverse=True)

    def get_statistics(self) -> Dict[str, Any]:
        """Get detector statistics"""
        return {
            "topics_tracked": len(self.forecaster.data),
            "emerging_signals": len(self.emerging_signals),
            "seasonal_patterns": len(self.seasonal_diseases),
            "forecasts_made": sum(len(v) for v in self.forecaster.data.values()),
            "last_analysis": datetime.utcnow().isoformat()
        }


# Singleton instance
_predictive_detector: Optional[PredictiveGapDetector] = None


def get_predictive_detector() -> PredictiveGapDetector:
    global _predictive_detector
    if _predictive_detector is None:
        _predictive_detector = PredictiveGapDetector()
    return _predictive_detector
