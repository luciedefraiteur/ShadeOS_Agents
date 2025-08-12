# Decision — Add header_signature/body_executable segmentation (2025-08-12_115926)

We should implement finer meta segmentation now before growing fixtures further. Benefits:
- Clearer visual validation; reduces ambiguity around multi-line signatures and docstrings.
- Stable primitives for future ancestry and TFME integration.

Plan:
1) Implement `header_signature`, `body_docstring`, `body_executable` in the detector meta.
2) Update debug runners to display them with anchors.
3) Then create the big fixture and matrix tests.
