"""
SQLite database for storing runs, labels, and experiment results.

Schema:
- tasks: Task instances with hidden properties
- runs: Workflow execution records
- node_results: Per-node results from runs
- ec_labels: Epistemic criticality labels from fault injection
- experiments: Experiment metadata and results
- predictions: Model predictions for analysis
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import numpy as np

from agentqo.executor import RunRecord
from agentqo.backends.base import NodeResult


def adapt_numpy_array(arr: np.ndarray) -> bytes:
    """Convert numpy array to bytes for SQLite storage."""
    return arr.tobytes()


def convert_numpy_array(data: bytes) -> np.ndarray:
    """Convert bytes back to numpy array."""
    return np.frombuffer(data, dtype=np.float32)


# Register numpy array adapters
sqlite3.register_adapter(np.ndarray, adapt_numpy_array)
sqlite3.register_converter("NUMPY", convert_numpy_array)


class AgentQODatabase:
    """SQLite database for AgentQO experiment data.
    
    Provides storage and retrieval for:
    - Task instances
    - Workflow runs
    - Node results with embeddings
    - EC labels from fault injection
    - Experiment results
    """
    
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: str | Path) -> None:
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_schema()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper settings."""
        conn = sqlite3.connect(
            str(self.db_path),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self.connection() as conn:
            cursor = conn.cursor()
            
            # Schema version table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
            """)
            
            # Check current version
            cursor.execute("SELECT version FROM schema_version")
            row = cursor.fetchone()
            
            if row is None:
                # Fresh database, create all tables
                self._create_tables(cursor)
                cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (self.SCHEMA_VERSION,)
                )
            elif row["version"] < self.SCHEMA_VERSION:
                # Migration needed (for future use)
                self._migrate_schema(cursor, row["version"])
    
    def _create_tables(self, cursor: sqlite3.Cursor) -> None:
        """Create all database tables."""
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                difficulty REAL NOT NULL,
                node_difficulties TEXT NOT NULL,  -- JSON
                node_importance TEXT NOT NULL,    -- JSON
                ground_truth TEXT,                -- JSON
                metadata TEXT,                    -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                task_id TEXT NOT NULL,
                final_quality REAL NOT NULL,
                total_cost REAL NOT NULL,
                skipped_nodes TEXT,    -- JSON list
                cancelled_nodes TEXT,  -- JSON list
                fidelity_plan TEXT,    -- JSON
                overrides TEXT,        -- JSON
                seed INTEGER NOT NULL,
                metadata TEXT,         -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
        """)
        
        # Node results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                output TEXT,           -- JSON
                correctness INTEGER NOT NULL,
                confidence REAL NOT NULL,
                embedding NUMPY NOT NULL,
                cost REAL NOT NULL,
                fidelity_used TEXT NOT NULL,
                metadata TEXT,         -- JSON
                FOREIGN KEY (run_id) REFERENCES runs(run_id),
                UNIQUE (run_id, node_id)
            )
        """)
        
        # EC labels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ec_labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT NOT NULL,
                node_id TEXT NOT NULL,
                num_samples INTEGER NOT NULL,
                consequence_mean REAL NOT NULL,
                consequence_std REAL NOT NULL,
                consequence_ci_low REAL NOT NULL,
                consequence_ci_high REAL NOT NULL,
                local_error_prob REAL NOT NULL,
                ec_score REAL NOT NULL,
                metadata TEXT,         -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (workflow_name, node_id)
            )
        """)
        
        # Experiments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                experiment_type TEXT NOT NULL,  -- h1, h2, h3, h4
                config TEXT NOT NULL,           -- JSON
                results TEXT,                   -- JSON
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                node_id TEXT NOT NULL,
                workflow_name TEXT NOT NULL,
                true_ec REAL NOT NULL,
                predicted_ec REAL NOT NULL,
                features TEXT,           -- JSON
                metadata TEXT,           -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_workflow ON runs(workflow_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_results_run ON node_results(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ec_labels_workflow ON ec_labels(workflow_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_experiment ON predictions(experiment_id)")
    
    def _migrate_schema(self, cursor: sqlite3.Cursor, from_version: int) -> None:
        """Migrate schema from older version."""
        # No migrations yet - for future use
        pass
    
    # Task operations
    def save_task(self, task: Any) -> None:
        """Save a task instance."""
        with self.connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks 
                (task_id, task_type, difficulty, node_difficulties, 
                 node_importance, ground_truth, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.task_type,
                task.difficulty,
                json.dumps(task.node_difficulties),
                json.dumps(task.node_importance),
                json.dumps(task.ground_truth) if task.ground_truth else None,
                json.dumps(task.metadata) if task.metadata else None,
            ))
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task by ID."""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?",
                (task_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return {
                "task_id": row["task_id"],
                "task_type": row["task_type"],
                "difficulty": row["difficulty"],
                "node_difficulties": json.loads(row["node_difficulties"]),
                "node_importance": json.loads(row["node_importance"]),
                "ground_truth": json.loads(row["ground_truth"]) if row["ground_truth"] else None,
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            }
    
    # Run operations
    def save_run(self, record: RunRecord) -> None:
        """Save a run record with all node results."""
        with self.connection() as conn:
            # Save run
            conn.execute("""
                INSERT OR REPLACE INTO runs
                (run_id, workflow_name, task_id, final_quality, total_cost,
                 skipped_nodes, cancelled_nodes, fidelity_plan, overrides, 
                 seed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.run_id,
                record.workflow_name,
                record.task_id,
                record.final_quality,
                record.total_cost,
                json.dumps(list(record.skipped_nodes)),
                json.dumps(list(record.cancelled_nodes)),
                json.dumps(self._serialize_fidelity_plan(record.fidelity_plan)),
                json.dumps(self._serialize_overrides(record.overrides)),
                record.seed,
                json.dumps(record.metadata),
            ))
            
            # Save node results
            for node_id, result in record.node_results.items():
                conn.execute("""
                    INSERT OR REPLACE INTO node_results
                    (run_id, node_id, output, correctness, confidence,
                     embedding, cost, fidelity_used, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.run_id,
                    node_id,
                    json.dumps(result.output),
                    int(result.correctness),
                    result.confidence,
                    result.embedding,
                    result.cost,
                    result.fidelity_used,
                    json.dumps(result.metadata),
                ))
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a run by ID."""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM runs WHERE run_id = ?",
                (run_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            # Get node results
            node_results = {}
            for result_row in conn.execute(
                "SELECT * FROM node_results WHERE run_id = ?",
                (run_id,)
            ):
                node_results[result_row["node_id"]] = {
                    "node_id": result_row["node_id"],
                    "output": json.loads(result_row["output"]) if result_row["output"] else None,
                    "correctness": bool(result_row["correctness"]),
                    "confidence": result_row["confidence"],
                    "embedding": result_row["embedding"],
                    "cost": result_row["cost"],
                    "fidelity_used": result_row["fidelity_used"],
                    "metadata": json.loads(result_row["metadata"]) if result_row["metadata"] else {},
                }
            
            return {
                "run_id": row["run_id"],
                "workflow_name": row["workflow_name"],
                "task_id": row["task_id"],
                "final_quality": row["final_quality"],
                "total_cost": row["total_cost"],
                "node_results": node_results,
                "skipped_nodes": set(json.loads(row["skipped_nodes"] or "[]")),
                "cancelled_nodes": set(json.loads(row["cancelled_nodes"] or "[]")),
                "seed": row["seed"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            }
    
    def get_runs_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all runs for a task."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT run_id FROM runs WHERE task_id = ?",
                (task_id,)
            ).fetchall()
            
            return [self.get_run(row["run_id"]) for row in rows]
    
    # EC label operations
    def save_ec_label(
        self,
        workflow_name: str,
        node_id: str,
        num_samples: int,
        consequence_mean: float,
        consequence_std: float,
        consequence_ci_low: float,
        consequence_ci_high: float,
        local_error_prob: float,
        ec_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Save an EC label for a node."""
        with self.connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO ec_labels
                (workflow_name, node_id, num_samples, consequence_mean,
                 consequence_std, consequence_ci_low, consequence_ci_high,
                 local_error_prob, ec_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow_name,
                node_id,
                num_samples,
                consequence_mean,
                consequence_std,
                consequence_ci_low,
                consequence_ci_high,
                local_error_prob,
                ec_score,
                json.dumps(metadata) if metadata else None,
            ))
    
    def get_ec_labels(self, workflow_name: str) -> Dict[str, Dict[str, Any]]:
        """Get all EC labels for a workflow."""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM ec_labels WHERE workflow_name = ?",
                (workflow_name,)
            ).fetchall()
            
            labels = {}
            for row in rows:
                labels[row["node_id"]] = {
                    "num_samples": row["num_samples"],
                    "consequence_mean": row["consequence_mean"],
                    "consequence_std": row["consequence_std"],
                    "consequence_ci_low": row["consequence_ci_low"],
                    "consequence_ci_high": row["consequence_ci_high"],
                    "local_error_prob": row["local_error_prob"],
                    "ec_score": row["ec_score"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                }
            
            return labels
    
    # Experiment operations
    def save_experiment(
        self,
        experiment_id: str,
        experiment_type: str,
        config: Dict[str, Any],
        results: Optional[Dict[str, Any]] = None,
        status: str = "pending",
    ) -> None:
        """Save an experiment."""
        with self.connection() as conn:
            now = datetime.now().isoformat()
            conn.execute("""
                INSERT OR REPLACE INTO experiments
                (experiment_id, experiment_type, config, results, status,
                 started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                experiment_id,
                experiment_type,
                json.dumps(config),
                json.dumps(results) if results else None,
                status,
                now if status == "running" else None,
                now if status == "completed" else None,
            ))
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get an experiment by ID."""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM experiments WHERE experiment_id = ?",
                (experiment_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return {
                "experiment_id": row["experiment_id"],
                "experiment_type": row["experiment_type"],
                "config": json.loads(row["config"]),
                "results": json.loads(row["results"]) if row["results"] else None,
                "status": row["status"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
            }
    
    # Prediction operations
    def save_predictions(
        self,
        experiment_id: str,
        model_name: str,
        predictions: List[Dict[str, Any]],
    ) -> None:
        """Save a batch of predictions."""
        with self.connection() as conn:
            for pred in predictions:
                conn.execute("""
                    INSERT INTO predictions
                    (experiment_id, model_name, node_id, workflow_name,
                     true_ec, predicted_ec, features, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    experiment_id,
                    model_name,
                    pred["node_id"],
                    pred["workflow_name"],
                    pred["true_ec"],
                    pred["predicted_ec"],
                    json.dumps(pred.get("features")),
                    json.dumps(pred.get("metadata")),
                ))
    
    def get_predictions(
        self,
        experiment_id: str,
        model_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get predictions for an experiment."""
        with self.connection() as conn:
            if model_name:
                rows = conn.execute(
                    "SELECT * FROM predictions WHERE experiment_id = ? AND model_name = ?",
                    (experiment_id, model_name)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM predictions WHERE experiment_id = ?",
                    (experiment_id,)
                ).fetchall()
            
            return [
                {
                    "model_name": row["model_name"],
                    "node_id": row["node_id"],
                    "workflow_name": row["workflow_name"],
                    "true_ec": row["true_ec"],
                    "predicted_ec": row["predicted_ec"],
                    "features": json.loads(row["features"]) if row["features"] else None,
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                }
                for row in rows
            ]
    
    # Helper methods
    def _serialize_fidelity_plan(self, plan: Any) -> Optional[Dict[str, Any]]:
        """Serialize FidelityPlan to JSON-compatible dict."""
        if plan is None:
            return None
        return {
            "assignments": {
                k: {"name": v.name, "cost": v.cost, "base_error_rate": v.base_error_rate}
                for k, v in plan.assignments.items()
            },
            "default_fidelity": (
                {"name": plan.default_fidelity.name, "cost": plan.default_fidelity.cost,
                 "base_error_rate": plan.default_fidelity.base_error_rate}
                if plan.default_fidelity else None
            ),
        }
    
    def _serialize_overrides(self, overrides: Any) -> Optional[Dict[str, Any]]:
        """Serialize ExecutionOverrides to JSON-compatible dict."""
        if overrides is None:
            return None
        return {
            "forced_correctness": overrides.forced_correctness,
            "skip_nodes": list(overrides.skip_nodes),
            "force_outputs": overrides.force_outputs,
        }
    
    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics."""
        with self.connection() as conn:
            stats = {}
            for table in ["tasks", "runs", "node_results", "ec_labels", "experiments", "predictions"]:
                row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                stats[table] = row["count"]
            return stats
