# Frozen AI candidates

Create one directory per official run:

```text
candidates/run-01/
├── src/transfer_fee/
│   ├── __init__.py
│   └── calculator.py
├── tests_ai/
│   └── test_calculator.py
├── ASSUMPTIONS.md
└── README.md
```

`README.md` records tool/model, timestamps, transcript path, raw-response checksum, and packaging-only fixes. Preserve the AI response before arranging it into this standard layout.

Do not place a reference implementation here. Failed or non-executable candidates remain part of the dataset and must not be silently replaced.

