# First-principles review: shared instructions

The learner's request, in their words: "each section is written thinking from first principles standpoint and someone having no knowledge about a particular topic can easily start from scratch and build a detailed intuition about the topic."

Your job is to make that true for your lessons. Read them as the learner, find every place where they would get lost or only memorise, and fix it in place.

## The reader you simulate

- Knows programming (Kotlin and the JVM at work, some Python), uses a Mac. Knows nothing about this topic.
- Has read only the EARLIER lessons of the course, in order (check `brief/index.json` for what each day covers). Assume nothing from later days.
- Wants to understand why things are the way they are, not just which command to type.

## Read first

1. `/home/user/devops-from-zero/brief/BRIEF.md` (writer rules, simple English, voice, schema). Its rules still apply.
2. The human-writing skill: `/root/.claude/skills/synced/5c806f8d-0769-4e35-ac24-a3ea18081c67_433d709e-8728-4258-b10c-98909f71fe68/human-writing/SKILL.md`. Any text you write or change is in blog mode: an experienced engineer explaining to one friend.
3. Your lessons in full, in page order: goal, guess, terms, sections, analogy, diagram caption, worked example, task, explain back, recap, check, interview, go deeper. Also skim the lesson before your first one, so you know where the reader is.

## What to look for, section by section

1. Problem first. Before a tool, feature or rule appears, does the reader know what goes wrong without it? If not, add the problem in one to three sentences, concretely (ideally with hello-devops).
2. Every new word explained at first use in the section text, not only in the terms list. Expand every acronym once. If an earlier day taught it, a short reminder with the day number is enough ("a Service (Day 41) is...").
3. Mechanism before options. Give the mental model of what actually happens (which process runs, which file is read, which machine talks to which, in what order) before flags, settings and variants.
4. No jumps. Each paragraph follows from the one before. Nothing depends on a later day except a short pointer ("Day 52 covers alerts").
5. A concrete example for every abstract idea, preferably from the lab.
6. Lists that are only facts: add the one line of "why" that connects each item to the problem, or turn the list into an explanation.
7. The "why" behind rules, defaults and orders ("why port 8000", "why this flag", "why this step comes first").
8. Where the reader would ask "but how does it know?" or "what happens if?", answer it.

Also check the analogy, worked example narration (`say`), task steps and hints, and explain-back answer in the same way.

## How to fix

- Edit prose only. Fields you may change: section `h` and `body`, `goal`, `analogy`, `mistake`, `real_world`, `diagram_caption`, `terms[].plain`, worked `say`, task `steps`, `hints`, `done_when`, `explain_back` `prompt` and `answer`, `recap`, check and guess `q` and `why`, interview `a`, `deeper.body`, and part `intro`, `recap`, flashcard `front` and `back`, quiz `q` and `why`, resource `why`.
- Never change: ids, titles, `terms[].term`, code, commands, worked `code`, URLs, refs, sources, quiz and check options or answer indexes, diagrams (SVG), the number or order of sections, minutes.
- Facts: do not change facts. When you add an explanation of how something works, it must be correct. If you are not sure, check the project's official docs (WebSearch works; GitHub repos can be cloned with --depth 1 into your scratch folder, then delete them). If you still cannot confirm it, say less.
- Keep the length rules: 1,400 to 2,200 words of section text per lesson, sentences of 30 words or fewer and a low average, lists for three or more items. If your additions push a lesson over 2,200 words, cut restating, side details or a weaker example elsewhere in that lesson. Depth of understanding beats breadth of facts.
- Keep the voice human. Do not add staging lines, "the key idea", "think of it as", "in other words", "this trips people up", one-line closers or the same opener in many sections.
- Write your changes with a Python script in your scratch folder `/home/user/devops-from-zero/brief/scratch/v4/<name>/` (exact old/new replacements, so the change is reviewable and can be re-run).

## Before you finish

1. `python3 brief/validate.py content/pN.json` gives 0 errors and 0 warnings for every part you touched.
2. `python3 brief/tells.py content/pN.json` gives 0 findings, and `python3 brief/tells.py content/p*.json` shows no repeated openers caused by your lessons.
3. `python3 brief/scratch/v4/protect.py brief/scratch/v4/orig/pN.json content/pN.json` prints "0 non-prose changes".
4. Do not run git commit or push. The lead commits.
5. Report in under 150 words: lessons reviewed, how many fixes, the three most common problems you found, two short before/after examples, any fact you corrected, and anything you could not fix within the rules (for example a lesson that needs a new section or a new diagram).
