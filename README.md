# Gradation Analysis

A desktop application for **sieve gradation analysis** of construction aggregates, built with Python and CustomTkinter. Generates, visualizes, and edits gradation curves interactively with real-time calculations.

## Features

- **Multiple Material Types** — Fine Aggregate, Coarse Aggregate (Type 1 & 2), Sub-Base, CRM Base, Aggregate 40 mm, and Aggregate 20 mm
- **Interactive Gradation Table** — Double-click to edit % Passing or Weight Retained values with automatic recalculation
- **Row Locking** — Lock any row to fix its Weight Retained and % Passing values; other unlocked rows adjust proportionally to maintain total weight balance
- **Draggable Graph** — Click and drag curve points on the gradation chart; use arrow keys for fine adjustments (±0.1%)
- **Random Curve Generation** — Generate smooth random gradation curves within specification limits
- **Fineness Modulus** — Automatic FM calculation with IS zone classification (Zone I–IV) for fine aggregates
- **Real-Time Sync** — Table, graph, and FM display stay synchronized on every edit
- **Total Weight Control** — Adjust total sample weight; retained values scale automatically
- **Dark Theme UI** — Modern dark interface with color-coded feedback

## Material Support

| Material | Sieves | Example Range |
|---|---|---|
| Fine Aggregate | 10.00 mm – Pan (8 sieves) | IS 383 Zone I–IV |
| Coarse Aggregate 1 | 40.00 mm – Pan (5 sieves) | IS 383 grading |
| Coarse Aggregate 2 | 40.00 mm – Pan (5 sieves) | IS 383 grading |
| Sub-Base | 75.00 mm – Pan (9 sieves) | IRC SP:89 |
| CRM Base | 45.00 mm – Pan (6 sieves) | CRM specification |
| Aggregate 40 mm | 80.00 mm – Pan (6 sieves) | Custom limits |
| Aggregate 20 mm | 40.00 mm – Pan (5 sieves) | Custom limits |

## How It Works

### Gradation Table
- **Sieve Size**, **Lower Limit**, **Upper Limit** — read-only specification data
- **% Passing** — editable; clamped to specification limits; recalculates retained weights
- **Wt. Retained (g)** — editable; other unlocked rows scale proportionally to maintain total weight
- **Lock** — click 🔓/🔒 to toggle; locked rows are preserved during recalculations

### Row Locking
1. Click the 🔓 icon in any row to lock it (turns to 🔒)
2. Edit another row's weight retained — locked rows stay fixed, only unlocked rows adjust
3. Click 🔒 again to unlock
4. Locks reset when switching materials

### Graph Panel
- Points are draggable within specification bounds
- Click a point to select it, then use ↑/↓ arrow keys for ±0.1% precision
- Type an exact value in the entry field and press Enter

## Installation

### Requirements
- Python 3.11+
- Dependencies: `customtkinter`, `matplotlib`, `numpy`

### Run from Source
```bash
git clone https://github.com/Sandeep2062/Gradation-Analysis.git
cd Gradation-Analysis
pip install -r requirements.txt
python main.py
```

### Build Executable
```bash
pip install pyinstaller
pyinstaller GradationAnalysis.spec
```
The output executable will be in the `dist/` folder.

## Project Structure

```
main.py                  # Entry point
config/
  materials.py           # Sieve sizes, limits for all material types
  themes.py              # Theme configuration
core/
  constraints.py         # Curve clamping utilities
  fm_calculator.py       # Fineness Modulus calculation
  gradation_engine.py    # Passing ↔ Retained conversion
  random_generator.py    # Smooth random curve generation
  total_weight.py        # Total weight manager
ui/
  app_window.py          # Main application window & layout
  footer.py              # Footer with social links
  graph_panel.py         # Interactive matplotlib graph
  input_panel.py         # Settings panel (weight, FM, random)
  table_panel.py         # Editable gradation table with lock
  tabs.py                # Material selection tabs
assets/
  icon.ico               # Application icon
```

## License

MIT License — see [LICENSE.txt](LICENSE.txt)
