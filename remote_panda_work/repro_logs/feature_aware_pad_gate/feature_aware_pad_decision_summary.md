# P1-A feature-aware PAD/prototype frozen gate decision

Status: No-Go for current D2 hard feature-aware PAD ranking probe

Data use: Weibo-21 seed42 train/val only; test was not exported or analyzed.

Key checks:
- Anchor direct verification max abs diff: train=0.0, val=0.0.
- Train PAD top2 CE=0.00025812417777966136, bottom2 CE=0.0002466201005506871, shuffled CE=0.00025625068824541706, random mean CE=0.00024700633185441046.
- Val PAD top2 CE=0.15778331337186874, bottom2 CE=0.158167083670277, shuffled CE=0.1568494839919968, random mean CE=0.15864899531485277.

Candidate summary:
- train:
  - feature_min_top2_nonself: CE=0.0002494306444706151, abs_diff=2.3445220392780557e-05, overlap=0.4894437677628908, pass=False
  - feature_mean_top2_nonself: CE=0.0002694976214422298, abs_diff=2.5734564620963957e-05, overlap=0.452902963865205, pass=False
  - hybrid_z_top2_nonself: CE=0.00024943122529320715, abs_diff=2.3445925656625176e-05, overlap=0.48995127892813645, pass=False
  - hybrid_rank_top2_nonself: CE=0.00026091462489709447, abs_diff=1.9635638497771576e-05, overlap=0.8072472594397077, pass=False
- val:
  - feature_min_top2_nonself: CE=0.1583180712909957, abs_diff=0.0010364806508017332, overlap=0.4894308943089431, pass=False
  - feature_mean_top2_nonself: CE=0.15686450523126927, abs_diff=0.0011891640032080971, overlap=0.4796747967479675, pass=False
  - hybrid_z_top2_nonself: CE=0.1583180712909957, abs_diff=0.0010364806508017332, overlap=0.4894308943089431, pass=False
  - hybrid_rank_top2_nonself: CE=0.15708177082992475, abs_diff=0.0012313302184898797, overlap=0.802439024390244, pass=False

Decision:
- No-Go for current hard feature-aware PAD ranking under current frozen evidence.
- Do not start current feature-aware PAD training from this gate. Continue candidate race with domain-conditioned expert gate or keep results as boundary-condition evidence.
- This does not permanently exclude soft/EMA prototype or class-aware prototype memory; those need direct D2/D3 and training D4 if promoted.
