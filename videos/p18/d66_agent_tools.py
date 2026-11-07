import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

# how the voice says this video's terms (spoken text only; captions keep the spelling)
SAY.extend([(r"\btools/(list|call)\b", r"tools \1"), (r"\bstdio\b", "standard I O"), (r"\bJSON-RPC\b", "jay-son R P C"),
            (r"\bpods_list_in_namespace\b", "pods list in namespace"), (r"\bread_only\b", "read only")])


def person(color=GREY_B):
    head = Circle(radius=0.16, stroke_color=color, stroke_width=3).set_fill(BLACK, 1)
    body = Arc(radius=0.3, start_angle=0, angle=PI, stroke_color=color, stroke_width=3).next_to(head, DOWN, buff=0.05)
    return VGroup(head, body)


class D66AgentTools(VoiceScene):
    def construct(self):
        self.title_card("AI agents that run tools", "the loop, MCP, and where the guardrails sit")

        # ---------- 1. the model only writes text; the host does the rest
        model = box("Model", BLUE_M, w=2.2).move_to([-5.0, 2.3, 0])
        mcap = T("only writes text", 22, BLUE_M).next_to(model, DOWN, buff=0.15)
        host = box("Agent host", GOLD_M, w=2.7).move_to([0.0, 2.3, 0])
        hcap = T("Claude Code, Copilot in VS Code", 22, GOLD_M).next_to(host, DOWN, buff=0.15)
        kapi = box("Kubernetes API", GREY_B, w=2.8, size=26).move_to([5.0, 2.3, 0])
        self.beat("An AI agent is a model in a loop that uses tools. But the model inside only produces text.",
                  Create(model[0]), Write(model[1]), FadeIn(mcap), run_time=2.0)
        nope = VGroup(M("kubectl", 24, GREY_B), tick(False, 0.22)).arrange(RIGHT, buff=0.2).move_to([-5.0, 0.6, 0])
        self.beat("It cannot open a network connection, or start kubectl by itself.",
                  FadeIn(nope[0]), Succession(Wait(0.8), Create(nope[1])), run_time=1.8)
        self.beat("The program around it, called the host, does that part. That is the agent you install, such as Claude Code, or Copilot in VS Code.",
                  FadeOut(nope), Create(host[0]), Write(host[1]), Succession(Wait(1.6), FadeIn(hcap)), run_time=3.4)

        # the conversation, as a row of blocks
        clab = T("conversation", 22, GREY_B).move_to([-6.4, 0.95, 0], aligned_edge=LEFT)
        X0, W, G = -6.4, 1.22, 0.08

        def block(label, col, i):
            c = chip(label, col, 20)
            c[0].stretch_to_fit_width(W)
            return c.move_to([X0 + W / 2 + i * (W + G), 0.4, 0])
        conv = [block("goal", YELLOW_M, 0), block("tools", GREY_B, 1)]
        goal = T("“Why does hello-devops keep restarting?”", 28, YELLOW_M).move_to([0, -1.1, 0])
        tl = VGroup(M("pods_list_in_namespace   list the Pods in a namespace   namespace", 20),
                    M("pods_log                 read a container's logs        name", 20),
                    M("…", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0, -2.3, 0])
        tlh = VGroup(T("name", 20, GREY_B), T("description", 20, GREY_B), T("arguments", 20, GREY_B))
        for h, x in zip(tlh, (tl[0][0].get_left()[0], tl[0][0].get_left()[0] + 25 * 0.144, tl[0][0].get_left()[0] + 56 * 0.144)):
            h.move_to([x, -1.65, 0], aligned_edge=LEFT)
        a_hm = Arrow(host.get_left() + UP * 0.2, model.get_right() + UP * 0.2, buff=0.12, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.06)
        a_mh = Arrow(model.get_right() + DOWN * 0.2, host.get_left() + DOWN * 0.2, buff=0.12, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.06)
        self.beat("On every call, the host sends the model your goal, the conversation so far, and a list of tools.",
                  FadeIn(clab), FadeIn(conv[0], shift=DOWN * 0.1), FadeIn(goal, shift=UP * 0.1), Succession(Wait(1.6), FadeIn(conv[1], shift=DOWN * 0.1)),
                  GrowArrow(a_hm), run_time=3.2)
        self.play(travel(a_hm, GOLD_M), run_time=0.8)
        self.beat("Each tool is plain text too: a name, a short description, and the arguments it takes.",
                  FadeIn(tlh), LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in tl], lag_ratio=0.3), run_time=2.6)

        call = VGroup(M("pods_list_in_namespace", 24, GOLD_M), M("namespace: hello", 24, WHITE)).arrange(RIGHT, buff=0.5).move_to([0, -1.1, 0])
        self.beat("The model replies with text. To use a tool, it writes a tool call in a fixed format: pods_list_in_namespace, with namespace hello.",
                  FadeOut(VGroup(tl, tlh, goal)), GrowArrow(a_mh), Succession(Wait(1.2), travel(a_mh, BLUE_M, run_time=0.9), FadeIn(call, shift=UP * 0.1)), run_time=4.2)
        conv.append(block("call", GOLD_M, 2))
        a_hk = Arrow(host.get_right() + UP * 0.2, kapi.get_left() + UP * 0.2, buff=0.12, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.06)
        a_kh = Arrow(kapi.get_left() + DOWN * 0.2, host.get_right() + DOWN * 0.2, buff=0.12, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.06)
        cred = chip("your credentials", GREY_B, 20).next_to(a_hk, UP, buff=0.12)
        appr = chip("approve?", GREEN_M, 20).next_to(host, UP, buff=0.15)
        self.beat("The host spots the tool call, asks for your approval if needed, and runs the tool, with the credentials you configured.",
                  FadeIn(conv[2], shift=DOWN * 0.1), Succession(Wait(0.8), FadeIn(appr, shift=DOWN * 0.1), Wait(0.6),
                  AnimationGroup(Create(kapi[0]), Write(kapi[1]), GrowArrow(a_hk), FadeIn(cred)), travel(a_hk, GOLD_M, run_time=0.8)), run_time=4.6)
        res = M("result: 2 Pods, 1 restarting", 24, GREEN_M).move_to([0, -1.1, 0])
        conv.append(block("result", GREEN_M, 3))
        self.beat("Then it adds the result to the conversation, as text, and calls the model again.",
                  FadeOut(appr), GrowArrow(a_kh), Succession(travel(a_kh, GREEN_M, run_time=0.8), AnimationGroup(Transform(call, res), FadeIn(conv[3], shift=DOWN * 0.1)),
                  travel(a_hm, GOLD_M, run_time=0.8)), run_time=3.4)
        whole = VGroup(*[c for c in conv])
        ghost = whole.copy()
        self.beat("The model keeps no memory between calls. Each call carries the whole conversation again, tool results included.",
                  Indicate(whole, color=YELLOW_M, scale_factor=1.03), Succession(Wait(1.2), ghost.animate(run_time=1.4).move_to(model).scale(0.25).set_opacity(0)), run_time=3.6)
        self.remove(ghost)

        # more steps, then the answer
        steps = T("model calls: 2", 24, GREY_B).move_to([4.6, -1.1, 0])
        self.play(FadeOut(call), FadeIn(steps), run_time=0.5)
        for i, (l, c) in enumerate([("call", GOLD_M), ("result", GREEN_M), ("call", GOLD_M), ("result", GREEN_M)]):
            conv.append(block(l, c, 4 + i))
        seq = []
        for k, b in enumerate(conv[4:8]):
            a = [FadeIn(b, shift=DOWN * 0.1)]
            if k % 2 == 1:
                a.append(Transform(steps, T(f"model calls: {3 + k // 2}", 24, GREY_B).move_to([4.6, -1.1, 0])))
            seq.append(AnimationGroup(*a))
        self.beat("So it reads the events, then fetches the logs of the restarting container. One step at a time, the same loop.",
                  Succession(*seq), run_time=4.2)
        conv.append(block("answer", BLUE_M, 8))
        ans = T("a reply with no tool call is the answer: the loop stops", 26, BLUE_M).move_to([-0.8, -1.1, 0])
        self.beat("When a reply has no tool call in it, that reply is the answer, and the loop stops.",
                  travel(a_mh, BLUE_M, run_time=0.8), FadeIn(conv[-1], shift=DOWN * 0.1), FadeIn(ans, shift=UP * 0.1), run_time=2.6)
        cost = VGroup(*[Rectangle(width=0.36, height=0.18 * (k + 1), stroke_width=0).set_fill(GOLD_M, 0.75) for k in range(5)]).arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
        cost.move_to([-3.0, -2.75, 0])
        costl = T("text sent per call", 22, GOLD_M).next_to(cost, RIGHT, buff=0.3).align_to(cost, DOWN)
        caps = VGroup(chip("timeout on every CI job", RED_M, 22), chip("spending limit on every API key", RED_M, 22))
        self.beat("One question can mean dozens of calls, and each call resends the whole conversation, so later steps cost more.",
                  FadeOut(ans), LaggedStart(*[GrowFromEdge(b, DOWN) for b in cost], lag_ratio=0.25), FadeIn(costl), run_time=3.4)
        caps.arrange(DOWN, buff=0.15, aligned_edge=LEFT).move_to([4.4, -2.65, 0])
        self.beat("So cap every run: a timeout on every CI job, and a spending limit on every API key.",
                  Circumscribe(steps, color=RED_M), LaggedStart(*[FadeIn(c, shift=LEFT * 0.15) for c in caps], lag_ratio=0.4), run_time=2.8)

        # ---------- 2. MCP: one plug between agents and tools
        part1 = VGroup(model, mcap, host, hcap, kapi, a_hm, a_mh, a_hk, a_kh, cred, clab, *conv, steps, cost, costl, caps)
        self.play(FadeOut(part1), run_time=0.8)
        agents = VGroup(*[box(f"agent {i + 1}", BLUE_M, w=1.8, h=0.6, size=22) for i in range(5)]).arrange(DOWN, buff=0.28).move_to([-4.6, -0.1, 0])
        systems = VGroup(*[box(n, GREY_B, w=2.2, h=0.6, size=22) for n in ("GitHub", "Kubernetes", "Grafana", "AWS")]).arrange(DOWN, buff=0.45).move_to([4.6, -0.1, 0])
        glue = VGroup(*[Line(a.get_right(), s.get_left(), stroke_width=1.5, color=GREY_D) for a in agents for s in systems])
        n20 = T("20 pieces of glue code", 28, RED_M).move_to([0, 3.2, 0])
        self.beat("Where does the tool list come from? Without a standard, five agents and four systems need twenty pieces of glue code.",
                  LaggedStart(*[FadeIn(a, shift=RIGHT * 0.1) for a in agents], lag_ratio=0.1), LaggedStart(*[FadeIn(s, shift=LEFT * 0.1) for s in systems], lag_ratio=0.1),
                  Succession(Wait(1.6), AnimationGroup(Create(glue, lag_ratio=0.05), FadeIn(n20))), run_time=4.4)
        bar = RoundedRectangle(corner_radius=0.12, width=1.0, height=4.6, stroke_color=YELLOW_M, stroke_width=3).set_fill(interpolate_color(ManimColor("#000000"), ManimColor(YELLOW_M), 0.15), 1).move_to([0, -0.1, 0])
        barl = T("MCP", 28, YELLOW_M).rotate(PI / 2).move_to(bar)
        nine = VGroup(*[Line(a.get_right(), [bar.get_left()[0], a.get_center()[1], 0], stroke_width=2.5, color=BLUE_M) for a in agents],
                      *[Line([bar.get_right()[0], s.get_center()[1], 0], s.get_left(), stroke_width=2.5, color=GREY_B) for s in systems])
        n9 = T("9 pieces: one per agent, one server per system", 28, GREEN_M).move_to([0, 3.2, 0])
        self.beat("With a shared protocol, each agent speaks it once, and each system gets one server: nine pieces. That protocol is the Model Context Protocol, MCP.",
                  FadeOut(glue), GrowFromCenter(bar), Write(barl), Create(nine), Transform(n20, n9), run_time=4.0)

        self.play(FadeOut(VGroup(agents, systems, bar, barl, nine, n20)), run_time=0.8)
        model = box("Model", BLUE_M, w=1.6).move_to([-5.6, 0.6, 0])
        hfr = RoundedRectangle(corner_radius=0.18, width=3.0, height=3.6, stroke_color=GOLD_M, stroke_width=3).move_to([-1.6, 0.6, 0])
        hl = T("host", 26, GOLD_M).move_to(hfr.get_top() + DOWN * 0.35)
        c1 = box("client", GOLD_M, w=1.8, h=0.65, size=24).move_to([-1.6, 1.3, 0])
        c2 = box("client", GOLD_M, w=1.8, h=0.65, size=24).move_to([-1.6, -0.4, 0])
        s1 = box("Kubernetes server", TEAL_M, w=3.0, h=0.75, size=24).move_to([2.45, 1.3, 0])
        s2 = box("GitHub server", TEAL_M, w=3.0, h=0.75, size=24).move_to([2.45, -0.4, 0])
        api = box("API server", GREY_B, w=1.9, h=0.75, size=24).move_to([5.45, 1.3, 0])
        l1 = Line(c1.get_right(), s1.get_left(), stroke_width=3, color=GREY_B)
        l2 = Line(c2.get_right(), s2.get_left(), stroke_width=3, color=GREY_B)
        self.beat("Inside the host, one MCP client talks to each server. A server wraps one system, such as a Kubernetes cluster, or GitHub.",
                  Create(model[0]), Write(model[1]), Create(hfr), FadeIn(hl), Create(c1[0]), Write(c1[1]), Create(c2[0]), Write(c2[1]),
                  Succession(Wait(1.4), AnimationGroup(Create(l1), Create(l2), Create(s1[0]), Write(s1[1]), Create(s2[0]), Write(s2[1]))), run_time=4.4)
        tlq = VGroup(M("tools/list", 22, YELLOW_M).next_to(l1, UP, buff=0.1), M("tools/list", 22, YELLOW_M).next_to(l2, UP, buff=0.1))
        lst = VGroup(M("pods_list_in_namespace", 20, TEAL_M), M("pods_log", 20, TEAL_M), M("…", 20, TEAL_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        lst2 = VGroup(M("GitHub tools …", 20, TEAL_M))
        merged = VGroup(lst.copy(), lst2.copy()).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        mfr = SurroundingRectangle(merged, buff=0.15, corner_radius=0.08, color=YELLOW_M, stroke_width=2).set_fill(BLACK, 1)
        mlist = VGroup(mfr, merged).move_to([-5.0, -1.95, 0])
        mll = T("one tool list", 22, YELLOW_M).next_to(mlist, DOWN, buff=0.12)
        self.beat("Each client asks its server for its tools, with a tools/list request. The host merges the answers into the one list it sends the model.",
                  FadeIn(tlq), Succession(AnimationGroup(travel(l1, YELLOW_M, run_time=0.8), travel(l2, YELLOW_M, run_time=0.8)),
                                          Wait(1.0), AnimationGroup(FadeIn(mlist, shift=LEFT * 0.3), FadeIn(mll))), run_time=4.6)
        tc = M("tools/call", 22, GOLD_M).next_to(l1, UP, buff=0.1)
        a_ma = Arrow(model.get_right(), c1.get_left(), buff=0.15, stroke_width=3, color=BLUE_M, max_tip_length_to_length_ratio=0.12)
        l3 = Line(s1.get_right(), api.get_left(), stroke_width=3, color=GREY_B)
        self.beat("When the model writes a tool call, the host passes it to the right client, which sends tools/call.",
                  FadeOut(tlq), GrowArrow(a_ma), Succession(travel(a_ma, BLUE_M, run_time=0.8), FadeIn(tc), travel(l1, GOLD_M, run_time=0.8)), run_time=3.6)
        self.beat("The server does the real work, such as a request to the Kubernetes API, and returns the result.",
                  Create(api[0]), Write(api[1]), Create(l3), Succession(Wait(0.6), travel(l3, GOLD_M, run_time=0.6), travel(Line(l3.get_end(), l3.get_start()), GREEN_M, run_time=0.6),
                                                                        travel(Line(l1.get_end(), l1.get_start()), GREEN_M, run_time=0.8)), run_time=3.6)
        tp1 = T("stdio: a local child process", 22, GREY_B).next_to(s1, DOWN, buff=0.15)
        tp2 = T("Streamable HTTP: a remote server", 22, GREY_B).next_to(s2, DOWN, buff=0.15)
        jr = M("JSON-RPC 2.0", 22, YELLOW_M).move_to([2.45, 2.6, 0])
        self.beat("The messages are JSON-RPC 2.0. A local server talks over stdio. A remote one, over Streamable HTTP.",
                  FadeIn(jr), Succession(Wait(1.6), FadeIn(tp1, shift=UP * 0.1), Wait(0.6), FadeIn(tp2, shift=UP * 0.1)), run_time=3.8)

        # ---------- 3. where the guardrails sit
        self.play(FadeOut(VGroup(tp1, tp2, jr, tc, mlist, mll)), run_time=0.6)
        g_host = SurroundingRectangle(hfr, buff=0.08, color=GREEN_M, stroke_width=4)
        consent = chip("your consent before any tool runs", GREEN_M, 22).move_to([-1.6, -1.75, 0])
        self.beat("So where do the guardrails sit? Not in the model. The MCP specification says the protocol cannot enforce security. It puts that job on the host, which must get your consent before it runs any tool.",
                  Succession(Wait(3.0), AnimationGroup(Create(g_host), FadeIn(consent, shift=UP * 0.1))), run_time=6.0)
        self.play(FadeOut(g_host), run_time=0.4)
        tok = chip("ai-agent token: 1 hour, read-only RBAC", GREEN_M, 22).move_to([3.9, 2.55, 0])
        a_tok = Arrow(tok.get_bottom(), l3.get_center() + UP * 0.08, buff=0.06, stroke_width=3, color=GREEN_M, max_tip_length_to_length_ratio=0.25)
        self.beat("Next, the credentials. A tool can do only what its credentials allow, whatever the model asks for. In the lab, the Kubernetes server signs in as the ai-agent ServiceAccount: read-only in hello, with a token that expires in an hour.",
                  Succession(Wait(3.6), AnimationGroup(FadeIn(tok, shift=DOWN * 0.1), GrowArrow(a_tok))), run_time=7.0)
        ro = M("read_only = true", 22, TEAL_M).next_to(s1, DOWN, buff=0.15)
        ro_n = T("hides write tools: best effort", 22, TEAL_M).next_to(ro, DOWN, buff=0.1)
        self.beat("The server's read_only setting hides the tools that write. Its own docs call that a best-effort guardrail.",
                  FadeIn(ro, shift=UP * 0.1), Succession(Wait(1.6), FadeIn(ro_n, shift=UP * 0.1)), run_time=3.6)
        dele = M("kubectl delete deploy redis", 22, RED_M).move_to([3.4, -2.4, 0])
        forb = M("Error from server (Forbidden)", 22, RED_M).next_to(dele, DOWN, buff=0.15)
        lk = SurroundingRectangle(api, buff=0.1, color=RED_M, stroke_width=4)
        rb = T("RBAC decides", 22, RED_M).next_to(api, DOWN, buff=0.2)
        self.beat("The API server checks every call against the token's RBAC. A delete is refused there, Forbidden. That is the lock that holds.",
                  FadeIn(dele, shift=UP * 0.1), Succession(Wait(1.6), AnimationGroup(Create(lk), FadeIn(rb), FadeIn(forb, shift=UP * 0.1))), run_time=4.4)

        # a person approves writes
        self.play(FadeOut(VGroup(dele, forb, ro_n)), run_time=0.5)
        dlg_rows = VGroup(T("The agent wants to run:", 22), M("scale deploy redis --replicas=0", 20, YELLOW_M),
                          VGroup(chip("approve", GREEN_M, 20), chip("deny", RED_M, 20)).arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.2)
        dlg_fr = RoundedRectangle(corner_radius=0.12, width=dlg_rows.width + 0.5, height=dlg_rows.height + 0.45, stroke_color=WHITE, stroke_width=2.5).set_fill(BLACK, 1)
        dlg = VGroup(dlg_fr, dlg_rows.move_to(dlg_fr)).move_to([3.4, -2.35, 0])
        who = person().next_to(dlg, LEFT, buff=0.35)
        self.beat("Then a person decides. Keep the approval prompts on for commands that change things, and route changes through a pull request.",
                  FadeIn(dlg, shift=UP * 0.15), FadeIn(who), Succession(Wait(2.4), Indicate(dlg_rows[2][1], color=RED_M, scale_factor=1.15)), run_time=4.4)
        unt = chip("untrusted text in: no writes, no secrets", GOLD_M, 22).move_to([-3.6, -2.75, 0])
        self.beat("And an agent that reads untrusted text, such as an issue or a log line, gets no write access and no secrets.",
                  FadeIn(unt, shift=UP * 0.1), run_time=2.4)

        # ---------- recap
        rc = T("the model only asks  ·  the host runs the tool  ·  the token sets the limit", 28, YELLOW_M).move_to([0, 3.25, 0])
        self.beat("The model only asks. The host runs the tool, MCP carries the call, and the token's rights set the limit.",
                  Write(rc), Indicate(tok, color=GREEN_M, scale_factor=1.06), run_time=3.4)
        self.wait(1.0)
