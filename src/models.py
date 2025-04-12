from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import json
from datetime import datetime


@dataclass
class ModelMetadata:
    """
    Metadata about an AI model.
    """
    name: str
    version: str
    created_date: Optional[datetime] = None
    authors: List[str] = field(default_factory=list)
    description: str = ""
    source_url: Optional[str] = None
    license: Optional[str] = None
    parameters_count: Optional[int] = None
    architecture_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    framework: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        result = {
            "name": self.name,
            "version": self.version,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "authors": self.authors,
            "description": self.description,
            "source_url": self.source_url,
            "license": self.license,
            "parameters_count": self.parameters_count,
            "architecture_type": self.architecture_type,
            "tags": self.tags,
            "framework": self.framework,
            "additional_info": self.additional_info
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelMetadata':
        """Create from dictionary."""
        created_date = None
        if data.get("created_date"):
            try:
                created_date = datetime.fromisoformat(data["created_date"])
            except ValueError:
                pass
                
        return cls(
            name=data["name"],
            version=data["version"],
            created_date=created_date,
            authors=data.get("authors", []),
            description=data.get("description", ""),
            source_url=data.get("source_url"),
            license=data.get("license"),
            parameters_count=data.get("parameters_count"),
            architecture_type=data.get("architecture_type"),
            tags=data.get("tags", []),
            framework=data.get("framework"),
            additional_info=data.get("additional_info", {})
        )


@dataclass
class BenchmarkResult:
    """
    Results of a model benchmark run.
    """
    model_name: str
    model_version: str
    task_type: str
    dataset: str
    metric: str
    score: float
    runtime_ms: int
    memory_usage_mb: float
    hardware_config: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    parameters_count: Optional[int] = None
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "task_type": self.task_type,
            "dataset": self.dataset,
            "metric": self.metric,
            "score": self.score,
            "runtime_ms": self.runtime_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "hardware_config": json.dumps(self.hardware_config),
            "timestamp": self.timestamp.isoformat(),
            "parameters_count": self.parameters_count,
            "source_url": self.source_url,
            "metadata": json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BenchmarkResult':
        """Create from dictionary."""
        # Parse hardware_config
        hardware_config = {}
        if isinstance(data.get("hardware_config"), str):
            try:
                hardware_config = json.loads(data["hardware_config"])
            except json.JSONDecodeError:
                pass
        elif isinstance(data.get("hardware_config"), dict):
            hardware_config = data["hardware_config"]
            
        # Parse metadata
        metadata = {}
        if isinstance(data.get("metadata"), str):
            try:
                metadata = json.loads(data["metadata"])
            except json.JSONDecodeError:
                pass
        elif isinstance(data.get("metadata"), dict):
            metadata = data["metadata"]
            
        # Parse timestamp
        timestamp = datetime.now()
        if data.get("timestamp"):
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except ValueError:
                pass
                
        return cls(
            model_name=data["model_name"],
            model_version=data["model_version"],
            task_type=data["task_type"],
            dataset=data["dataset"],
            metric=data["metric"],
            score=float(data["score"]) if data.get("score") is not None else 0.0,
            runtime_ms=int(data.get("runtime_ms", 0)),
            memory_usage_mb=float(data.get("memory_usage_mb", 0.0)),
            hardware_config=hardware_config,
            timestamp=timestamp,
            parameters_count=data.get("parameters_count"),
            source_url=data.get("source_url"),
            metadata=metadata
        )


@dataclass
class DatasetMetadata:
    """
    Metadata about a dataset used for benchmarking.
    """
    name: str
    version: Optional[str] = None
    task_type: Optional[str] = None
    size: Optional[int] = None
    source_url: Optional[str] = None
    license: Optional[str] = None
    description: str = ""
    citation: Optional[str] = None
    metrics: List[str] = field(default_factory=list)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "name": self.name,
            "version": self.version,
            "task_type": self.task_type,
            "size": self.size,
            "source_url": self.source_url,
            "license": self.license,
            "description": self.description,
            "citation": self.citation,
            "metrics": self.metrics,
            "additional_info": self.additional_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatasetMetadata':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data.get("version"),
            task_type=data.get("task_type"),
            size=data.get("size"),
            source_url=data.get("source_url"),
            license=data.get("license"),
            description=data.get("description", ""),
            citation=data.get("citation"),
            metrics=data.get("metrics", []),
            additional_info=data.get("additional_info", {})
        )