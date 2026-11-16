# Book voice for "DevOps, from zero" (fifth pass, November 2026)

Every lesson is rewritten in the voice of the **venkat-voice** skill (load it with the Skill tool as
`anthropic-skills:venkat-voice` and follow it). This file adds what is specific to this course: who the
reader is, the house rules that win over the skill, how the skill's moves map onto the lesson JSON, and the
everyday worlds each part reuses.

## The reader is a complete newcomer

The site is open to anyone. Write for someone who can use a computer and a web browser, and nothing more.
Do NOT assume they program for a living, know Kotlin, Java, Python, the JVM, Gradle, backends, databases,
servers, terminals, networks, Linux, the cloud or any company's tools. They may have written a few lines of
code once. They should be able to open any lesson and follow it from its first sentence.

- Openings and running examples start from everyday situations everyone has lived: a kitchen, a shop, a
  post office, a library, moving house, a school timetable. Set the scene in plain words before it carries
  any weight.
- A tool or product name (Docker, Kubernetes, Terraform, Prometheus...) appears only after the reader
  understands the problem it solves. Say in one plain sentence what it is the first time it appears in each
  lesson, even if an earlier lesson explained it ("Docker, the tool that builds and runs containers, ...").
- Every technical word is defined in one plain sentence at first use in each lesson: file, folder, process,
  port, server, request, IP address, YAML, JSON, environment variable, dependency, commit, image... If a
  sentence needs two new words, split it.
- Code and commands: before a listing, say in plain words what it does and why we need it; after it, walk
  through the lines that matter. Never assume the reader can read the language.
- The lab app `hello-devops` is introduced in plain words wherever a lesson leans on it: "a tiny web app
  that answers every visit with a greeting and a count of visits so far".

## House rules that win over the skill

- Very simple English: average sentence about 15 words, rarely over 30; paragraphs of three to five
  sentences.
- No em dashes or en dashes anywhere (use commas, colons, periods or parentheses).
- `python3 brief/validate.py content/pN.json` gives 0 errors and 0 warnings, and
  `python3 brief/tells.py content/pN.json` gives 0 findings. The tells list (stock phrases such as
  "in other words", "think of it as", "the key idea", "it turns out", "here's the catch") still applies.
- Facts must not change. The lessons were researched and tested; keep every version, command, flag, port,
  number and output exactly. When you add an explanation of how something works, it must be correct; if you
  are not sure, check the official docs (WebSearch works) or say less.
- Never change: ids, titles, `terms[].term`, code, commands, worked `code`, URLs, refs, sources, quiz and
  check options and answer indexes, diagrams (SVG), section figures, `minutes`, lab files. Keep the same
  number of sections in the same order, each about the same topic as before (videos and figures are
  attached to section positions). Section headings may change.
- No invented biography: "I" for opinions, expectations and reactions only. Stories put the reader or a
  plausible team in the scene. Never name a real employer, bank or card company.
- Humor: subtle and rare, as the skill says. Many sections have none.

## Mapping the skill's moves onto the lesson JSON

- `opening` (new, 90 to 180 words, markdown): an everyday scene with a small stake, the surprise or problem
  in it, why the trap is easy to fall into, a one-line link to the previous lesson (its title, not "Day N"
  alone), and the plan. It can end with "Before we start, make a guess, and keep it in mind." (the `guess`
  question follows it on the page).
- `guess`: same contract; reword `q` and `why` in the same plain voice. Options and answer stay.
- `terms[].plain`: one plain sentence each, no jargon inside the definition.
- `sections` (same count and order): one idea each, problem first, the naive way failing in public, one
  running example evolving version by version, honest numbers (the lab's real outputs are already in the
  lessons; reuse them, never invent output), at most one short bold rule per section, and a one-sentence
  bridge at the end that names the next step. Headings name the step of the journey in sentence case and
  say plainly what the section covers ("Why the second container can't find the first", not "Networking").
  Section text in total: 1,400 to 2,600 words.
- `aside` (optional, at most one): `{"title": "the reader's question?", "body": "3 to 6 sentences", "after": <section index>}`.
- `analogy`, `real_world`, `mistake`: optional once `opening` exists. Weave the good parts into the prose and
  delete the field, or keep it only if it adds something the prose doesn't.
