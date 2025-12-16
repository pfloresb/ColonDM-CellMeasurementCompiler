# ColonDM-CellMeasurementCompiler
A short script to combine outputs from Colon320DM cellprofiler cell counting pipeline.

When running script, type the following file arguments in order:
1. File path to desired file
2. Path to output CSV file
3. Column name for conditions you want to sort by. If entering multiple conditions, separate each column with commas
4. Column name for measurements to average (default from the current Cell Profiler pipeline is Count_Cells)

If you need help when running the program, run the following snippet:
python3 measurement-integration.py --help

Typing that in your terminal will list the positional arguments to be included
