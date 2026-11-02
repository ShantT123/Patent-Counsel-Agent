# Portfolio strategy demonstration

Every company, person, record, source note, and counsel assessment in this example is fictional. No real patent claim analysis is demonstrated.

From the repository root:

```sh
python3 skills/portfolio-strategy/scripts/strategy.py examples/portfolio-strategy/input.json
python3 skills/portfolio-strategy/scripts/strategy.py examples/portfolio-strategy/csv-input.json --records-csv examples/portfolio-strategy/records.csv
python3 -m unittest discover -s tests -v
```

The two commands should produce identical JSON. `expected-output.json` is actual generated analyzer output; `strategy-review.md` is a manually prepared explanation. `sources.md` contains the fictional notes cited by the input.

Try changing an assignment from proposed to confirmed, adding a missing family label, or refreshing a source date. Observe the inventory changes without treating them as proof of legal coverage. Do not modify source evidence dates just to suppress warnings in a real review.