- `recap`: 4 to 6 bullets, one of them stating the limit of today's tool.
- `closing` (new, 60 to 120 words): look back at the opening scene, one concrete thing to look for in the
  reader's own work or in the lab, then "Next, we'll..." and the question the next lesson answers.
- Worked example `say`, task steps, hints and done_when, explain-back prompt and answer, check and interview
  answers, `deeper.body`, `diagram_caption`, `goal`: same calm, plain voice, no unexplained jargon.
- Part fields (`intro`, `recap`, flashcard fronts and backs, quiz `q` and `why`, resource `why`): same voice.

## Everyday worlds, one family per part

Pick the family for your part, set it up in plain words in the first lesson that uses it, and keep using it
in that part so the reader meets old friends. Map every part of the picture to the technical idea out loud
once ("the kitchen is the server, each cook is a process"). Invent your own scenes and jokes; never copy a
book's or a speaker's.

- Part 0 (start here): a small bakery that grows from one home kitchen into a shop with many branches.
- Parts 1 and 2 (shell, Git): an office building with rooms, labelled drawers, keys and a mail room; a
  notebook where every saved page keeps a photo of the last one.
- Part 3 (networks, cloud): the postal system, street addresses, apartment numbers, sealed envelopes;
  renting rooms in a hotel instead of building a house.
- Part 4 (Python scripts): a helper who follows a written checklist and reports back done or failed.
- Parts 5 to 7 (Docker, CI, builds): a lunchbox packed the same way every time; a restaurant kitchen where
  every dish is tasted before it leaves; a recipe with ingredients that come from other recipes.
- Parts 8 and 9 (Terraform, Ansible): an architect's plan and a builder who compares it with the house;
  a checklist that a careful housekeeper can run twice without harm.
- Parts 10 and 11 (Kubernetes, GitOps): a restaurant manager who keeps every table staffed no matter who
  calls in sick; a menu board that the kitchen follows exactly.
- Parts 12 to 14 (metrics, dashboards, logs, traces): a car dashboard, a hospital patient chart, a parcel
  tracking number that follows a package through every depot.
- Parts 15 and 16 (mesh, Dynatrace): a building's reception desk and security guards; a detective who reads
  every clue at once.
- Parts 17 to 19 (security, AI, platform): food safety labels and sealed jars; a capable but new intern whose
  work you check; a paved path through a park.

## Process

1. Read the venkat-voice skill, this file, `brief/BRIEF.md` (only the rules still apply; the reader
   description there is replaced by the one above), and your lessons in full. Skim the lesson before your
   first one.
2. Rewrite one lesson at a time with a Python script in `brief/scratch/v5/<your name>/` that loads
   `content/pN.json`, replaces that lesson's prose fields, and writes the file back. Never touch other
   writers' parts.
3. After each lesson: `python3 brief/validate.py content/pN.json`, `python3 brief/tells.py content/pN.json`,
   and `python3 brief/scratch/v5/protect.py brief/scratch/v5/orig/pN.json content/pN.json` (0 non-prose
   changes). Then `python3 site/build.py` must succeed.
4. Read each lesson from the top as the newcomer before moving on. Check the skill's "Before you hand it in"
   list.
5. No git commands. The lead commits.

## Lead's notes from the pilots (read before each lesson)

- Pace new words. At most one new term per sentence, and no more than three new terms in one paragraph. If a
  paragraph needs more, split it, or ask whether the reader needs that word today.
- Trivia that the intuition doesn't need (an acronym's expansion, an interface's name, history, a removed
  feature) moves to `deeper` or an `aside`, or goes. Moving a fact is fine; changing one is not.
- Prefer a short story over a bullet list of facts. A list is fine for steps, or for three or more parallel
  items the reader will come back to.
- Link to the previous lesson in natural words ("Last time, a careful checklist set up our servers..."), not
  by pasting its full title.
- `analogy`, `real_world` and `mistake` may be removed when the opening and sections already carry them
  (validate.py now allows that).
