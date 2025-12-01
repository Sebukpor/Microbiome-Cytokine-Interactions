#!/usr/bin/env python3
"""
Metagenomic Taxonomic Classification Pipeline

Processes FASTQ files using Kraken2 (+ Bracken) to generate species-level
abundance tables in CSV format.

Dependencies (must be installed and in PATH):
  - kraken2
  - bracken (optional but recommended)
  - vsearch (optional; not used in this version but reserved for future extension)
  - Python: pandas, tqdm, numpy

Input:
  - Directory of FASTQ files (`.fastq`, `.fastq.gz`, paired as *_R1* / *_R2*)
Output:
  - microbes_abundances.csv: sample-wise species read counts
  - classification_log.txt: detailed execution log

Usage:
  python metagenomic_classifier.py \\
    --input_dir /path/to/fastqs \\
    --output_dir /path/to/results \\
    --kraken_db /path/to/kraken2_db \\
    [--threads 4] \\
    [--use_bracken] \\
    [--debug]

Author: Divine Sebukpor - DAS medhub
License: MIT
Version: 1.1.0
Date: 2025-12-01
"""

import os
import sys
import argparse
import logging
import subprocess
import glob
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
from typing import List, Optional, Dict, Tuple


def setup_logger(output_dir: str, debug: bool = False) -> logging.Logger:
    log_file = os.path.join(output_dir, "classification_log.txt")
    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def run_cmd(cmd: str, logger: logging.Logger, check: bool = True) -> Tuple[int, str, str]:
    logger.debug(f"Running: {cmd}")
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"STDERR: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.returncode, result.stdout, result.stderr


def discover_samples(input_dir: str) -> Dict[str, List[str]]:
    """
    Discover FASTQ files and group into samples.
    Supports:
      - Paired-end: *_R1*.fastq[.gz] and *_R2*.fastq[.gz]
      - Single-end: any other .fastq or .fastq.gz
    """
    fastq_files = glob.glob(os.path.join(input_dir, "**", "*.fastq*"), recursive=True)
    if not fastq_files:
        raise FileNotFoundError(f"No FASTQ files found in {input_dir}")

    # Identify R1 files for paired-end
    r1_files = [f for f in fastq_files if "_R1" in os.path.basename(f)]
    samples = {}

    for r1 in r1_files:
        sample_id = os.path.basename(r1).split("_R1")[0]
        r2 = r1.replace("_R1", "_R2")
        if os.path.exists(r2):
            samples[sample_id] = [r1, r2]
        else:
            samples[sample_id] = [r1]

    # Handle unpaired files
    used_files = set(sum(samples.values(), []))
    unpaired = [f for f in fastq_files if f not in used_files]
    for f in unpaired:
        sample_id = os.path.splitext(os.path.splitext(os.path.basename(f))[0])[0]
        samples[sample_id] = [f]

    return samples


def run_kraken2(
    sample_id: str,
    fastq_files: List[str],
    db_path: str,
    threads: int,
    logger: logging.Logger
) -> str:
    """Run Kraken2 and return path to report file."""
    report = f"/tmp/{sample_id}.kraken2.report"
    output = f"/tmp/{sample_id}.kraken2.out"

    is_paired = len(fastq_files) == 2
    is_gz = any(f.endswith('.gz') for f in fastq_files)

    cmd = [
        "kraken2",
        f"--db '{db_path}'",
        f"--threads {threads}",
        "--use-names",
        "--report-zero-counts",
        "--memory-mapping",
        f"--report '{report}'",
        f"--output '{output}'"
    ]

    if is_paired:
        cmd.append("--paired")
    if is_gz:
        cmd.append("--gzip-compressed")

    cmd.extend([f"'{f}'" for f in fastq_files])
    run_cmd(" ".join(cmd), logger)

    if not os.path.exists(report) or os.path.getsize(report) == 0:
        raise RuntimeError(f"Kraken2 produced empty report for {sample_id}")

    # Clean up large output file
    if os.path.exists(output):
        os.remove(output)

    return report


