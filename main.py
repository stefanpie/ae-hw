import asyncio
import os
import shutil
from pathlib import Path
from pprint import pp

from dotenv import dotenv_values
from openevolve import OpenEvolve
from openevolve.config import Config

DIR_CURRENT = Path(__file__).parent
DIR_PROBLEM = DIR_CURRENT / "problem_multiplier"

OUTPUT_DIR = DIR_CURRENT / "run_output_multiplier"
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)

env_data = dotenv_values(DIR_CURRENT / ".env")
open_router_api_key = env_data.get("OPENAI_API_KEY")
assert open_router_api_key, "OPENAI_API_KEY must be set in .env file"
os.environ["OPENAI_API_KEY"] = open_router_api_key

config = Config.from_yaml((DIR_PROBLEM / "config_multiplier.yaml"))

evolve = OpenEvolve(
    initial_program_path=str(DIR_PROBLEM / "mult.v"),
    evaluation_file=str(DIR_PROBLEM / "evaluator.py"),
    config=config,
    output_dir=str(OUTPUT_DIR),
)


# Run the evolution
best_program = asyncio.run(evolve.run())

print("Best program metrics:")
for name, value in best_program.metrics.items():
    print(f"  {name}: {value:.4f}")
