PY ?= python3

.PHONY: all quick clean test manuscript qc figures tables
.PHONY: phase1 phase2 phase3 phase4 phase5 phase6 phase7 phase8 phase9 phase10 phase11 phase12

all: phase1 phase2 phase3 phase4 phase5 phase6 phase7 phase8 phase9 phase10 phase11 phase12 figures tables manuscript qc

quick: test
	$(PY) scripts/run_quick.py

test:
	$(PY) -m pytest tests/ -x -q

phase1:
	$(PY) scripts/phase01_feasibility_audit.py

phase2:
	$(PY) scripts/phase02_baseline_validation.py

phase3:
	$(PY) scripts/phase03_intervention_check.py

phase4:
	$(PY) scripts/phase04_populations.py

phase5:
	$(PY) scripts/phase05_spreading.py

phase6:
	$(PY) scripts/phase06_outcomes.py

phase7:
	$(PY) scripts/phase07_controls.py

phase8:
	$(PY) scripts/phase08_timing.py

phase9:
	$(PY) scripts/phase09_pareto.py

phase10:
	$(PY) scripts/phase10_uncertainty.py

phase11:
	$(PY) scripts/phase11_scaling.py

phase12:
	$(PY) scripts/phase12_classification.py

figures:
	$(PY) scripts/phase13_results.py

tables: figures

manuscript:
	$(PY) scripts/build_manuscript.py

qc:
	$(PY) scripts/qc_traceability.py

clean:
	rm -rf results/figures/* results/tables/* results/logs/* data/processed/* manuscript/output 2>/dev/null || true
