#!/usr/bin/env python3
"""
Load a QASM file, build the corresponding Qiskit circuit,
draw it with Matplotlib, and save to <qasm_base_name>.png.
"""

import os
import argparse
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

def qasm_to_png(qasm_path: str, scale: float = 1.0) -> str:
    """
    Load a QASM file, draw the circuit, and save as a PNG.

    Parameters
    ----------
    qasm_path : str
        Path to the input .qasm file.
    scale : float
        Scale factor for the matplotlib drawing.

    Returns
    -------
    output_path : str
        Name of the saved PNG file.
    """
    # Load the circuit
    qc = QuantumCircuit.from_qasm_file(qasm_path)

    # Draw with Matplotlib
    fig = qc.draw(output='mpl', scale=scale)
    
    # Determine output filename
    base = os.path.splitext(os.path.basename(qasm_path))[0]
    output_path = f"{base}.png"
    
    # Save and close
    fig.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(
        description="Convert a QASM file to a Matplotlib circuit diagram (PNG)."
    )
    parser.add_argument(
        'qasm_file',
        help="Path to the input .qasm file"
    )
    parser.add_argument(
        '--scale',
        type=float,
        default=1.0,
        help="Scaling factor for the circuit drawing (default: 1.0)"
    )
    args = parser.parse_args()

    png_path = qasm_to_png(args.qasm_file, scale=args.scale)
    print(f"Circuit diagram saved as: {png_path}")

if __name__ == "__main__":
    main()
