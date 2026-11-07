# Human-writing pass (blog mode): instructions for each editor

You are editing finished lessons of "DevOps, from zero" so the prose reads as written by a person, not a chatbot. The learner asked for this explicitly.

Read these first, fully:
1. The human-writing skill: /root/.claude/skills/synced/5c806f8d-0769-4e35-ac24-a3ea18081c67_433d709e-8728-4258-b10c-98909f71fe68/human-writing/SKILL.md. Apply it in Edit mode, format "Blog or article" (blog mode).
2. /home/user/devops-from-zero/brief/BRIEF.md: the learner, the simple-English and list rules, the markup, and the "Voice" section with its list of templated shapes.

Voice: an experienced engineer writing a blog-style lesson for one friend who is new to DevOps. Direct, concrete, second person, uneven rhythm that follows the thought, plain opinions where there is a real basis.

What to edit: every prose field. Part level: intro, recap, flashcards[].back, quiz[].why, resources[].why. Lesson level: goal, terms[].plain (keep short), sections[].body, analogy, mistake, real_world, worked.steps[].say, task steps/hints/done_when, explain_back prompt and answer, recap, check[].why and guess.why, interview[].a, deeper.body.

How to edit (this is not synonym swapping):
1. Read each lesson start to finish as the learner would, then mark the tells: staging and run-up lines, forced triads, one-line closers, "-ing" tails, filler transitions, fake-deep sayings, sentences that only restate, paragraphs that could sit in any other article, and the same shape repeated across sections or lessons.
2. Rewrite each marked spot around its point. Cut what only restates. Keep every supported claim.
3. Known repeated shapes in this course (fix all of them):
   - Analogy endings with a formula ("Where it breaks: ..."): say where the comparison stops working in your own words, folded into the analogy, and vary how you do it.
   - real_world opening with "At PayLite/PayFlow/PayLoop/a ...": open with the situation or the problem instead. A made-up company name at most once in your whole set of lessons.
   - mistake opening with "The most common mistake"/"The classic mistake": open with the mistake itself.
   - "this trips most people up", "here's the thing/part", "the key idea", "in other words", "think of it as", "in short": rewrite every one.
4. Run `python3 /home/user/devops-from-zero/brief/tells.py <your file>` until it reports 0 findings.

Hard limits:
- Keep the simple English: short sentences (none over 30 words), everyday words, the list rules from the brief.
- Never change: ids, titles, terms[].term, code, `commands`, any code inside worked steps, URLs, refs and sources (titles may stay as they are), answer indexes, option meanings, diagrams.
- Do not add facts, numbers, names, dates, anecdotes, quotes or sources that are not already there. If you find a clear factual error, fix it and report it.
- Do not rerun any older build or humanize scripts under brief/scratch (they would overwrite content).

Mechanics:
- Write your edits with a new script in /home/user/devops-from-zero/brief/scratch/v3/<your-name>/humanize.py that loads the current JSON, replaces the prose fields, and writes it back (json.dump, ensure_ascii=False, indent=1).
- Before writing, copy the original file into your scratch folder. After writing, run a diff script that proves only prose fields changed: same keys, same code, commands, URLs, answer indexes and diagrams.
- Validate: `python3 /home/user/devops-from-zero/brief/validate.py <file>` must give 0 errors and 0 warnings, and tells.py 0 findings.

Report back in under 120 words: findings before and after, the kinds of tells you fixed most, two short before/after examples, and any factual fixes.
