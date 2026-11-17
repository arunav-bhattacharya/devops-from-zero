"""Book-voice rewrite of d13 (fifth edition). Run: python3 brief/scratch/v5/tb/d13.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply import apply

opening = """Picture checking into a hotel for a long stay. The desk hands you two things: a master key that opens every door in the building, and a bill that grows every night. A sensible guest locks the master key in the safe, asks for an ordinary key card, and glances at the bill each morning.

Many cloud tutorials skip all of that. They start with "create an access key", a password for programs that never expires, because it is the quickest way to make the first command work. It does work. It also works for anyone who later finds it in a file or an old commit.

Last time, you designed a cloud network on paper. Today the account becomes real.

In this lesson, we'll open an AWS account that cannot surprise you with a bill and lock away its master key. Then we'll sign in from the terminal without a stored key, read a permission file line by line, and store, share and delete files in S3. Before we start, make a guess, and keep it in mind."""

guess = {
    "q": "You create an access key, a password for programs, for an AWS user and save it in the file ~/.aws/credentials. When does that key stop working?",
    "why": "An access key is long-lived: it works until someone deactivates or deletes it, for you and for anyone who copies it. Today's login uses `aws login` instead, whose credentials expire on their own.",
}

terms_plain = [
    "The email login an AWS account was opened with. It can do anything, including close the account.",
    "A named identity inside one account for one person, with its own password, MFA and permissions.",
    "An ID and a secret that sign requests to AWS. A long-lived one works until someone deletes it.",
    "An access key, a secret and a session token that stop working by themselves after a set time.",
    "AWS's single sign-on for people: one browser login gives short-lived access to each account and role.",
    "Amazon Resource Name: the full unique name of an AWS resource, such as arn:aws:s3:::my-bucket.",
    "The part of an IAM role that says who may assume the role.",
    "A link to one private file in S3 that works without a login until it expires.",
]

s1 = """Today you get a real AWS account, Amazon's cloud from the last lesson. The first choice comes during sign-up. Since July 15, 2025, every new account picks one of two plans:

- The Free plan gives you $100 in credits, plus up to $100 more for trying five services. It ends after six months or when the credits are used up, whichever comes first. It never charges your card.
- The Paid plan starts with the same credits, but once they are gone, you pay for what you use.

Pick the Free plan for this course. When it ends, the account closes instead of sending a bill. AWS keeps your data for 90 days after that, and upgrading in that window brings the account back.

Sign-up asks for an email address, a password, a card and a phone number for a verification code. AWS does not charge the card while you stay on the Free plan; it is there in case you upgrade later.

A few actions move a Free plan account to the Paid plan automatically, and your Free Tier credits end at once. Two of them are joining AWS Organizations and setting up an AWS Control Tower landing zone. Both are for companies that manage many accounts, and this course needs neither. Accounts opened before July 15, 2025 stay on the older 12-month free tier, which can bill you. So the budget in the next section matters even more there.

The extra $100 comes from five tasks in the Explore AWS panel on the console's home page, worth $20 each. The console is AWS's website for managing your account. One task is creating a cost budget, which costs nothing, so start with that one. Some of the others, such as launching a server, spend a little of your credits.

You are checked in. Next, before anything else, the master key goes into the safe."""

s2 = """The email address you signed up with is the root user, the hotel's master key. It can do anything in the account, including closing it, and no permission rule can limit it. You protect it once and then put it away:

1. Turn on MFA for it. MFA (multi-factor authentication) is a second proof on top of the password, such as your fingerprint. AWS now requires MFA for the root user of every account. A passkey (Touch ID on your Mac) or an authenticator app (a phone app that shows changing codes) both work. You can register up to eight devices, so add a spare.
2. Never create access keys for it.
3. Create your everyday IAM user (next section), sign out, and keep root for the rare account-level task, such as changing the plan.

Then, before you create anything else, set a budget. In the console, open Billing and Cost Management, then Budgets, and pick the template called Zero spend budget. AWS describes it as a budget that notifies you once your spending exceeds the AWS Free Tier limits. Give it your email address and create it. That is also the $20 task from the Explore AWS panel.

**A budget is an alarm, not a brake. Deleting is what stops the bill.**

As the last lesson said, it sends an email and stops nothing. Its numbers lag too: AWS refreshes budget data up to three times a day, so an alert can arrive hours after the spending. What protects you is deleting things the same day, which is why both AWS lessons end with a cleanup script. Budgets without actions cost nothing, so a second one from the Monthly cost budget template, set to $5, is a cheap extra alarm.

With the master key locked away, you need an ordinary key card for daily work. Next, we'll see how people and programs each get one."""

