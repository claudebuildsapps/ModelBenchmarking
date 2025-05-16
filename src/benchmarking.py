import time
import psutil
import platform
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from .database import DatabaseManager, get_database_manager

class ModelBenchmark:
    """
    Core benchmarking functionality for AI models.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize the benchmarking system.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager or get_database_manager()
        
    def benchmark_model(self, 
                       model_name: str,
                       model_version: str,
                       task_type: str,
                       dataset: str,
                       metric: str,
                       model_fn: Callable,
                       inputs: Any,
                       expected_outputs: Optional[Any] = None,
                       parameters_count: Optional[int] = None,
                       source_url: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Benchmark a model's performance.
        
        Args:
            model_name: Name of the model
            model_version: Model version identifier
            task_type: Type of task (e.g., 'image_classification')
            dataset: Dataset used for benchmarking
            metric: Performance metric name
            model_fn: Callable function that runs the model
            inputs: Input data for the model
            expected_outputs: Expected model outputs (for accuracy metrics)
            parameters_count: Number of model parameters
            source_url: Source URL for the model
            metadata: Additional metadata as a dictionary
            
        Returns:
            Benchmark results
        """
        # Measure memory usage before
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)  # Convert to MB
        
        # Measure execution time
        start_time = time.time()
        outputs = model_fn(inputs)
        end_time = time.time()
        runtime_ms = (end_time - start_time) * 1000
        
        # Measure memory usage after
        memory_after = process.memory_info().rss / (1024 * 1024)  # Convert to MB
        memory_usage = memory_after - memory_before
        
        # Calculate the score
        score = self._calculate_score(outputs, expected_outputs, metric) if expected_outputs else None
        
        # Get hardware configuration
        hardware_config = self._get_hardware_info()
        
        # Prepare benchmark result
        result = {
            "id": str(uuid.uuid4()),
            "model_name": model_name,
            "model_version": model_version,
            "task_type": task_type,
            "dataset": dataset,
            "metric": metric,
            "score": score,
            "runtime_ms": int(runtime_ms),
            "memory_usage_mb": float(memory_usage),
            "hardware_config": hardware_config,
            "parameters_count": parameters_count,
            "source_url": source_url,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Store result in database
        if self.db_manager:
            self.db_manager.insert_benchmark(result)
            
        return result
    
    def _calculate_score(self, 
                         outputs: Any, 
                         expected_outputs: Any, 
                         metric: str) -> float:
        """
        Calculate the score based on the specified metric.
        
        Args:
            outputs: Model outputs
            expected_outputs: Expected outputs
            metric: Metric name
            
        Returns:
            Calculated score
        """
        # Implement various metrics
        if metric == "accuracy":
            correct = sum(1 for y_pred, y_true in zip(outputs, expected_outputs) if y_pred == y_true)
            return correct / len(outputs) if outputs else 0
            
        elif metric == "precision":
            true_positives = sum(1 for y_pred, y_true in zip(outputs, expected_outputs) 
                               if y_pred == 1 and y_true == 1)
            predicted_positives = sum(1 for y_pred in outputs if y_pred == 1)
            return true_positives / predicted_positives if predicted_positives else 0
            
        elif metric == "recall":
            true_positives = sum(1 for y_pred, y_true in zip(outputs, expected_outputs) 
                              if y_pred == 1 and y_true == 1)
            actual_positives = sum(1 for y_true in expected_outputs if y_true == 1)
            return true_positives / actual_positives if actual_positives else 0
            
        elif metric == "f1":
            precision = self._calculate_score(outputs, expected_outputs, "precision")
            recall = self._calculate_score(outputs, expected_outputs, "recall")
            return 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0
            
        elif metric == "mean_squared_error":
            return sum((y_pred - y_true) ** 2 for y_pred, y_true in zip(outputs, expected_outputs)) / len(outputs) if outputs else 0
        
        # Add more metrics as needed
        
        # Default: return 0 for unknown metrics
        return 0.0
        
    def _get_hardware_info(self) -> Dict[str, str]:
        """
        Get information about the hardware environment.
        
        Returns:
            Hardware configuration information
        """
        return {
            "cpu": platform.processor(),
            "cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
    
    def compare_models(self, 
                       models: List[Dict[str, Any]],
                       task_type: str,
                       dataset: str,
                       metric: str,
                       inputs: Any,
                       expected_outputs: Optional[Any] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compare multiple models on the same task.
        
        Args:
            models: List of model configurations
            task_type: Type of task
            dataset: Dataset name
            metric: Performance metric
            inputs: Input data
            expected_outputs: Expected outputs
            
        Returns:
            Comparison results
        """
        results = []
        
        for model_config in models:
            result = self.benchmark_model(
                model_name=model_config["name"],
                model_version=model_config["version"],
                task_type=task_type,
                dataset=dataset,
                metric=metric,
                model_fn=model_config["function"],
                inputs=inputs,
                expected_outputs=expected_outputs,
                parameters_count=model_config.get("parameters_count"),
                source_url=model_config.get("source_url"),
                metadata=model_config.get("metadata")
            )
            results.append(result)
            
        # Sort results by score (descending) and runtime (ascending)
        sorted_by_score = sorted(results, key=lambda x: (-(x["score"] or 0), x["runtime_ms"]))
        sorted_by_runtime = sorted(results, key=lambda x: (x["runtime_ms"], -(x["score"] or 0)))
        
        return {
            "by_score": sorted_by_score,
            "by_runtime": sorted_by_runtime
        }
        
    def get_model_benchmarks(self, model_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get benchmark results for a specific model.
        
        Args:
            model_name: Name of the model
            limit: Maximum number of results to return
            
        Returns:
            List of benchmark results
        """
        if not self.db_manager:
            return []
            
        df = self.db_manager.get_model_benchmarks(model_name, limit)
        return df.to_dict('records') if not df.empty else []
        
    def get_top_models(self, task_type: str, metric: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top-performing models for a specific task and metric.
        
        Args:
            task_type: Type of task
            metric: Performance metric
            limit: Maximum number of results to return
            
        Returns:
            List of top models
        """
        if not self.db_manager:
            return []
            
        df = self.db_manager.get_top_models(task_type, metric, limit)
        return df.to_dict('records') if not df.empty else []