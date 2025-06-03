import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from pprint import pp

DIR_CURRENT = Path(__file__).parent
TB_FILE = DIR_CURRENT / "adder_tb.v"


def evaluate(program_path):
    """Evaluate a verilog design using iverlog to run a testbench and yosys to make sure the design is synthesizable and get stats"""

    program_path = Path(program_path)

    # make a tempdir to store the output
    # eval_dir = tempfile.TemporaryDirectory(delete=False)
    with tempfile.TemporaryDirectory(delete=False) as eval_dir:
        eval_dir_fp = Path(eval_dir)
        print(f"Using temporary directory: {eval_dir_fp}")

        # program_temp_path = eval_dir_fp / program_path.name
        program_temp_path = eval_dir_fp / "adder.v"
        program_temp_path.write_text(program_path.read_text())

        lines = program_temp_path.read_text().splitlines()
        if lines[0].strip() == "python":
            lines = lines[1:]
        elif lines[0].strip() == "verilog":
            lines = lines[1:]
        program_temp_path.write_text("\n".join(lines))

        tb_temp_path = eval_dir_fp / TB_FILE.name
        tb_temp_path.write_text(TB_FILE.read_text())

        # run iverilog to compile the design and testbench
        p = subprocess.run(
            [
                "iverilog",
                "-g2012",
                "-o",
                f"{eval_dir_fp}/adder_tb.vvp",
                str(program_temp_path),
                str(tb_temp_path),
            ],
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            print(f"Error compiling with iverilog: {p.stderr.strip()}")
            return {
                "lut_count": 0.0,
                "total_lut_sizes": 0.0,
                # "error": f"Testbench compilation failed for iverilog:\n{p.stderr.strip()}",
                "invalid": 1.0,
            }
        # then run the testbench
        p = subprocess.run(
            ["vvp", f"{eval_dir_fp}/adder_tb.vvp"], capture_output=True, text=True
        )
        if p.returncode != 0:
            print(f"Error running testbench with vvp: {p.stderr.strip()}")
            return {
                "lut_count": 0.0,
                "total_lut_sizes": 0.0,
                # "error": f"Testbench execution failed for vvp:\n{p.stderr.strip()}",
                "invalid": 1.0,
            }
        if "FAIL" in p.stdout:
            print(f"Testbench failed:\n{p.stdout.strip()}")
            return {
                "lut_count": 0.0,
                "total_lut_sizes": 0.0,
                # "error": f"Testbench failed:\n{p.stdout.strip()}",
                "invalid": 1.0,
            }

        stat_json_output_fp = eval_dir_fp / "yosys_stats.json"

        # then run yosys to synthesize the design and get stats
        yosys_script = ""
        yosys_script += f"read_verilog -sv {program_temp_path}\n"
        yosys_script += (
            "synth_xilinx -family xc7 -top adder_64 -nocarry -noiopad -nodsp\n"
        )
        yosys_script += f"tee -o {stat_json_output_fp} stat -json\n"

        # write the yosys script to a file
        yosys_script_fp = eval_dir_fp / "yosys_script.ys"
        yosys_script_fp.write_text(yosys_script)

        p = subprocess.run(
            ["yosys", "-s", str(yosys_script_fp)], capture_output=True, text=True
        )

        if p.returncode != 0:
            print(f"Error running yosys: {p.stderr.strip()}")
            return {
                "lut_count": 0.0,
                "total_lut_sizes": 0.0,
                # "error": f"Yosys synthesis failed:\n{p.stderr.strip()}",
                "invalid": 1.0,
            }

        stats = json.loads(stat_json_output_fp.read_text())
        stats_top_cells = stats["design"]["num_cells_by_type"]

        lut_count = 0.0
        total_lut_sizes = 0.0
        for key, value in stats_top_cells.items():
            if key.startswith("LUT"):
                lut_count += value
                total_lut_sizes += value * float(key.replace("LUT", ""))

        return {
            "lut_count": float(lut_count),
            "total_lut_sizes": float(total_lut_sizes),
            # "error": None,
            "invalid": 0.0,
        }


if __name__ == "__main__":
    base_design_path = DIR_CURRENT / "adder.v"
    result = evaluate(base_design_path)
    pp(result)