s3 = """Every request to AWS, from the console or a program, is checked against credentials: an access key ID, a secret and, for temporary credentials, a session token. The CLI, AWS's command-line tool, never sends the secret itself. It uses it to sign each request, and AWS checks the signature with its own copy of the secret. The safe rule is about where credentials come from:

- People sign in through a browser and get short-lived credentials.
- Programs, such as a server or a CI job (the robot that tests each change), assume an IAM role and never hold a stored key.
- A long-lived access key is the last resort. It works for whoever holds it, copied from a laptop, a log or a git repo, until someone deletes it.

**People sign in, and programs assume roles. Neither should need a stored key.**

At work you will meet IAM Identity Center, AWS's single sign-on. Your company login opens a portal with every account and role you may use. You connect the CLI once with `aws configure sso`, which asks for, in order:

1. A session name of your choice.
2. The start URL of the portal, shaped like `https://d-xxxxxxxxxx.awsapps.com/start`.
3. The SSO region, then the registration scopes (keep the default).
4. Your approval in the browser window it opens.
5. The account, the role, a default region and an output format.
6. A profile name. It suggests the role and account, such as `AdministratorAccess-123456789012`.

After that, `aws sso login --profile NAME` signs you in for the day.

On your own Free plan account there is a catch. Identity Center gives access to AWS accounts only through an organization instance, which needs AWS Organizations, and that ends the Free plan. Its smaller account instance cannot give access to accounts at all.

So today you make an IAM user, your own key card, with a console password, MFA and the AdministratorAccess policy. It is your own sandbox, so admin rights are reasonable. Then `aws login`, in CLI 2.32.0 or later, signs the CLI in through the browser with that same login. It is a day pass printed from your key card. It stores temporary credentials and refreshes them every 15 minutes, and no key ever lands on your disk. A user without admin rights needs the AWS managed policy `SignInLocalDevelopmentAccess` for it.

Programs get roles: Day 14 gives a server one through an instance profile, and Days 27 and 35 give GitHub Actions one through OIDC.

You have a login. Next, we'll put the CLI to work and learn the three habits that prevent most confusion."""

s4 = """Install the CLI with `brew install awscli`, which is version 2, and check it with `aws --version`. Homebrew, the Mac's package installer from Day 2, provides `brew`. AWS also publishes a Mac installer package; check its install page if Homebrew is not an option. If you only have a browser, AWS CloudShell is a terminal inside the console, already signed in as you. It is free.

Settings live in named profiles in `~/.aws/config`. A profile is a saved set of settings with a name. `aws login --profile learn` creates one called learn. Pick it for one command with `--profile learn`, or for the whole terminal with `export AWS_PROFILE=learn` (an environment variable, as in Day 7).

Three habits prevent most confusion:

- Ask who you are. `aws sts get-caller-identity` prints the account and identity the CLI is using right now. STS is the AWS service that hands out temporary credentials. If the ARN ends in `:root`, stop and sign in as your IAM user.
- Know your region. Each region has its own API address, such as `ec2.eu-central-1.amazonaws.com`, so each command goes to one region. It comes from `--region`, then `AWS_REGION`, then the profile. A bucket or server in another region is invisible from this one, and it still bills.
- Shape the output. The `--output` option takes json, yaml, text or table. The `--query` option takes JMESPath, a small language for picking fields out of JSON, and runs on your laptop after the answer arrives.

For example, `--query Account --output text` prints only the 12-digit number, ready for a shell variable. The jq tool from Day 5 works too, and it is better at heavy reshaping. The `--query` option needs nothing installed, so it also works in CloudShell and on servers.

Some EC2 commands accept `--dry-run`. AWS checks your permissions and the request, then refuses with `DryRunOperation` if the call would have worked. Day 14 launches its server that way first. When AWS returns an error, the CLI exits with 254, so a script with `set -e` (Day 7) stops at the failing line.

Who you are is only half the question. The other half is what you may do. Next, we'll read the list of doors on a key card."""

