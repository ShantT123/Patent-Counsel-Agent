# Filing-review demonstration

All inputs and source notes are fictional. Policy is **draft**; no professional fees or legal conclusions are represented.

From the repository root:

```sh
python3 skills/filing-review/scripts/review.py examples/filing-review/input.json
python3 -m unittest discover -s tests -v
```

`expected-output.json` is actual calculator output generated from the included input. `review-packet.md` explains the results for a human reviewer. `sources.md` supplies source locators for the illustrative data. No model or attorney validation is implied.

Try changing a weight or cost, rerunning, and comparing the results. Do not enter a made-up detectability value to complete INV-01. If an authorized user approves a real policy, record its state, approver, and date; simply changing the flag does not confer legal authority.
