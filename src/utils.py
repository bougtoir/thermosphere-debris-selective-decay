"""Shared utilities: config, paths, seeds, logging."""
from __future__ import annotations

import os
import yaml

import numpy as np


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_config(path=None):
    if path is None:
        path = os.path.join(repo_root(), "config", "default.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def rng(seed=None, cfg=None):
    if seed is None:
        seed = load_config()["seed"] if cfg is None else cfg["seed"]
    return np.random.default_rng(seed)


def ensure_dirs():
    for d in ["results/figures", "results/tables", "results/logs",
              "data/processed", "docs", "manuscript/output"]:
        os.makedirs(os.path.join(repo_root(), d), exist_ok=True)
