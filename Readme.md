# AutoT2T
Automated Text-to-Table for Reasoning-Intensive Table QA: Pipeline Design and Benchmarking Insights

**AutoT2T** is a framework for automatically converting math word problems into table-based reasoning tasks, facilitating both dataset generation and large language model (LLM) evaluation in structured Table QA scenarios. This code repo consists of a data generation pipeline and a flexible evaluation module, designed to benchmark and analyze reasoning abilities across diverse table formats, augmentations, and LLM backends.


## Generation for new table reason data

This scipte provides a pipeline to automatically convert mathematical word problems into structured **table reasoning tasks**. It is designed to support research in **reasoning-intensive Table Question Answering (Table QA)** by enabling scalable, controllable, and diverse table generation from existing math datasets (e.g., GSM8K).
You can use this code to generate your own dataset accroding to your need.

### ✨ Key Features

- ✅ Automatic transformation of math word problems into **formal logic expressions**
- ✅ Generation of structured **tables with reasoning chains**
- ✅ Optional **table augmentations** (row/column perturbation, ordering, etc.)
- ✅ Verifies solution correctness via formal solvers
- ✅ Outputs data in a ready-to-use JSONL format

### ⚙️ How It Works

#### 1. 🔍 Semantic Decoupling

Decomposes a math word problem into a formal, machine-interpretable logic representation (e.g., SMT-style symbolic equations).

- Uses a large language model (e.g., DeepSeek-v3) to convert natural language into formal language modeling
- Ensures semantic correctness by solving the logic expression and validating the result against the ground truth answer.

#### 2. 🧱 Tabular Transformation

Converts the validated logic expression into a structured table that reflects the reasoning process.

- Each row corresponds to an entity
- The values in the table will be brought back for verification

#### 3. 🔧 Table Augmentation *(Optional)*

Applies controlled transformations to test LLM robustness under structure variability. Supported augmentations include:

- **RowAug**: Add redundant or distractor rows.
- **ColAug**: Add irrelevant or noisy columns.
- **OrdShf**: Shuffle the order of rows or columns.
- **InfMut**: Inject misleading or conflicting information

### 🚀 Run the pipeline

~~~bash
python main.py \
  --input_path gen_data/gsm8k.jsonl \
  --output_path results \
  --gpu 0 \
  --ColAug 1 \
  --RowAug 5
~~~

**Important!!!** 
TabularGSM is built based on deepseek v3, please use the corresponding API key. If you encounter other LLMs, please change the regular expression accordingly.


## Evaluation for generated table reason data

This script evaluates large language models (LLMs) such as DeepSeek, Qwen, GPT-4, etc., on rensoning-intensive table QA datasets like TabularGSM. It supports different prompting strategies (e.g., zero-shot), logging, timeout handling, and result resumption.

### 🧠 Features

- Supports multiple LLMs: DeepSeek, Qwen, GPT-4, GLM, Gemini, LLaMA, etc.
- Handles both text-based and table-based reasoning tasks.
- Supports table format styles: `se` (structured example) and `md` (markdown).
- Logs results and supports resumption of unfinished runs.
- Measures accuracy per instance and by problem type.

---

### 📦 Requirements

- Python 3.8+
- Required packages (if not available, install via pip):

```bash
pip install -r requirements.txt
```

### 🚀 How to Run
```bash
python main_evaluate.py --dataset [Your dataset name] --format [se/md] --model [Your model]

# A example is as follows
python main_evaluate.py --dataset TabularGSM_easy --format se --model Qwen314B

```