s5 = """An IAM policy is a JSON document that lists which doors a key card opens. Open `policies/reports-reader-permissions.json` from the lab and read it next to this list:

- `Version` is always `"2012-10-17"`, the version of the policy language. You never change it.
- `Statement` is a list of rules, each with an optional `Sid`, a label for humans.
- `Effect` is Allow or Deny.
- `Action` names API calls as `service:Action`, such as `s3:GetObject`.
- `Resource` names what the call acts on, by ARN.
- `Condition` is optional and narrows the rule further.

An ARN, short for Amazon Resource Name, has the shape `arn:aws:service:region:account:resource`. S3 bucket names are global, so bucket ARNs leave the region and account empty: `arn:aws:s3:::hello-devops-lab-123456789012`. Objects add their key, as in `.../reports/*`.

The file's first statement allows `s3:ListBucket` on the bucket, but its Condition only matches listings whose prefix starts with `reports/`. The second allows `s3:GetObject` on objects under `reports/`. Nothing allows `s3:DeleteObject`. AWS decides every call the same way: it starts from deny, a matching Allow opens the call, and an explicit Deny anywhere beats every Allow. So a delete fails.

A role carries two policies. The permissions policy, like this one, says what the role may do. The trust policy says who may assume it, the way a contractor's badge lists who may collect it at the desk. In `reports-reader-trust.json` the Principal is `arn:aws:iam::ACCOUNT_ID:root`, which means the whole account: any identity in it whose own policy allows `sts:AssumeRole`. It does not mean the root user, despite the name.

`aws sts assume-role` checks both sides, your own policy and the role's trust policy. Then it hands back temporary credentials that last an hour by default. Their access key ID starts with ASIA, while long-lived keys start with AKIA, so you can tell them apart in a log.

Two AWS tools check a policy before it bites. IAM Access Analyzer's policy validation runs over 100 checks on grammar and good practice (`aws accessanalyzer validate-policy`). The policy simulator answers "would this call be allowed?" without making the call (`aws iam simulate-custom-policy`).

Now there is something worth guarding. Next, we'll store a file, share it, and delete it again."""

s6 = """S3 (Simple Storage Service) keeps files, which it calls objects, in buckets. Picture the hotel's luggage room, where every bag gets a tag. You read and write each object whole, over HTTPS, and cannot change a few bytes in the middle as on a disk. An object's name is its key, such as `reports/2026-11-06.csv`. The slashes only look like folders. S3 has none; the console draws key prefixes as if they were.

Four rules shape what you do with it:

- Bucket names are unique across every AWS account in the world, and each name becomes part of a web address, such as `NAME.s3.amazonaws.com`. So the lab puts your account ID in the name.
- Block Public Access stops any setting from opening a bucket to the whole internet. It has four settings, and every bucket created since April 2023 starts with all four on. Leave them on. `s3-lab.sh` sets them anyway, so anyone reading the script sees the intent.
- Versioning keeps every old version of an object. Once it is on, you can suspend it but never turn it fully off. A delete then only adds a delete marker on top, and removing the marker brings the object back.
- A lifecycle rule deletes objects on a schedule. The lab's rule removes reports after 30 days, replaced versions 7 days later, and unfinished uploads after a day.

To share one private object, make a presigned URL: a link that carries a signature made with your credentials. Anyone who has the link can read that object until it expires, and from the CLI it can last up to 7 days. It also dies when the credentials that signed it expire. So a link signed with `aws login` or a role can stop working long before the time you asked for.

Deleting a versioned bucket needs one more step. The command `aws s3 rb --force` removes the current objects, but old versions and delete markers stay, and the bucket refuses to go. The lab's `cleanup.sh` deletes every version first. The few kilobytes you store today cost a tiny fraction of a cent.

All of this assumes you opened an account. If you are not ready to, there is a way to practise anyway."""

s7 = """You can learn every command from today without an account. moto is a free program that pretends to be AWS on your laptop, an emulator. Install it in a Python virtual environment (a private folder for one project's packages). Start it with `moto_server -p 5050`, and point the CLI at it: `--endpoint-url http://localhost:5050` for one command, or `export AWS_ENDPOINT_URL=http://localhost:5050` for the whole terminal. Fake keys such as `testing` are fine. The lab README has the exact steps, and every lab script runs there.

The worked example below ran on moto, and each step says where its output differs from AWS. Some things an emulator cannot teach:

- It allows every call, so you never see AccessDenied, and the policy simulator does not run.
- New buckets have no Block Public Access until you set it, and presigned URLs never expire.
- Nothing bills, so you learn nothing about cost.
- On Day 14 no server boots and no logs arrive.

LocalStack is a bigger emulator. Since March 2026 it needs a LocalStack account and an auth token, with a free plan for non-commercial use. moto needs neither, so the course uses it.

When you go back to real AWS, unset the fake keys and the endpoint, or close that terminal tab. Left behind, they quietly win over your profile, as the common mistake below shows. An emulator is a practice hotel with cardboard doors: good for learning the corridors, useless for learning which doors are locked."""

sections = [
    ("Checking in: open the account on the Free plan", s1),
    ("Put the master key in the safe, then set the alarm", s2),
    ("Key cards for people, roles for programs", s3),
    ("Talking to AWS from the terminal: profiles, regions and output", s4),
    ("Reading the list of doors: an IAM policy, and a role's two policies", s5),
    ("S3: store, share and delete a file", s6),
    ("No account yet? Practise on a pretend AWS", s7),
]