def run_bracken(
    kraken_report: str,
    db_path: str,
    logger: logging.Logger,
    read_len: int = 150,
    level: str = "S"
) -> str:
    """Run Bracken on Kraken2 report; return Bracken output path."""
    bracken_out = kraken_report.replace(".kraken2.report", ".bracken")
    cmd = (
        f"bracken -d '{db_path}' "
        f"-i '{kraken_report}' "
        f"-o '{bracken_out}' "
        f"-r {read_len} "
        f"-l {level}"
    )
    run_cmd(cmd, logger)
    if not os.path.exists(bracken_out):
        raise RuntimeError("Bracken failed to produce output")
    return bracken_out


def parse_species_abundance(report_path: str, use_bracken: bool = False) -> pd.DataFrame:
    """Parse Kraken2 or Bracken report to species-level counts."""
    if use_bracken:
        # Bracken output format
        df = pd.read_csv(report_path, sep="\t")
        df = df[["name", "new_est_reads"]].rename(columns={"new_est_reads": "reads"})
    else:
        # Kraken2 report format
        df = pd.read_csv(
            report_path,
            sep="\t",
            header=None,
            names=["perc", "reads_rooted", "reads_direct", "rank", "taxid", "name"]
        )
        df = df[df["rank"] == "S"][["name", "reads_rooted"]].rename(columns={"reads_rooted": "reads"})

    df["name"] = df["name"].str.strip()
    return df


def main():
    parser = argparse.ArgumentParser(description="Metagenomic Classification with Kraken2/Bracken")
    parser.add_argument("--input_dir", required=True, help="Directory with FASTQ files")
    parser.add_argument("--output_dir", required=True, help="Directory for output files")
    parser.add_argument("--kraken_db", required=True, help="Path to Kraken2 database")
    parser.add_argument("--threads", type=int, default=4, help="Threads per sample")
    parser.add_argument("--use_bracken", action="store_true", help="Run Bracken for abundance refinement")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--read_length", type=int, default=150, help="Read length for Bracken (default: 150)")

    args = parser.parse_args()

    # Validate inputs
    if not os.path.isdir(args.input_dir):
        raise NotADirectoryError(f"Input directory not found: {args.input_dir}")
    if not os.path.isdir(args.kraken_db):
        raise NotADirectoryError(f"Kraken2 DB directory not found: {args.kraken_db}")
    if not os.path.exists(os.path.join(args.kraken_db, "hash.k2d")):
        raise FileNotFoundError("Kraken2 DB appears invalid (missing hash.k2d)")

    os.makedirs(args.output_dir, exist_ok=True)
    logger = setup_logger(args.output_dir, args.debug)

    # Discover samples
    samples = discover_samples(args.input_dir)
    logger.info(f"Found {len(samples)} samples to process")

    # Output file
    output_csv = os.path.join(args.output_dir, "microbes_abundances.csv")
    first = True
    success = 0

    for sample_id, fastqs in tqdm(samples.items(), desc="Classifying samples"):
        try:
            # Run Kraken2
            kraken_report = run_kraken2(sample_id, fastqs, args.kraken_db, args.threads, logger)

            if args.use_bracken:
                # Estimate read length (simple heuristic)
                read_len = args.read_length  # Could enhance with actual read sampling
                bracken_report = run_bracken(kraken_report, args.kraken_db, logger, read_len=read_len)
                report_to_use = bracken_report
            else:
                report_to_use = kraken_report

            # Parse abundances
            df = parse_species_abundance(report_to_use, use_bracken=args.use_bracken)
            df_t = df.set_index("name")["reads"].to_frame().T
            df_t["SampleID"] = sample_id

            # Append to CSV
            df_t.to_csv(output_csv, mode="a", index=False, header=first)
            first = False
            success += 1

            # Cleanup
            os.remove(kraken_report)
            if args.use_bracken:
                os.remove(bracken_report)

        except Exception as e:
            logger.error(f"Failed to process {sample_id}: {e}")

    logger.info(f"Completed. {success}/{len(samples)} samples succeeded. Output: {output_csv}")


if __name__ == "__main__":
    main()
