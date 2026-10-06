# Final Project — Computational Focus Stacking (Group 14)

Inspired by *Spatially-Varying Autofocus* (Qin, Sankaranarayanan, O'Toole; ICCV 2025, CMU Image Science Lab).
Idea: shoot a focal stack of one scene, align it, find the sharpest source frame per region,
and fuse into an all-in-focus image plus a focus map — a software version of the paper's
"different regions focus at different depths" concept.

## Deliverables
1. All-in-focus image per scene + focus map (which frame won each pixel).
2. Comparison: single-focus photos vs. fused result (crops at near / mid / far).
3. Ablations: number of input frames (e.g. 3 / 5 / 10), focus measure, patch size, hard vs. soft blend.
4. Stretch (pick if time): (a) simulate the paper's *selective DoF* / tilted focus plane from the focus map;
   (b) compare with a third-party stacker (Photoshop / Helicon / Zerene) — option (c) in the assignment.

## Layout
```
lab_project/
├── README.md
├── requirements.txt
├── docs/        assignment text, proposal slide (Group14FinalProj.pdf), paper PDF/notes
├── data/
│   ├── raw/       original focal stacks, one folder per scene (scene01/…); NOT committed except small samples
│   └── aligned/   registered frames (regenerable; ignored)
├── src/         align / sharpness / fuse / experiments / figures
├── results/     focus_maps/, all_in_focus/, comparisons/
└── report/      write-up and final slides
```

## Capture checklist
- Tripod, manual focus, fixed aperture / ISO / shutter, fixed white balance (turn off auto everything).
- 8–12 frames from nearest to farthest focus; keep the sequence order in file names (`01.jpg` …).
- Scenes with clear depth layers: macro (small objects on a table), desk scene, a tilted-plane scene (books / a ruler).
- Also shoot one handheld stack to test the alignment step.

## Timeline (presentation 1-slide: Oct 6; final: end of Nov)
| week | goal |
|---|---|
| by Oct 13 | read paper; shoot first stack; baseline fuse (Laplacian + argmax) working |
| by Oct 20 | alignment + focus-breathing correction; soft blending |
| by Oct 27 | 3 scenes shot; ablations run |
| by Nov 10 | stretch goal (selective DoF simulation or third-party comparison) |
| by Nov 17 | figures, report draft |
| by Nov 24 | polish, rehearse, submit |

## Roles (fill in)
- Capture & data: 
- Alignment: 
- Sharpness / fusion: 
- Experiments & figures: 
- Report / slides: 

## Notes
The instructor grades on effort and interesting results and penalizes "AI slop":
write the core code ourselves, shoot our own data, and keep notes on what failed.