closing = """We started at a hotel desk with a master key and a growing bill. The master key is now in the safe behind MFA, and a zero-spend budget watches the bill. Your terminal signs in with a day pass that expires on its own. A role showed that a key card can open exactly one corridor, and no more.

Before any command that changes your account, run `aws sts get-caller-identity` and read which account, and which identity, it names.

Next, we'll rent a whole server of our own. How do you get a shell on a machine in the cloud without opening a door to the whole internet?"""

worked_say = [
    "Ask who you are first. On real AWS this prints your 12-digit account ID and `user/learner`; on moto every account is 123456789012 and the user is moto. Keep the ID in a shell variable, because the bucket name needs it.",
    "Create the bucket and ask for its Block Public Access settings. Here moto differs from AWS: real S3 answers with all four settings on, while moto has none until you set them. Setting them yourself is a good habit either way, and it prints nothing when it works.",
    "Upload a small CSV file (a table as plain text) straight from a pipe: the `-` means read from standard input (Day 5). `--summarize` adds the totals to the listing.",
    "Share it for five minutes. Our test ran moto on port 5013, while yours runs on 5050. The presigned URL works with no login at all, while the plain URL gets 403. On real AWS the URL starts with `https://hello-devops-lab-...s3.amazonaws.com`, and after five minutes it returns 403 too; moto never checks the expiry.",
    "Turn on versioning, overwrite the report, then delete it by mistake. The listing shows two versions and a delete marker on top. The first upload came before versioning, so its version ID is `null`, on AWS too. moto's other IDs look like UUIDs; real ones are longer random strings.",
    "Undo the delete by deleting the marker, and the newest version is back. Then add the lifecycle rule from the lab and read it back as a table.",
    "Now try to remove the bucket the quick way. The `--force` flag deletes the current object, which in a versioned bucket only adds one more marker, and the old versions keep the bucket alive. The lab's `cleanup.sh` lists every version and marker, deletes them, and then the bucket goes.",
]

recap = [
    "Pick the Free plan: when credits or six months run out, the account closes instead of billing.",
    "Lock the root user with MFA, give it no keys, and set a zero-spend budget before anything else.",
    "People sign in for short-lived credentials (`aws login`, or `aws configure sso` at work); programs use roles.",
    "A policy is Effect, Action, Resource and Condition; calls start denied and any Deny wins.",
    "A role has a trust policy (who may assume it) and a permissions policy (what it may do).",
    "The limits: a budget only warns, an emulator allows every call, and a versioned bucket must lose every version before it goes.",
]

deeper = {"body": """Every AWS CLI command, and every SDK such as boto3 on Day 16, looks for credentials in a fixed order and stops at the first it finds. Simplified:

1. Options on the command line, such as `--profile`.
2. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN`.
3. The chosen profile in `~/.aws/config` and `~/.aws/credentials`: a login session, an SSO session, a role to assume, or stored keys.
4. On AWS itself, the container's or the server's role (Day 14).

`aws configure list` shows what the CLI would use and where each value came from. Picture test keys left in the environment, and a profile called learn that holds a different key. With `AWS_PROFILE=learn` exported, the access key's TYPE column says `env`: the leftover variables win. With `--profile learn` on the command line, the TYPE says `config-file`. The CLI treats a profile named on the command line as an explicit choice and skips the key variables, while `AWS_PROFILE` gets no such priority. That difference explains a lot of confusing "but I logged in" moments.

Some tools, especially older ones, do not understand `aws login` or SSO profiles yet. For them, `aws configure export-credentials --profile learn --format env` prints `export` lines with the profile's current temporary keys. Run it inside `eval "$(...)"` and that terminal has plain variables the old tool can read. They expire like any temporary credentials, so you repeat it later. Another way is a profile with a `credential_process` line, which tells a tool to run a command whenever it needs credentials.

The CLI caches temporary credentials in `~/.aws/login/cache` for `aws login` and in `~/.aws/sso/cache` for SSO. They expire, but until then they are as powerful as your login. Keep the folder private and out of container images, and remember that `aws logout` clears the login cache.

Last, the habit that ties this together: run `aws sts get-caller-identity` before anything that changes your account. It costs nothing and answers the only question that matters before a delete: which account, and as whom. (STS, by the way, stands for Security Token Service.)"""}

apply(3, "d13", {
    "goal": "By the end you can open an AWS account that cannot surprise you with a bill, sign in to the AWS CLI without a stored key, read an IAM policy line by line, and create, share and delete an S3 bucket from your terminal.",
    "opening": opening,
    "guess": guess,
    "terms_plain": terms_plain,
    "sections": sections,
    "diagram_caption": "aws login turns your browser sign-in into temporary keys; IAM then checks each request and allows it or denies it.",
    "worked_say": worked_say,
    "recap": recap,
    "closing": closing,
    "check": [{}, {}, {}],
    "interview": [{}, {}, {}],
    "deeper": deeper,
    "drop": ["analogy"],
})
print("d13 written")
