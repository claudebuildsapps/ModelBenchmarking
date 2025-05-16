#!/usr/bin/env python3
"""
Terminal User Interface for ModelBenchmarking database navigation.
This script provides a simple text-based interface to view and navigate
benchmark data in the database.
"""

import sys
import os
import time
import logging
import argparse
import curses
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
from tabulate import tabulate
import signal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_database_manager, DatabaseManager
import sqlite3
from src.scrapers import HuggingFaceScraper, PaperWithCodeScraper
from src.models import ModelMetadata, BenchmarkResult, DatasetMetadata
from config.settings import DATABASE_CONFIG, get_settings


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='data/tui.log'
)
logger = logging.getLogger(__name__)


class View(Enum):
    """Available views in the interface."""
    MAIN_MENU = 0
    MODELS_LIST = 1
    MODEL_DETAILS = 2
    BENCHMARKS_LIST = 3
    BENCHMARK_DETAILS = 4
    TASKS_LIST = 5
    DATA_SCRAPER = 6


class TUIController:
    """
    Terminal User Interface controller for navigating benchmark data.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the TUI controller.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.current_view = View.MAIN_MENU
        self.prev_view = None
        self.selected_index = 0
        self.models_data = []
        self.benchmarks_data = []
        self.tasks_data = []
        self.selected_model = None
        self.selected_benchmark = None
        self.selected_task = None
        self.message = ""
        self.filter_text = ""
        self.should_exit = False
        
    def populate_data(self):
        """Populate data from the database."""
        try:
            # Get models
            models_query = """
                SELECT DISTINCT model_name, model_version, MAX(timestamp) as last_updated
                FROM model_benchmarks
                GROUP BY model_name, model_version
                ORDER BY model_name
            """
            self.models_data = self.db_manager.execute_df(models_query).to_dict('records')
            
            # Get benchmark results
            benchmarks_query = """
                SELECT id, model_name, metric, score, task_type, dataset, timestamp
                FROM model_benchmarks
                ORDER BY timestamp DESC
                LIMIT 100
            """
            self.benchmarks_data = self.db_manager.execute_df(benchmarks_query).to_dict('records')
            
            # Get tasks
            tasks_query = """
                SELECT DISTINCT task_type, metric, COUNT(*) as count
                FROM model_benchmarks
                GROUP BY task_type, metric
                ORDER BY count DESC
            """
            self.tasks_data = self.db_manager.execute_df(tasks_query).to_dict('records')
            
            if not self.models_data:
                self.message = "No models found in database. Use 'Data Scraper' to populate data."
            
        except Exception as e:
            logger.error(f"Error populating data: {e}")
            self.message = f"Error: {str(e)}"
    
    def handle_input(self, key: int):
        """
        Handle user input.
        
        Args:
            key: Key code from curses
        """
        if key == curses.KEY_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == curses.KEY_DOWN:
            if self.current_view == View.MAIN_MENU:
                self.selected_index = min(6, self.selected_index + 1)
            elif self.current_view == View.MODELS_LIST:
                self.selected_index = min(len(self.models_data) - 1, self.selected_index + 1) if self.models_data else 0
            elif self.current_view == View.BENCHMARKS_LIST:
                self.selected_index = min(len(self.benchmarks_data) - 1, self.selected_index + 1) if self.benchmarks_data else 0
            elif self.current_view == View.TASKS_LIST:
                self.selected_index = min(len(self.tasks_data) - 1, self.selected_index + 1) if self.tasks_data else 0
        elif key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter key
            self.handle_enter()
        elif key == 27 or key == ord('q'):  # ESC or 'q'
            if self.current_view == View.MAIN_MENU:
                self.should_exit = True
            else:
                self.go_back()
        elif key == ord('r'):  # Refresh
            self.populate_data()
            self.message = "Data refreshed"
        elif key == ord('f'):  # Filter
            self.filter_text = self.prompt_for_input("Enter filter text:")
            self.message = f"Filter applied: {self.filter_text}"
        elif key == ord('h'):  # Help
            self.show_help()
        
    def handle_enter(self):
        """Handle enter key press in different views."""
        if self.current_view == View.MAIN_MENU:
            if self.selected_index == 0:  # Models list
                self.current_view = View.MODELS_LIST
                self.selected_index = 0
            elif self.selected_index == 1:  # Benchmarks list
                self.current_view = View.BENCHMARKS_LIST
                self.selected_index = 0
            elif self.selected_index == 2:  # Tasks list
                self.current_view = View.TASKS_LIST
                self.selected_index = 0
            elif self.selected_index == 3:  # Refresh data
                self.populate_data()
                self.message = "Data refreshed from database"
            elif self.selected_index == 4:  # Data scraper
                self.current_view = View.DATA_SCRAPER
                self.selected_index = 0
            elif self.selected_index == 5:  # Help
                self.show_help()
            elif self.selected_index == 6:  # Exit
                self.should_exit = True
        
        elif self.current_view == View.MODELS_LIST:
            if self.models_data:
                self.selected_model = self.models_data[self.selected_index]
                self.current_view = View.MODEL_DETAILS
                self.selected_index = 0
        
        elif self.current_view == View.BENCHMARKS_LIST:
            if self.benchmarks_data:
                self.selected_benchmark = self.benchmarks_data[self.selected_index]
                self.current_view = View.BENCHMARK_DETAILS
                self.selected_index = 0
        
        elif self.current_view == View.TASKS_LIST:
            if self.tasks_data:
                self.selected_task = self.tasks_data[self.selected_index]
                # Show benchmarks for this task
                task_type = self.selected_task['task_type']
                metric = self.selected_task['metric']
                task_benchmarks_query = f"""
                    SELECT id, model_name, score, dataset, timestamp
                    FROM model_benchmarks
                    WHERE task_type = '{task_type}' AND metric = '{metric}'
                    ORDER BY score DESC
                    LIMIT 20
                """
                self.benchmarks_data = self.db_manager.execute_df(task_benchmarks_query).to_dict('records')
                self.current_view = View.BENCHMARKS_LIST
                self.selected_index = 0
                self.message = f"Showing benchmarks for {task_type} - {metric}"
        
        elif self.current_view == View.DATA_SCRAPER:
            if self.selected_index == 0:  # Scrape popular models
                self.scrape_models()
            elif self.selected_index == 1:  # Scrape benchmarks
                self.scrape_benchmarks()
            elif self.selected_index == 2:  # Back to main menu
                self.current_view = View.MAIN_MENU
                self.selected_index = 0
    
    def go_back(self):
        """Go back to previous view."""
        if self.current_view == View.MODEL_DETAILS:
            self.current_view = View.MODELS_LIST
        elif self.current_view == View.BENCHMARK_DETAILS:
            self.current_view = View.BENCHMARKS_LIST
        else:
            self.current_view = View.MAIN_MENU
        self.selected_index = 0
        self.message = ""
    
    def scrape_models(self):
        """Scrape popular models and store in database."""
        self.message = "Scraping models from Hugging Face..."
        try:
            scraper = HuggingFaceScraper(use_selenium=False)  # Using requests is usually faster
            models = scraper.get_popular_models(limit=10)
            
            # Store in database
            for model in models:
                model_metadata = ModelMetadata(
                    name=model['name'],
                    version="latest",
                    description=f"Model from Hugging Face with {model.get('downloads', 0)} downloads",
                    source_url=model['url'],
                    tags=model.get('tags', [])
                )
                
                # Create a dummy benchmark result for the model
                benchmark_data = {
                    "model_name": model['name'],
                    "model_version": "latest",
                    "task_type": model.get('tags', ['unknown'])[0] if model.get('tags') else "unknown",
                    "dataset": "huggingface",
                    "metric": "downloads",
                    "score": float(model.get('downloads', 0)) if model.get('downloads') else 0.0,
                    "runtime_ms": 0,
                    "memory_usage_mb": 0.0,
                    "hardware_config": {"source": "huggingface"},
                    "metadata": {
                        "likes": model.get('likes', 0),
                        "tags": model.get('tags', [])
                    }
                }
                
                try:
                    self.db_manager.insert_benchmark(benchmark_data)
                except Exception as e:
                    logger.error(f"Error inserting benchmark: {e}")
            
            self.message = f"Successfully scraped {len(models)} models!"
            # Refresh data
            self.populate_data()
            
        except Exception as e:
            logger.error(f"Error scraping models: {e}")
            self.message = f"Error: {str(e)}"
    
    def scrape_benchmarks(self):
        """Scrape benchmarks from Papers With Code."""
        self.message = "Scraping benchmarks from Papers With Code..."
        try:
            scraper = PaperWithCodeScraper(use_selenium=False)
            tasks = scraper.get_benchmark_tasks()[:5]  # Get first 5 tasks
            
            total_benchmarks = 0
            
            for task in tasks:
                task_results = scraper.get_benchmark_results(task['url'])
                
                if not task_results or 'results' not in task_results:
                    continue
                
                results = task_results['results'][:10]  # Get top 10 results
                
                for result in results:
                    model_name = result['model']
                    task_type = task_results['task']
                    dataset = task_results['dataset']
                    score_text = result['score']
                    
                    # Try to parse the score to a float
                    try:
                        score = float(score_text.replace('%', ''))
                    except ValueError:
                        score = 0.0
                    
                    benchmark_data = {
                        "model_name": model_name,
                        "model_version": "latest",
                        "task_type": task_type,
                        "dataset": dataset,
                        "metric": "accuracy",
                        "score": score,
                        "runtime_ms": 0,
                        "memory_usage_mb": 0.0,
                        "hardware_config": {"source": "paperswithcode"},
                        "metadata": {
                            "paper_title": result.get('paper_title', ''),
                            "paper_url": result.get('paper_url', ''),
                            "code_url": result.get('code_url', '')
                        }
                    }
                    
                    try:
                        self.db_manager.insert_benchmark(benchmark_data)
                        total_benchmarks += 1
                    except Exception as e:
                        logger.error(f"Error inserting benchmark: {e}")
            
            self.message = f"Successfully scraped {total_benchmarks} benchmarks!"
            # Refresh data
            self.populate_data()
            
        except Exception as e:
            logger.error(f"Error scraping benchmarks: {e}")
            self.message = f"Error: {str(e)}"

    def show_help(self):
        """Show help information."""
        self.message = """
        Help:
        - UP/DOWN: Navigate
        - ENTER: Select
        - ESC/q: Back/Exit
        - r: Refresh data
        - f: Filter (not implemented yet)
        - h: Show this help
        """
    
    def prompt_for_input(self, prompt_text: str) -> str:
        """
        Prompt user for input.
        
        Args:
            prompt_text: Text to display in the prompt
            
        Returns:
            User input
        """
        # Not implemented in this basic version
        return ""
    
    def render(self, stdscr):
        """
        Render the current view.
        
        Args:
            stdscr: Standard screen from curses
        """
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Header
        header = "ModelBenchmarking TUI"
        stdscr.addstr(1, (width - len(header)) // 2, header, curses.A_BOLD)
        
        # Status line at the bottom
        if self.message:
            status = self.message[:width-2]
            stdscr.addstr(height-2, 1, status)
        
        # Help line
        help_text = "ESC/q: Back/Exit | ENTER: Select | r: Refresh | h: Help"
        stdscr.addstr(height-1, 1, help_text[:width-2])
        
        # Render current view
        if self.current_view == View.MAIN_MENU:
            self.render_main_menu(stdscr)
        elif self.current_view == View.MODELS_LIST:
            self.render_models_list(stdscr)
        elif self.current_view == View.MODEL_DETAILS:
            self.render_model_details(stdscr)
        elif self.current_view == View.BENCHMARKS_LIST:
            self.render_benchmarks_list(stdscr)
        elif self.current_view == View.BENCHMARK_DETAILS:
            self.render_benchmark_details(stdscr)
        elif self.current_view == View.TASKS_LIST:
            self.render_tasks_list(stdscr)
        elif self.current_view == View.DATA_SCRAPER:
            self.render_data_scraper(stdscr)
        
        stdscr.refresh()
    
    def render_main_menu(self, stdscr):
        """Render main menu."""
        menu_items = [
            "1. Models List",
            "2. Benchmarks List",
            "3. Tasks List",
            "4. Refresh Data",
            "5. Data Scraper",
            "6. Help",
            "7. Exit"
        ]
        
        for i, item in enumerate(menu_items):
            y = 4 + i
            x = 4
            mode = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
            stdscr.addstr(y, x, item, mode)
    
    def render_models_list(self, stdscr):
        """Render models list."""
        stdscr.addstr(3, 2, "Models List", curses.A_BOLD)
        
        if not self.models_data:
            stdscr.addstr(5, 4, "No models found. Use Data Scraper to populate.")
            return
        
        # Header
        stdscr.addstr(5, 2, "Model Name", curses.A_BOLD)
        stdscr.addstr(5, 30, "Version", curses.A_BOLD)
        stdscr.addstr(5, 45, "Last Updated", curses.A_BOLD)
        stdscr.addstr(6, 2, "-" * 60)
        
        # List items
        for i, model in enumerate(self.models_data):
            if i >= 15:  # Show max 15 items
                break
                
            y = 7 + i
            mode = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
            
            name = model.get('model_name', 'Unknown')[:25]
            version = model.get('model_version', 'Unknown')[:12]
            last_updated = str(model.get('last_updated', ''))[:19]
            
            stdscr.addstr(y, 2, name, mode)
            stdscr.addstr(y, 30, version, mode)
            stdscr.addstr(y, 45, last_updated, mode)
    
    def render_model_details(self, stdscr):
        """Render model details."""
        if not self.selected_model:
            return
            
        stdscr.addstr(3, 2, f"Model Details: {self.selected_model.get('model_name', 'Unknown')}", curses.A_BOLD)
        
        # Get benchmarks for this model
        model_name = self.selected_model.get('model_name', '')
        model_benchmarks_query = f"""
            SELECT task_type, dataset, metric, score, timestamp
            FROM model_benchmarks
            WHERE model_name = '{model_name}'
            ORDER BY timestamp DESC
            LIMIT 10
        """
        model_benchmarks = self.db_manager.execute_df(model_benchmarks_query).to_dict('records')
        
        # Model info
        y = 5
        stdscr.addstr(y, 4, f"Name: {self.selected_model.get('model_name', 'Unknown')}")
        y += 1
        stdscr.addstr(y, 4, f"Version: {self.selected_model.get('model_version', 'Unknown')}")
        y += 1
        stdscr.addstr(y, 4, f"Last Updated: {self.selected_model.get('last_updated', '')}")
        
        # Benchmarks
        y += 2
        stdscr.addstr(y, 2, "Recent Benchmarks:", curses.A_BOLD)
        y += 1
        
        if not model_benchmarks:
            stdscr.addstr(y, 4, "No benchmarks found for this model.")
            return
            
        # Header
        stdscr.addstr(y, 2, "Task", curses.A_BOLD)
        stdscr.addstr(y, 25, "Dataset", curses.A_BOLD)
        stdscr.addstr(y, 45, "Metric", curses.A_BOLD)
        stdscr.addstr(y, 60, "Score", curses.A_BOLD)
        y += 1
        stdscr.addstr(y, 2, "-" * 70)
        y += 1
        
        # List items
        for i, benchmark in enumerate(model_benchmarks):
            if i >= 10:  # Show max 10 items
                break
                
            task = benchmark.get('task_type', 'Unknown')[:20]
            dataset = benchmark.get('dataset', 'Unknown')[:18]
            metric = benchmark.get('metric', 'Unknown')[:12]
            score = f"{benchmark.get('score', 0):.4f}"[:8]
            
            stdscr.addstr(y, 2, task)
            stdscr.addstr(y, 25, dataset)
            stdscr.addstr(y, 45, metric)
            stdscr.addstr(y, 60, score)
            y += 1
    
    def render_benchmarks_list(self, stdscr):
        """Render benchmarks list."""
        stdscr.addstr(3, 2, "Benchmarks List", curses.A_BOLD)
        
        if not self.benchmarks_data:
            stdscr.addstr(5, 4, "No benchmarks found. Use Data Scraper to populate.")
            return
        
        # Header
        stdscr.addstr(5, 2, "Model Name", curses.A_BOLD)
        stdscr.addstr(5, 30, "Task", curses.A_BOLD)
        stdscr.addstr(5, 50, "Metric", curses.A_BOLD)
        stdscr.addstr(5, 65, "Score", curses.A_BOLD)
        stdscr.addstr(6, 2, "-" * 75)
        
        # List items
        for i, benchmark in enumerate(self.benchmarks_data):
            if i >= 15:  # Show max 15 items
                break
                
            y = 7 + i
            mode = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
            
            name = benchmark.get('model_name', 'Unknown')[:25]
            task = benchmark.get('task_type', 'Unknown')[:18]
            metric = benchmark.get('metric', 'Unknown')[:12]
            score = f"{benchmark.get('score', 0):.4f}"[:8]
            
            stdscr.addstr(y, 2, name, mode)
            stdscr.addstr(y, 30, task, mode)
            stdscr.addstr(y, 50, metric, mode)
            stdscr.addstr(y, 65, score, mode)
    
    def render_benchmark_details(self, stdscr):
        """Render benchmark details."""
        if not self.selected_benchmark:
            return
            
        stdscr.addstr(3, 2, "Benchmark Details", curses.A_BOLD)
        
        # Benchmark info
        y = 5
        model_name = self.selected_benchmark.get('model_name', 'Unknown')
        stdscr.addstr(y, 4, f"Model: {model_name}")
        y += 1
        
        task = self.selected_benchmark.get('task_type', 'Unknown')
        stdscr.addstr(y, 4, f"Task: {task}")
        y += 1
        
        dataset = self.selected_benchmark.get('dataset', 'Unknown')
        stdscr.addstr(y, 4, f"Dataset: {dataset}")
        y += 1
        
        metric = self.selected_benchmark.get('metric', 'Unknown')
        stdscr.addstr(y, 4, f"Metric: {metric}")
        y += 1
        
        score = self.selected_benchmark.get('score', 0)
        stdscr.addstr(y, 4, f"Score: {score}")
        y += 1
        
        timestamp = self.selected_benchmark.get('timestamp', '')
        stdscr.addstr(y, 4, f"Timestamp: {timestamp}")
        y += 2
        
        # Get all benchmarks for the same task/metric for comparison
        task_benchmarks_query = f"""
            SELECT model_name, score
            FROM model_benchmarks
            WHERE task_type = '{task}' AND metric = '{metric}'
            ORDER BY score DESC
            LIMIT 10
        """
        task_benchmarks = self.db_manager.execute_df(task_benchmarks_query).to_dict('records')
        
        # Compare with other models
        stdscr.addstr(y, 2, f"Top models for {task} ({metric}):", curses.A_BOLD)
        y += 1
        
        if not task_benchmarks:
            stdscr.addstr(y, 4, "No comparison data available.")
            return
            
        # Header
        stdscr.addstr(y, 4, "Model", curses.A_BOLD)
        stdscr.addstr(y, 35, "Score", curses.A_BOLD)
        y += 1
        stdscr.addstr(y, 4, "-" * 40)
        y += 1
        
        # List items
        for i, benchmark in enumerate(task_benchmarks):
            if i >= 10:  # Show max 10 items
                break
                
            name = benchmark.get('model_name', 'Unknown')[:28]
            score = f"{benchmark.get('score', 0):.4f}"[:8]
            
            # Highlight the current model
            mode = curses.A_BOLD if name == model_name else curses.A_NORMAL
            
            stdscr.addstr(y, 4, name, mode)
            stdscr.addstr(y, 35, score, mode)
            y += 1
    
    def render_tasks_list(self, stdscr):
        """Render tasks list."""
        stdscr.addstr(3, 2, "Tasks List", curses.A_BOLD)
        
        if not self.tasks_data:
            stdscr.addstr(5, 4, "No tasks found. Use Data Scraper to populate.")
            return
        
        # Header
        stdscr.addstr(5, 2, "Task Type", curses.A_BOLD)
        stdscr.addstr(5, 30, "Metric", curses.A_BOLD)
        stdscr.addstr(5, 45, "Count", curses.A_BOLD)
        stdscr.addstr(6, 2, "-" * 60)
        
        # List items
        for i, task in enumerate(self.tasks_data):
            if i >= 15:  # Show max 15 items
                break
                
            y = 7 + i
            mode = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
            
            task_type = task.get('task_type', 'Unknown')[:25]
            metric = task.get('metric', 'Unknown')[:12]
            count = str(task.get('count', 0))
            
            stdscr.addstr(y, 2, task_type, mode)
            stdscr.addstr(y, 30, metric, mode)
            stdscr.addstr(y, 45, count, mode)
    
    def render_data_scraper(self, stdscr):
        """Render data scraper options."""
        stdscr.addstr(3, 2, "Data Scraper", curses.A_BOLD)
        
        menu_items = [
            "1. Scrape Popular Models from Hugging Face",
            "2. Scrape Benchmarks from Papers With Code",
            "3. Back to Main Menu"
        ]
        
        for i, item in enumerate(menu_items):
            y = 5 + i * 2
            mode = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
            stdscr.addstr(y, 4, item, mode)


def curses_main(stdscr, db_manager):
    """Main function for curses application."""
    # Setup curses
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking input
    
    # Create controller
    controller = TUIController(db_manager)
    controller.populate_data()
    
    # Main loop
    while not controller.should_exit:
        controller.render(stdscr)
        
        try:
            key = stdscr.getch()
            if key != -1:  # If a key was pressed
                controller.handle_input(key)
        except KeyboardInterrupt:
            break


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Terminal UI for ModelBenchmarking")
    parser.add_argument(
        "--db-type", 
        choices=["clickhouse", "timescaledb"],
        default=DATABASE_CONFIG["type"],
        help="Database type to use"
    )
    parser.add_argument("--host", help="Database host")
    parser.add_argument("--port", type=int, help="Database port")
    parser.add_argument("--user", help="Database username")
    parser.add_argument("--password", help="Database password")
    parser.add_argument("--database", help="Database name")
    
    args = parser.parse_args()
    
    # Build configuration from arguments
    config = {}
    if args.host:
        config["host"] = args.host
    if args.port:
        config["port"] = args.port
    if args.user:
        config["user"] = args.user
    if args.password:
        config["password"] = args.password
    if args.database:
        config["database"] = args.database
    
    # Get appropriate database configuration
    db_config = {**DATABASE_CONFIG.get(args.db_type, {}), **config}
    
    try:
        # Initialize database manager
        db_manager = get_database_manager(args.db_type, **db_config)
        
        # Make sure database is set up
        from scripts.setup_database import setup_database
        setup_database(args.db_type, **db_config)
        
        # Start the curses application
        curses.wrapper(lambda stdscr: curses_main(stdscr, db_manager))
        
    except ImportError as e:
        print(f"\nError: Required package not installed: {str(e)}")
        
        if args.db_type == "clickhouse":
            print("\nTo install ClickHouse driver, run: pip install clickhouse-driver")
        elif args.db_type == "timescaledb":
            print("\nTo install TimescaleDB driver, run: pip install psycopg2-binary")
            
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()