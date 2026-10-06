# AI-generated direct/global comparison

- AI: OpenAI ChatGPT built-in image generation (`image_gen` tool).
- Exact image model/version: not exposed by the tool; not verified. Do not label this GPT-4o or another specific version.
- Date used: 2026-09-25 (America/New_York).
- Input: `../output/floodlit.png` (1920 × 1080).
- Outputs, in requested order: `ai_direct.png`, `ai_global.png`.
- Generation mode: two separate built-in image edits, each referencing only the original floodlit image. Existing measured direct/global images and capture videos were not used as generation inputs.
- Native generated resolution: 1672 × 941 for both images. Delivery files were resampled to 1920 × 1080 using macOS sips; no independent brightness normalization was applied.

## Evidence limits

These are qualitative AI-generated estimates for the lab comparison, not measured Nayar et al. decompositions. A single floodlit photo does not uniquely determine direct and global transport. Generated details and shadows differ from the input. Exact framing/pixel correspondence is not guaranteed, and the pair does not establish Direct + Global = the input. Resizing matches dimensions only. Radiometric additivity should be assessed in linear light, not by adding gamma-encoded display values.

Method reference: https://www.cs.columbia.edu/CAVE/projects/separation/separation.php

## Direct generation prompt

Use case: lighting-weather. Scientific lab AI comparison, image 1 of 2: DIRECT component estimate. Edit target: the supplied floodlit tabletop photograph, 1920x1080. Produce ONLY one full-frame Direct image. Preserve EXACT viewpoint, framing, pixel resolution (1920x1080), geometry, objects, silhouettes, surface textures and printed text. Retain only single-bounce source-to-surface-to-camera light, both diffuse and specular direct reflections; suppress indirect interreflections and subsurface scattering. Retain point-source highlights on apple, candle lid and ceramic mug. Cast shadows should be nearly black. Suppress yellow reflected fill on lower mug from foreground yellow envelope, red reflected fill from red backdrop, internal diffuse multiple-bounce fill inside mug and apple's subsurface glow, without removing directly lit red/yellow intrinsic surface colors. Preserve illumination direction and source exposure, no exposure normalization, no aesthetic relighting, no new light. This is a qualitative single-photo estimate motivated by Nayar et al. 2006, not a measured decomposition. Target shared linear-radiance brightness scale with complementary Global so Direct+Global reconstructs original; do not brighten Direct to compensate for removed light. No labels, borders, panels, or watermarks.

## Global generation prompt

Use case: lighting-weather. Scientific lab AI comparison, image 2 of 2: GLOBAL component estimate. Edit target is the supplied original floodlit photograph, NOT an already edited Direct image. Output ONLY one full-frame Global image. Output resolution must be exactly 1920x1080 matching original. Preserve EXACT pixel alignment, viewpoint, framing, all object geometry, silhouettes, textures and printed text; do not move, resize, redraw, warp or crop anything. Show only indirect light: surface interreflections and subsurface scattering. Suppress all single-bounce source-to-surface-to-camera diffuse illumination AND direct specular highlights on apple, candle metal lid, mug. Retain dim red color bleed from red backdrop onto nearby surfaces and toy; warm yellow bounced light from foreground envelope onto lower/front mug; diffuse multiple bounce illumination inside mug; subtle subsurface apple glow. Retain realistic spatial texture: Global is not merely a blurred photo. The yellow envelope, backdrop and wooden table should be much darker after removing direct illumination, no artificial highlights or new illumination. Keep original exposure and shared brightness scale with Direct; Global should be a dim residual, not independently normalized or brightened. Target Direct+Global=input in linear light, though this is a qualitative single-photo estimate rather than measured Nayar separation. No captions, labels, panels, borders, watermarks.

