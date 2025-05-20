#!/usr/bin/env python3
"""
Load one or more QASM files (from a file or an entire folder), build the corresponding Qiskit circuits,
 draw them with Matplotlib, and save to <qasm_base_name>.png inside a specified output directory.
"""

import os
import argparse
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt


def qasm_to_png(qasm_path: str, output_dir: str, scale: float = 1.0) -> str:
    """
    Load a QASM file, draw the circuit, and save as a PNG in the output directory.

    Parameters
    ----------
    qasm_path : str
        Path to the input .qasm file.
    output_dir : str
        Directory where the PNG will be saved.
    scale : float
        Scale factor for the matplotlib drawing.

    Returns
    -------
    output_path : str
        Path of the saved PNG file.
    """
    # Load the circuit
    qc = QuantumCircuit.from_qasm_file(qasm_path)

    # Draw with Matplotlib
    fig = qc.draw(output='mpl', scale=scale)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine output filename
    base = os.path.splitext(os.path.basename(qasm_path))[0]
    output_path = os.path.join(output_dir, f"{base}.png")
    
    # Save and close
    fig.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert a QASM file or all QASM files in a directory to Matplotlib circuit diagrams (PNG)."
    )
    parser.add_argument(
        'input_path',
        help="Path to an input .qasm file or a directory containing .qasm files"
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help="Directory to save the output PNG files (default: current directory)"
    )
    parser.add_argument(
        '--scale',
        type=float,
        default=1.0,
        help="Scaling factor for the circuit drawing (default: 1.0)"
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help="If set and a directory is given, scan subdirectories recursively for .qasm files"
    )
    args = parser.parse_args()

    path = args.input_path
    processed = []

    if os.path.isdir(path):
        # Gather .qasm files
        if args.recursive:
            for root, dirs, files in os.walk(path):
                for fn in files:
                    if fn.lower().endswith('.qasm'):
                        processed.append(os.path.join(root, fn))
        else:
            for fn in os.listdir(path):
                if fn.lower().endswith('.qasm') and os.path.isfile(os.path.join(path, fn)):
                    processed.append(os.path.join(path, fn))

        if not processed:
            print(f"No .qasm files found in directory: {path}")
            return

        for qasm_file in processed:
            try:
                out = qasm_to_png(qasm_file, args.output_dir, scale=args.scale)
                print(f"[{qasm_file}] → {out}")
            except Exception as e:
                print(f"Error processing '{qasm_file}': {e}")

    else:
        # Single file
        if not path.lower().endswith('.qasm'):
            print(f"Provided file is not a .qasm file: {path}")
            return
        try:
            out = qasm_to_png(path, args.output_dir, scale=args.scale)
            print(f"Circuit diagram saved as: {out}")
        except Exception as e:
            print(f"Error processing '{path}': {e}")


if __name__ == "__main__":
    main()
