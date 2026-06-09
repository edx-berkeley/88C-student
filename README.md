# DATA 88C Jupyter Notebook Materials

Public lab and lecture notebooks for **DATA 88C: Computational Structures in Data Science** (edX xSeries).

This repository mirrors the [Data 8 materials-sp26](https://github.com/data-8/materials-sp26) layout: a Jupyter Book site with notebooks organized by course part.

## Contents

- **Part 1 - Introduction to Python** (`lab/1/`, `lec/1/`): 4 labs — getting started through higher-order functions
- **Part 2 - Recursion and Object-Oriented Programming** (`lab/2/`, `lec/2/`): 4 labs — abstract data types through object-oriented programming
- **Part 3 - Working with Data Structures** (`lab/3/`, `lec/3/`): 4 labs — inheritance through SQL

Student-facing notebooks are sourced from the course authoring pipeline into this repository.

## Local development

```bash
pip install -r requirements.txt
jupyter lab
```

Open **http://localhost:8888/lab** and navigate to notebooks under `lab/` and `lec/`.

## Build the book site

```bash
npm install -g jupyter-book
jupyter-book build --html
```

The built site is in `_build/html/`.

On push to `main`, the GitHub Action syncs `myst.yml` with notebooks on disk and deploys to GitHub Pages.

## Related courses

- [88B materials](https://github.com/edx-berkeley/88b_jupyternotebook)
- [88E materials](https://github.com/edx-berkeley/88E-student)
