# HybridIDS-nhom3

Pipeline IDS lai (Rule-based + ML) cho môn Project II.

## 1. Yeu cau

- Python 3.10+
- Windows/Linux/macOS

## 2. Cai dat

```bash
python -m venv .venv
```

Kich hoat moi truong ao:

- Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

- Linux/macOS:

```bash
source .venv/bin/activate
```

Sau do cai thu vien:

```bash
pip install -r requirements.txt
```

## 3. Cau truc package

Da bo sung `__init__.py` cho cac thu muc module:

- `capture/`
- `rule_engine/`
- `ml/`
- `ui/`
- `shared/`

Nhung import sau deu hop le:

```python
from capture import capture_packet
from rule_engine import detect
from ml import predict
from ui import show
```

## 4. Chay nhanh pipeline

```bash
python main.py
```

Ky vong output:

```text
capture module working
rule engine working
ml module working
ui working
Done
```

## 5. Quy uoc shared

- Dataclass schema nam trong `shared/schema.py`
- Helper dung chung nam trong `shared/utils.py`:
	- `now_iso`
	- `load_json`
	- `save_json`
	- `to_json`

Vi du su dung:

```python
from shared.schema import FeatureVector
from shared.utils import load_json, save_json
```

## 6. Tai lieu lien quan

- `contract.md`: Hop dong giao tiep giua cac module

