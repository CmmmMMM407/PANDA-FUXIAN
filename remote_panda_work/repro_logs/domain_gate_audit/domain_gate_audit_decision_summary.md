# P1-B domain-conditioned expert gate audit

Status: Blocked/current checkpoint unsupported for 9-domain expert verification

Data use: train/val only; test was not exported or analyzed.

Static audit:
- domain_num=9, task_num=2.
- text_gate_count=2, image_gate_count=2, fusion_gate0_count=2.
- can_index_by_domain_without_new_modules=False.
- Forward path uses hardcoded index 0 for text/image/fusion gates and experts.

Dynamic index1 control:
- Train gate1-gate0 CE mean=0.0745474741315855, flip rate=0.03288672350791717, abs diff=0.04192277638399445.
- Val gate1-gate0 CE mean=0.16897495910795785, flip rate=0.08292682926829269, abs diff=0.09513010112835225.

Decision:
- Do not start P1-B training from this gate.
- Retain as implementation-analysis evidence: PANDA's current checkpoint does not contain a trained 9-domain expert gate.
- This is not a domain-conditioned expert method-family failure; a real 9-domain MoE requires new modules, controls, and D4 validation.
