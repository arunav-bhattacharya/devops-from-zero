"""Book-voice rewrite of Part 3's own fields. Run after d10.py to d14.py."""
import json, pathlib
path = pathlib.Path(__file__).resolve().parents[4] / "content/p3.json"
P = json.loads(path.read_text())

P["intro"] = ("Every deploy in this course travels over a network, and most real systems run on computers rented from someone else. "
              "Part 3 follows one message the way a letter travels. Day 10 covers names, addresses and ports, and Day 11 what the message says and the servers in the middle. Day 12 covers the rented cloud around it all. "
              "Days 13 and 14 make that cloud real: an AWS account on the Free plan, the command line, permissions, file storage and a small server of your own. "
              "They cost a few cents of credits, and without an account, every AWS command also runs on a pretend AWS on your laptop.")
P["recap"] = [
    "An IP address finds the machine and a port finds the program; private addresses reach the internet through NAT.",
    "/N fixes N bits: /24 holds 256 addresses and /16 holds 65,536; apps in containers bind to 0.0.0.0.",
    "DNS walks from your resolver to root, TLD and authoritative servers, and caches each answer for its TTL.",
    "Unresolved means DNS, refused means no listener, and a timeout means a drop or a wrong address.",
    "HTTP is text with methods, headers and status codes; TLS seals it and proves the server's name.",
    "A reverse proxy ends TLS and spreads the load, and 502, 503 and 504 usually come from it.",
    "In the cloud, route tables make subnets public or private; security groups are stateful and NACLs are not.",
    "On AWS: Free plan, root MFA and a zero-spend budget first; people get short-lived logins and programs get roles.",
    "An IAM policy is Effect, Action, Resource and Condition; calls start denied, and any Deny wins.",
    "A server should install itself with user data and systemd, be reached through Session Manager, and be terminated when done.",
]
fronts = {
    "401 or 403?": "401 or 403: what is the difference?",
    "502 or 504?": "502 or 504: what is the difference?",
    "Layer 4 or layer 7 load balancer?": "Layer 4 or layer 7 load balancer: what does each see?",
    "Security group or network ACL?": "Security group or network ACL: how do they differ?",
}
backs = {
    "What does NAT do in your home router?": "It swaps your private source address for its own public one on the way out, remembers the swap, and reverses it for replies.",
    "401 or 403?": "401: who are you? (credentials missing or wrong). 403: I know you, and you may not do this.",
}
for f in P["flashcards"]:
    old = f["front"]
    if old in backs:
        f["back"] = backs[old]
    f["front"] = fronts.get(old, old)
qs = {
    0: ("An app in a container listens on 127.0.0.1:8000. You run it with `-p 8000:8000` and curl localhost:8000 on your Mac. What happens?",
        "Docker forwards to the container's network address, and an app bound to the container's own loopback never sees that traffic."),
    2: ("You changed an A record (a name-to-address answer in DNS) whose TTL is 3600. Twenty minutes later, some users still reach the old server. Why?",
        "Resolvers may reuse a remembered answer until its TTL of one hour runs out."),
}
for i, (q, w) in qs.items():
    P["quiz"][i]["q"], P["quiz"][i]["why"] = q, w
res = {
    "How DNS works (Computerphile)": "A clear whiteboard walk through resolvers, root servers and caching, in plain words.",
    "TLS handshake explained (Computerphile)": "Mike Pound draws the TLS handshake and the key exchange on paper, one message at a time.",
    "AWS Certified Cloud Practitioner course, CLF-C02 (freeCodeCamp)": "A long, free course on the core AWS services; the parts on regions, VPCs, IAM, EC2 and billing match this part.",
}
for r in P["resources"]:
    if r["title"] in res:
        r["why"] = res[r["title"]]
path.write_text(json.dumps(P, indent=1, ensure_ascii=False) + "\n")
print("p3 part fields written")
