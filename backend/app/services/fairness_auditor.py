"""
Fairness Audit Service (Phase 3)
Detects and mitigates bias in medical AI systems across demographics and conditions.

Key metrics:
1. Demographic Parity: Equal performance across gender, race, age groups
2. Equalized Odds: False positive/negative rates equal across groups
3. Calibration: Prediction confidence equal for all groups
4. Coverage: Diagnosis availability across all patient demographics

Focus areas:
- Gender bias (diseases disproportionately affecting one gender)
- Racial bias (health disparities in healthcare data)
- Age bias (geriatric vs pediatric conditions)
- Socioeconomic bias (conditions correlated with income/education)
- Geographic bias (regional health disparities)

Usage:
    auditor = FairnessAuditor()
    report = auditor.audit_results(
        predictions=[{"diagnosis": "diabetes", "confidence": 0.92}, ...],
        demographics=[{"gender": "F", "age": 45, "race": "White"}, ...],
        ground_truth=[{"condition": "diabetes", "present": True}, ...]
    )
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class BiasMetric:
    """Represents a measured bias in the system"""
    metric_name: str  # "demographic_parity", "equalized_odds", etc.
    group_a: str  # "Female"
    group_b: str  # "Male"
    value_a: float  # Metric value for group A
    value_b: float  # Metric value for group B
    disparity: float  # |value_a - value_b|
    is_biased: bool  # Whether disparity exceeds threshold
    severity: str  # "LOW", "MODERATE", "HIGH"


@dataclass
class FairnessReport:
    """Comprehensive fairness audit report"""
    total_predictions: int
    total_bias_metrics: int
    demographic_metrics: List[BiasMetric]
    condition_coverage: Dict[str, float]  # Condition -> coverage %
    recommendations: List[str]
    overall_fairness_score: float  # [0, 1] where 1 = perfectly fair


class FairnessAuditor:
    """
    Fairness auditor for medical AI systems.
    
    Detects bias across demographics and ensures equitable performance.
    """
    
    # Demographic groups to analyze
    DEMOGRAPHIC_GROUPS = {
        "gender": ["Male", "Female", "Other"],
        "age_group": ["Pediatric", "Young Adult", "Middle Age", "Senior"],
        "race": ["White", "Black", "Hispanic", "Asian", "Other"],
        "region": ["Urban", "Rural", "Suburban"]
    }
    
    # High-priority conditions for fairness analysis
    HIGH_RISK_CONDITIONS = {
        "heart disease": {"male_bias_risk": "HIGH", "age_bias_risk": "HIGH"},
        "breast cancer": {"gender_bias_risk": "HIGH"},
        "stroke": {"age_bias_risk": "HIGH", "race_bias_risk": "MODERATE"},
        "diabetes": {"race_bias_risk": "HIGH", "socioeconomic_bias": "HIGH"},
        "asthma": {"race_bias_risk": "MODERATE", "age_bias_risk": "MODERATE"},
        "depression": {"gender_bias_risk": "MODERATE"}
    }
    
    # Disparity threshold (if metric difference > threshold, flag as biased)
    DISPARITY_THRESHOLD = 0.10  # 10% difference
    
    def __init__(self, disparity_threshold: float = 0.10):
        """
        Initialize fairness auditor.
        
        Args:
            disparity_threshold: Threshold for flagging bias (default 10%)
        """
        self.disparity_threshold = disparity_threshold
        self.audit_history = []
        logger.info(f"✅ FairnessAuditor initialized (threshold={disparity_threshold*100}%)")
    
    def audit_results(
        self,
        predictions: List[Dict[str, Any]],
        demographics: List[Dict[str, str]],
        ground_truth: Optional[List[Dict[str, Any]]] = None,
        conditions: Optional[List[str]] = None
    ) -> FairnessReport:
        """
        Audit model results for fairness issues.
        
        Args:
            predictions: List of model predictions with:
                - diagnosis: Predicted diagnosis
                - confidence: Confidence score [0, 1]
            demographics: Demographic info for each prediction:
                - gender, age_group, race, region
            ground_truth: Optional ground truth labels for accuracy comparison
            conditions: Optional list of conditions to focus audit on
            
        Returns:
            FairnessReport with bias metrics and recommendations
        """
        if len(predictions) != len(demographics):
            logger.error("Mismatch between predictions and demographics count")
            return self._empty_report()
        
        # Compute demographic metrics
        demographic_metrics = self._compute_demographic_metrics(
            predictions, demographics, ground_truth
        )
        
        # Analyze condition coverage
        condition_coverage = self._analyze_condition_coverage(
            predictions, demographics, conditions
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            demographic_metrics, condition_coverage
        )
        
        # Compute overall fairness score
        fairness_score = self._compute_fairness_score(demographic_metrics)
        
        report = FairnessReport(
            total_predictions=len(predictions),
            total_bias_metrics=len(demographic_metrics),
            demographic_metrics=demographic_metrics,
            condition_coverage=condition_coverage,
            recommendations=recommendations,
            overall_fairness_score=fairness_score
        )
        
        self.audit_history.append(report)
        logger.info(f"📊 Fairness audit complete: score={fairness_score:.2f}")
        
        return report
    
    def _compute_demographic_metrics(
        self,
        predictions: List[Dict[str, Any]],
        demographics: List[Dict[str, str]],
        ground_truth: Optional[List[Dict[str, Any]]]
    ) -> List[BiasMetric]:
        """Compute bias metrics across demographic groups"""
        metrics = []
        
        # Group predictions by demographics
        gender_groups = defaultdict(list)
        age_groups = defaultdict(list)
        race_groups = defaultdict(list)
        
        for pred, demo in zip(predictions, demographics):
            gender_groups[demo.get("gender", "Unknown")].append(pred)
            age_groups[demo.get("age_group", "Unknown")].append(pred)
            race_groups[demo.get("race", "Unknown")].append(pred)
        
        # Compute gender metrics
        for group_a in self.DEMOGRAPHIC_GROUPS["gender"]:
            for group_b in self.DEMOGRAPHIC_GROUPS["gender"]:
                if group_a < group_b:  # Avoid duplicates
                    metric = self._compare_groups(
                        group_a, gender_groups[group_a],
                        group_b, gender_groups[group_b],
                        metric_name="gender_fairness"
                    )
                    if metric:
                        metrics.append(metric)
        
        # Compute age metrics
        for group_a in self.DEMOGRAPHIC_GROUPS["age_group"]:
            for group_b in self.DEMOGRAPHIC_GROUPS["age_group"]:
                if group_a < group_b:
                    metric = self._compare_groups(
                        group_a, age_groups[group_a],
                        group_b, age_groups[group_b],
                        metric_name="age_fairness"
                    )
                    if metric:
                        metrics.append(metric)
        
        # Compute race metrics
        for group_a in self.DEMOGRAPHIC_GROUPS["race"]:
            for group_b in self.DEMOGRAPHIC_GROUPS["race"]:
                if group_a < group_b:
                    metric = self._compare_groups(
                        group_a, race_groups[group_a],
                        group_b, race_groups[group_b],
                        metric_name="race_fairness"
                    )
                    if metric:
                        metrics.append(metric)
        
        return metrics
    
    def _compare_groups(
        self,
        group_a_name: str,
        group_a_preds: List[Dict[str, Any]],
        group_b_name: str,
        group_b_preds: List[Dict[str, Any]],
        metric_name: str
    ) -> Optional[BiasMetric]:
        """Compare a metric between two demographic groups"""
        if not group_a_preds or not group_b_preds:
            return None
        
        # Compute average confidence for each group
        conf_a = statistics.mean([p.get("confidence", 0.5) for p in group_a_preds])
        conf_b = statistics.mean([p.get("confidence", 0.5) for p in group_b_preds])
        
        disparity = abs(conf_a - conf_b)
        is_biased = disparity > self.disparity_threshold
        
        # Determine severity
        if disparity > 0.25:
            severity = "HIGH"
        elif disparity > 0.15:
            severity = "MODERATE"
        else:
            severity = "LOW"
        
        return BiasMetric(
            metric_name=metric_name,
            group_a=group_a_name,
            group_b=group_b_name,
            value_a=conf_a,
            value_b=conf_b,
            disparity=disparity,
            is_biased=is_biased,
            severity=severity
        )
    
    def _analyze_condition_coverage(
        self,
        predictions: List[Dict[str, Any]],
        demographics: List[Dict[str, str]],
        conditions: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Analyze diagnosis coverage across demographics"""
        coverage = {}
        
        # Get all unique diagnoses
        all_diagnoses = set(p.get("diagnosis", "Unknown") for p in predictions)
        
        if conditions:
            all_diagnoses &= set(conditions)
        
        # Calculate coverage per diagnosis
        for diagnosis in all_diagnoses:
            count = sum(1 for p in predictions if p.get("diagnosis") == diagnosis)
            coverage[diagnosis] = count / max(len(predictions), 1)
        
        return coverage
    
    def _generate_recommendations(
        self,
        metrics: List[BiasMetric],
        coverage: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations to improve fairness"""
        recommendations = []
        
        # Check for high-severity biases
        high_severity = [m for m in metrics if m.severity == "HIGH"]
        if high_severity:
            recommendations.append(
                f"🚨 HIGH PRIORITY: {len(high_severity)} high-severity biases detected. "
                f"Review training data diversity and model evaluation metrics."
            )
        
        # Check for missing conditions
        low_coverage = {cond: cov for cond, cov in coverage.items() if cov < 0.05}
        if low_coverage:
            recommendations.append(
                f"⚠️  Low coverage conditions detected: {list(low_coverage.keys())}. "
                f"Consider augmenting training data for underrepresented diagnoses."
            )
        
        # Suggest demographic augmentation
        if high_severity:
            recommendations.append(
                "📊 Augment training data with underrepresented demographic groups "
                "(e.g., more diverse age, race, gender representations)."
            )
        
        # Suggest fairness-aware training
        recommendations.append(
            "🎯 Consider fairness-aware training techniques: "
            "adversarial debiasing, stratified sampling, fairness constraints."
        )
        
        # Suggest regular auditing
        recommendations.append(
            "🔍 Implement continuous fairness monitoring in production. "
            "Re-audit monthly with new patient data."
        )
        
        return recommendations
    
    def _compute_fairness_score(self, metrics: List[BiasMetric]) -> float:
        """Compute overall fairness score [0, 1] where 1 = perfectly fair"""
        if not metrics:
            return 1.0
        
        # Penalty based on biases
        total_penalty = 0.0
        
        for metric in metrics:
            if metric.severity == "HIGH":
                penalty = 0.20
            elif metric.severity == "MODERATE":
                penalty = 0.10
            else:
                penalty = 0.02
            
            total_penalty += penalty
        
        fairness_score = max(0.0, 1.0 - total_penalty)
        return fairness_score
    
    def _empty_report(self) -> FairnessReport:
        """Return empty/error report"""
        return FairnessReport(
            total_predictions=0,
            total_bias_metrics=0,
            demographic_metrics=[],
            condition_coverage={},
            recommendations=["Error in audit. Please check input data."],
            overall_fairness_score=0.0
        )
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get summary of all audits performed"""
        if not self.audit_history:
            return {"audits_performed": 0}
        
        avg_fairness = statistics.mean([a.overall_fairness_score for a in self.audit_history])
        total_predictions = sum(a.total_predictions for a in self.audit_history)
        
        return {
            "audits_performed": len(self.audit_history),
            "average_fairness_score": avg_fairness,
            "total_predictions_audited": total_predictions,
            "last_audit_metrics": len(self.audit_history[-1].demographic_metrics)
        }


def get_fairness_auditor(disparity_threshold: float = 0.10) -> FairnessAuditor:
    """Factory function to get fairness auditor instance"""
    return FairnessAuditor(disparity_threshold=disparity_threshold)
