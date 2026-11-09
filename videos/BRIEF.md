# Course videos brief (DevOps, from zero)

The learner asked for narrated videos and animations that explain the key concepts of the key chapters, in the same style and audio quality as their other course (ai-engineer-from-zero): a 3Blue1Brown look (black stage, Manim palette, outlined boxes that draw on, smooth motion), a calm teacher voice (Kokoro `af_heart`), and visuals that move in step with what is said. High resolution: every video is rendered at 1920x1080, 30 fps.

## Tools (already installed; do not reinstall)

- Manim: `/home/user/videotools/manimenv/bin/manim` (Manim Community 0.22). Kokoro model in `/home/user/videotools/tts/`. Fonts: CMU Serif and CMU Typewriter Text.
- Helpers: `/home/user/devops-from-zero/videos/fg.py`. Read it fully. Key pieces:
  - `VoiceScene.beat(text, *anims, run_time=None)` speaks one line with the Kokoro teacher voice and plays the animations inside that time. It also writes captions (`captions/<Scene>.vtt`).
  - `title_card(title, sub)`, `box()`, `mbox()` (monospace label), `chip()`, `arrow()`, `edge_arrow()`, `link()`, `travel()` (a dot that flows along a line), `tick()`, `fit()`, `on_circle()`, `T()` (CMU Serif text), `M()` (monospace text).
  - Colours: `BLUE_M, TEAL_M, GREEN_M, YELLOW_M, GOLD_M, RED_M, PURPLE_M, GREY_M`, plus Manim's `GREY_B`, `GREY_D`.
  - `SAY` is the pronunciation list (kubectl is said "cube control", YAML "yammel", etcd "et-see-dee"...). If the voice must say a new term, add it to `SAY` only if it is clearly missing; never change existing entries (other writers share the file).
- The finished example to match: `videos/p10/d38_reconcile.py` (scene `D38Reconcile`, Day 38, "Kubernetes runs on a loop"). Read it first. It shows the pace, the layout, how each beat changes the picture, and how the narration follows the lesson text.
- Reference quality from the other course (read 1 or 2): `/home/user/ai-engineer-from-zero/videos/rag.py`, `agent.py`, `map.py`.
- Render the final: `videos/render_hd.sh <file.py relative to videos/> <SceneClass> <slug> [poster_seconds]`. It renders 1920x1080 at 30 fps, levels the voice to -16 LUFS, and writes `public/video/<slug>.mp4`, `.jpg` (poster) and `.vtt` (captions).

## What to make

For each video in your task:
1. Read the lesson in `/home/user/devops-from-zero/content/pN.json` (sections, analogy, worked example, diagram caption). The video explains the concept named in your task, the way the lesson does.
2. Write the narration yourself as `beat()` lines: very simple English, short sentences, a calm teacher explaining at a whiteboard, 3Blue1Brown pacing. Facts, numbers, names, commands and ports must match the lesson text exactly. Never add a claim the lesson does not make. Use the lab's names (hello-devops, port 8000) or clearly fake data. Never name a real employer, bank or card company. No em or en dashes in narration (captions show the same text).
3. Show, don't tell. Every beat changes something on screen: build the diagram step by step, move a packet, fill a box, highlight the part being discussed, count up a number. Use real structure (pipelines, loops, layers, timelines, tables, short code or commands in `M()` when the code is the point). On-screen text is labels and short phrases, never paragraphs.
4. Length: as long as the idea needs, usually 1.5 to 3.5 minutes. Open with `title_card()`. End with a one-line recap beat.

## Files and names

- Put each scene in `videos/pN/dDD_<topic>.py` (N = part number, DD = day). Start the file with the same two lines as the example (`import sys, pathlib; sys.path.insert(0, ...)` then `from fg import *`).
- Scene class names are unique across the course: `D05Pipes`, `D40Rollout`, and so on.
- Slug: `dDD-<topic>` (lowercase, hyphens), for example `d40-rollout`.
- Manifest: write `videos/manifest/<your-name>.json` (your name is given in your task), one entry per video:
```json
{"d40": [{"slug": "d40-rollout", "title": "How a rolling update swaps old Pods for new ones", "after": 2, "file": "p10/d40_rollout.py", "scene": "D40Rollout", "poster_at": 120.0}]}
```
`after` is the 0-based index of the lesson section the video belongs after (the section that explains this concept). `title` is a short plain sentence-case title shown under the player. `poster_at` is a time where the picture is complete and calm.

## Quality loop (do this for every video)

1. Quick check: `cd /home/user/devops-from-zero/videos && nice -n 10 /home/user/videotools/manimenv/bin/manim -ql --disable_caching --media_dir media/<Scene> pN/<file>.py <Scene>` (your own media folder, so parallel renders never collide).
2. Grab 8 frames across the video with ffmpeg and tile them into one contact sheet (`ffmpeg ... -vf tile=2x4`), then look at it with the Read tool. Fix any overlap, text running off the frame or within 0.3 units of its edge, text crossing a line or arrow, sizes too small to read (nothing under size 20), empty-looking frames, and animations that cancel each other (do not combine `FadeIn(x)` and `Indicate(x)` on the same object in one `play`; use `Succession`).
3. Only when the frames look right, render the final with `render_hd.sh`. One final render at a time; the machine has 4 cores shared with other writers.
4. After the final render, delete `videos/media/<Scene>/` to save disk space. Keep `public/video/<slug>.*`.

## Rules

- You own only the scene files, captions and manifest named in your task, and their outputs in `public/video/`. Do not edit lesson content, the site, or other writers' files.
- Do not run git commit or push. The lead commits.
- Do not download or install anything.
- Report in under 120 words: videos made (slug, length), anything you could not do, and any place where the lesson text itself looked wrong.

## Second batch notes (Nov 9)

- 21 videos already exist (see `videos/manifest/*.json` and `public/video/`). Watch how they look by reading one or two scene files; do not repeat a topic an existing video already covers in the same lesson.
- Caption times were fixed in `fg.py` (`_ts`). If you add pronunciations, prefer `SAY.extend([...])` inside your own scene file.
