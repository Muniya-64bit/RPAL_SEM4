# RPAL Interpreter

## Introduction

This project is a full implementation of an interpreter for **RPAL (Right-reference Pedagogic Algorithmic Language)** using Python. It covers all key components of an interpreter pipeline:

* **Lexical Analyzer (Scanner)**: Breaks down RPAL source code into tokens such as identifiers, keywords, literals, and operators.
* **Parser**: Constructs an **Abstract Syntax Tree (AST)** from the token stream based on RPAL grammar.
* **Standardizer**: Converts the AST into a **Standardized AST (SAST)** to simplify and normalize its structure.
* **CSE Machine (Control Stack Environment)**: Simulates execution of the standardized AST using a runtime stack-based model.

---

## Setup

### Prerequisites

* **Python 3.x**
  Install it from [python.org](https://www.python.org/downloads/) if not already installed.

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/rpal-interpreter.git
   cd rpal-interpreter
   ```

2. No external libraries are required. The interpreter uses only standard Python libraries.

---

## File Structure

```
rpal-interpreter/
├── myrpal.py                    # Entry point to the interpreter
├── parser/                      # Parser module
├── scanner/                     # Lexical analyzer (scanner)
├── standardizer/                # AST standardizer module
├── inputs/                      # Test input files
│   ├── t1.txt
│   ├── t2.txt
│   └── ...
├── input.txt                    # Default input file
├── Makefile                     # Makefile to simplify usage
└── README.md                    # Project documentation
```

---

## Usage

### Run with Makefile

#### 1. **Run and print final output**

```bash
make run file=inputs/t1.txt
```

#### 2. **Print Abstract Syntax Tree (AST)**

```bash
make ast file=inputs/t1.txt
```

#### 3. **Print Standardized AST (SAST)**

```bash
make sast file=inputs/t1.txt
```

#### 4. **Clean up bytecode/cache**

```bash
make clean
```

---

### Run with Python Directly

#### 1. **Run and print final output**

```bash
python myrpal.py inputs/t1.txt
```

#### 2. **Print AST**

```bash
python myrpal.py -ast inputs/t1.txt
```

#### 3. **Print SAST**

```bash
python myrpal.py -sast inputs/t1.txt
```

> Note: If you're on Linux/Mac and `python` doesn't work, use `python3`.

---

## Troubleshooting

### 🐍 Python Not Found

* Ensure Python is installed and added to your system’s PATH.
* On some Linux systems, use `python3` instead of `python`.

### 📄 File Not Found

* Make sure the input file path is correct.
* For example, use `inputs/t2.txt` instead of just `t2.txt` if the file is inside the `inputs/` folder.

---

## License

This project is for educational purposes and distributed under the MIT License.
