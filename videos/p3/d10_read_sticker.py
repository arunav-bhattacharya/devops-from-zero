import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([
    (r"172\.20\.0\.2", "172 dot 20 dot 0 dot 2"), (r"127\.0\.0\.1", "127 dot 0 dot 0 dot 1"), (r"\bnc -zv\b", "N C dash Z V"),
    (r"\bgetaddrinfo\b", "get adder info"), (r"\bdb\.internal\b", "D B dot internal"), (r"/etc/hosts", "slash etc slash hosts"),
    (r"\bICMP\b", "I C M P"), (r"\bdig\b", "dig"), (r"\bshopnet\b", "shop net"), (r"\bRedis\b", "reddis"),
    (r"\b6379\b", "six three seven nine"), (r"\b6380\b", "six three eight zero"), (r"\b5432\b", "five four three two"),
])

APP, DNSC, ROAD, DOOR, STK = BLUE_M, PURPLE_M, GREY_B, TEAL_M, YELLOW_M
ROAD_Y = -0.35
APP_P = np.array([-5.2, ROAD_Y, 0])
BOOK_P = np.array([-1.7, 1.95, 0])
MACH_P = np.array([3.95, ROAD_Y, 0])


def tint(c, a=0.14):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), a)


def sticker(top, err, color=STK, w=3.6):
    a = fit(T(top, 26, BLACK), w - 0.3)
    r = RoundedRectangle(corner_radius=0.06, width=w, height=1.15 if err else 0.8, stroke_width=0).set_fill(color, 1)
    if not err:
        return VGroup(r, a.move_to(r)).rotate(-4 * DEGREES)
    b = M(err, 22, BLACK)
    fit(b, w - 0.3)
    VGroup(a, b).arrange(DOWN, buff=0.12).move_to(r)
    return VGroup(r, a, b).rotate(-4 * DEGREES)


def parcel(color=GOLD_M, s=1.0):
    b = Rectangle(width=0.62, height=0.44, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), 1)
    f = VMobject(stroke_color=color, stroke_width=2.5).set_points_as_corners([b.get_corner(UL), b.get_center() + DOWN * 0.04, b.get_corner(UR)])
    return VGroup(b, f).scale(s)


def door(num, color=DOOR):
    r = Rectangle(width=0.95, height=1.35, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.12), 1)
    k = Dot(radius=0.05, color=color).move_to(r.get_right() + LEFT * 0.18)
    n = M(num, 22, color).next_to(r, UP, buff=0.12)
    return VGroup(r, k, n)


class D10ReadSticker(VoiceScene):
    def construct(self):
        self.title_card("Read the sticker", "four ways a connection fails, and what each one tells you")

        # ---------- 1. the returned parcels
        p = parcel(GOLD_M, 2.4).move_to(UP * 0.6)
        self.beat("Picture a parcel that comes back to your door, with a sticker on it.", FadeIn(p, shift=LEFT * 1.5), run_time=1.6)
        s1 = sticker("no such street", "", w=3.4).move_to(LEFT * 4.3 + DOWN * 1.9)
        s2 = sticker("nobody at this apartment", "", w=3.8).move_to(DOWN * 1.9)
        s3 = sticker("never came back", "", GREY_B, w=3.4).move_to(RIGHT * 4.3 + DOWN * 1.9)
        self.beat("One sticker says, no such street. Another says, nobody at this apartment. And a third parcel never comes back at all.",
                  FadeIn(s1, shift=UP * 0.2), Succession(Wait(2.0), FadeIn(s2, shift=UP * 0.2)), Succession(Wait(4.0), FadeIn(s3, shift=UP * 0.2)), run_time=6.0)
        self.beat("Each sticker points to a different mistake, and each needs a different fix. Computers leave stickers too. We call them error messages.",
                  Indicate(s1[1], color=BLACK), Succession(Wait(1.2), Indicate(s2[1], color=BLACK)), Succession(Wait(2.4), Indicate(s3[1], color=BLACK)), run_time=4.0)
        same = T("it can't connect", 40, RED_M).move_to(UP * 0.6)
        self.beat("Here's the trap. Every failure feels like the same thing. It can't connect. So people restart things at random, when the sticker already said what broke.",
                  FadeOut(p), FadeIn(same), VGroup(s1, s2, s3).animate.set_opacity(0.3), run_time=2.4)
        self.beat("Restarting at random is the network version of shaking a vending machine. Sometimes it works, and you learn nothing. So let's learn to read the sticker instead.",
                  Wiggle(same), run_time=1.6)
        self.play(FadeOut(VGroup(same, s1, s2, s3)), run_time=0.6)

        # ---------- 2. the running case and one message that works
        app = box("app", APP, w=2.2, h=1.1).move_to(APP_P)
        mach = RoundedRectangle(corner_radius=0.16, width=4.4, height=3.3, stroke_color=GREY_B, stroke_width=2.5).move_to(MACH_P)
        mt = M("cache", 26).next_to(mach.get_top(), DOWN, buff=0.3)
        d1 = door("6379").move_to(MACH_P + LEFT * 0.7 + UP * 0.05)
        d2 = door("6380", GREY_B).move_to(MACH_P + RIGHT * 1.25 + UP * 0.05)
        red = T("Redis", 26, DOOR).next_to(d1[0], DOWN, buff=0.15)
        self.beat("Here's our running case. hello-devops, the course's tiny web app, keeps its visit count in a small database called Redis. Redis runs in a container named cache, on port 6379.",
                  FadeIn(app), Succession(Wait(3.6), AnimationGroup(Create(mach), FadeIn(mt))), Succession(Wait(7.0), AnimationGroup(FadeIn(d1), FadeIn(red))), run_time=10.0)
        q = T("“The app can't reach cache.”", 30, YELLOW_M).move_to(UP * 3.05)
        self.beat("And a colleague says, the app can't reach cache. Before we read any error, let's follow one message that works, step by step.",
                  FadeIn(q, shift=DOWN * 0.1), run_time=1.6)
        self.play(FadeOut(q), run_time=0.4)

        # step 1: the name
        book = box("DNS: the phone book", DNSC, w=3.6, h=1.0).move_to(BOOK_P)
        n1 = T("1  name", 26, DNSC).next_to(book, RIGHT, buff=0.35)
        ask = arrow(app[0].get_top() + RIGHT * 0.3, book[0].get_bottom() + LEFT * 0.9, DNSC)
        self.beat("Step one, the name. Machines connect to addresses, not names. So the app first asks DNS, the phone book of the network. What's the address of cache?",
                  FadeIn(book), FadeIn(n1), Succession(Wait(5.0), GrowArrow(ask), travel(ask, DNSC, 0.8)), run_time=8.0)
        addr = chip("cache = 172.20.0.2", DNSC, 24, mono=True).next_to(book, DOWN, buff=0.3)
        self.beat("The answer comes back. 172.20.0.2. The name has become a street address.",
                  FadeIn(addr, shift=DOWN * 0.15), run_time=1.6)
        self.beat("Out on the internet, that question can pass through a whole chain of servers, and each one keeps the answer for a while. That while is called its TTL.",
                  Indicate(book[1], color=DNSC), run_time=1.6)

        # step 2: the address
        road = Line(app[0].get_right(), mach.get_left(), stroke_width=3, color=ROAD)
        n2 = T("2  address", 26, GREY_B).next_to(road, DOWN, buff=0.65).shift(LEFT * 0.4)
        env = parcel(GOLD_M, 0.8).move_to(app[0].get_right() + RIGHT * 0.4 + UP * 0.35)
        self.beat("Step two, the address. The message travels to the machine at 172.20.0.2.",
                  Create(road), FadeIn(n2), Succession(Wait(1.6), FadeIn(env), env.animate(run_time=1.8).move_to(mach.get_left() + LEFT * 0.45 + UP * 0.35)), run_time=4.6)

        # step 3: the door and the handshake
        n3 = T("3  door", 26, DOOR).next_to(mach, UP, buff=0.2).align_to(mach, RIGHT)
        self.beat("Step three, the door. One machine runs many programs, so a port picks the program, like an apartment number. Redis listens behind door 6379.",
                  FadeIn(n3), Succession(Wait(3.6), FadeIn(d2)), Succession(Wait(6.4), Indicate(d1[2], color=DOOR, scale_factor=1.3)), run_time=8.0)
        self.play(FadeOut(env), run_time=0.3)
        hs_y = [ROAD_Y + 0.75, ROAD_Y + 0.2, ROAD_Y - 0.35]
        L, R = app[0].get_right()[0] + 0.15, mach.get_left()[0] - 0.15
        syn = Arrow([L, hs_y[0], 0], [R, hs_y[0], 0], buff=0, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.04)
        sa = Arrow([R, hs_y[1], 0], [L, hs_y[1], 0], buff=0, stroke_width=3, color=DOOR, max_tip_length_to_length_ratio=0.04)
        ack = Arrow([L, hs_y[2], 0], [R, hs_y[2], 0], buff=0, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.04)
        ls = [M(t, 22, c).next_to(a, UP, buff=0.04) for t, a, c in (("SYN", syn, GOLD_M), ("SYN-ACK", sa, DOOR), ("ACK", ack, GOLD_M))]
        self.beat("Before any data moves, TCP, the registered mail of the network, does a three-step handshake. SYN. I want to talk.",
                  FadeOut(road), Succession(Wait(5.0), AnimationGroup(GrowArrow(syn), FadeIn(ls[0]))), run_time=7.0)
        self.beat("SYN-ACK. Fine, I hear you.", GrowArrow(sa), FadeIn(ls[1]), run_time=1.4)
        okc = T("connected", 26, GREEN_M).next_to(n2, DOWN, buff=0.2)
        self.beat("ACK. And the connection is open.", GrowArrow(ack), FadeIn(ls[2]), Succession(Wait(1.2), FadeIn(okc)), run_time=2.0)
        hs = VGroup(syn, sa, ack, *ls, okc)
        self.beat("Name, address, door. Three steps. And each one has its own sticker.",
                  Indicate(n1, color=DNSC), Succession(Wait(0.8), Indicate(n2, color=WHITE)), Succession(Wait(1.6), Indicate(n3, color=DOOR)), run_time=3.4)
        self.play(FadeOut(hs), run_time=0.5)
        road = Line(app[0].get_right(), mach.get_left(), stroke_width=3, color=ROAD)
        self.play(Create(road), FadeOut(addr), run_time=0.5)

        # ---------- 3. the colleague's error: predict which step
        fix = T("restart Redis?", 30, RED_M).move_to(MACH_P + DOWN * 2.35)
        self.beat("Back to our colleague. The app can't reach cache. The obvious fix is to restart Redis. Before you do, read the sticker.",
                  Succession(Wait(2.6), FadeIn(fix, shift=UP * 0.1)), run_time=5.0)
        e1 = M('nc: getaddrinfo for host "cache" port 6379: Name or service not known', 22, RED_M)
        fit(e1, 12.6).move_to(UP * 3.15)
        self.beat("Here it is. nc -zv cache 6379 says, getaddrinfo for host cache, port 6379, Name or service not known.",
                  Write(e1), run_time=3.0)
        self.beat("Pause and guess. Which step broke? The name, the address, or the door?",
                  Indicate(n1, color=DNSC), Indicate(n2, color=WHITE), Indicate(n3, color=DOOR), run_time=2.0, after=2.2)
        x1 = tick(False, 0.35).next_to(n1, RIGHT, buff=0.25)
        self.beat("The name. getaddrinfo is the function programs call to look up a name, and it failed before a single packet left the app.",
                  Create(x1), book[0].animate.set_stroke(RED_M), run_time=1.6)
        self.add(book[1])
        self.beat("So restarting Redis would change nothing. Redis never even heard a knock.",
                  Succession(Wiggle(fix, run_time=1.4), Wait(0.6), FadeOut(fix, run_time=0.6)), run_time=3.0)
        self.remove(fix)
        st1 = sticker("no such street", "Name or service not known", w=4.0).scale(0.75).move_to([-5.0, -2.75, 0])
        self.beat("That's the no such street sticker. The house can be in perfect shape. The postman still can't find the street.",
                  FadeIn(st1, shift=DOWN * 0.15), run_time=1.6)
        fixc = M("$ docker network connect shopnet client", 22, GREEN_M).move_to(e1)
        self.beat("In the lab, the cause was simple. The client container sat on Docker's default network, so its phone book had never heard of cache. Connect it to shopnet, and the name resolves to 172.20.0.2.",
                  ReplacementTransform(e1, fixc), Succession(Wait(6.4), AnimationGroup(FadeOut(x1), book[0].animate.set_stroke(DNSC), FadeIn(addr))), run_time=10.0)
        self.add(book[1])
        self.beat("So fix the step the sticker names, not the one you happen to be looking at.", Indicate(st1[1], color=BLACK), run_time=1.6)

        # ---------- 4. refused: nobody at this apartment
        e2 = M("nc: connect to cache (172.20.0.2) port 6380 (tcp) failed: Connection refused", 22, RED_M)
        fit(e2, 12.6).move_to(UP * 3.15)
        knock = Arrow(road.get_start() + UP * 0.25, road.get_end() + UP * 0.25, buff=0, stroke_width=3, color=GOLD_M, max_tip_length_to_length_ratio=0.04)
        kl = M("SYN to 6380", 22, GOLD_M).next_to(knock, UP, buff=0.05)
        self.beat("Now knock on a door where nobody lives. nc -zv cache 6380.",
                  ReplacementTransform(fixc, e2), GrowArrow(knock), FadeIn(kl), Indicate(d2[2], color=WHITE, scale_factor=1.3), run_time=3.0)
        rst = Arrow(road.get_end() + DOWN * 0.25, road.get_start() + DOWN * 0.25, buff=0, stroke_width=3, color=RED_M, max_tip_length_to_length_ratio=0.04)
        rl = M("reset", 22, RED_M).next_to(rst, DOWN, buff=0.05)
        self.beat("The machine is there, so it answers the SYN at once, with a reset. Connection refused. Nothing listens on that port.",
                  GrowArrow(rst), FadeIn(rl), run_time=1.4)
        st2 = sticker("nobody at this apartment", "Connection refused", w=4.0).scale(0.75).move_to([4.75, -2.75, 0])
        self.beat("Nobody at this apartment. The app is down, on another port, or bound to 127.0.0.1, so it only answers knocks from inside its own machine.",
                  FadeIn(st2, shift=UP * 0.15), run_time=1.6)
        self.play(FadeOut(VGroup(knock, kl, rst, rl)), run_time=0.4)

        # ---------- 5. timed out: the parcel that vanishes, and a timing prediction
        e3 = T("timed out", 30, RED_M).move_to(UP * 3.15)
        self.beat("And the parcel that never comes back? That's a timeout. Nothing answers at all. A firewall dropped the packets, or the address is wrong, or unreachable.",
                  ReplacementTransform(e2, e3), run_time=1.6)
        self.beat("Pause and guess. Which sticker arrives faster, refused, or timed out?",
                  Indicate(st2[2], color=BLACK), Indicate(e3, color=RED_M), run_time=1.6, after=2.2)
        tl = NumberLine(x_range=[0, 8, 1], length=5.5, include_numbers=False, color=GREY_B).move_to([-3.25, -1.75, 0])
        tlab = T("time", 24, GREY_B).next_to(tl, RIGHT, buff=0.2)
        r_mark = VGroup(Dot(tl.n2p(0.08), color=DOOR), T("refused: about a millisecond", 24, DOOR)).arrange(UP, buff=0.15)
        r_mark[0].move_to(tl.n2p(0.08)); r_mark[1].next_to(r_mark[0], UP, buff=0.2).align_to(tl, LEFT)
        self.beat("Refused comes back in about a millisecond.",
                  Create(tl), FadeIn(tlab), FadeIn(r_mark), run_time=1.6)
        tries = VGroup(*[Dot(tl.n2p(x), color=GOLD_M) for x in (0.08, 1.0, 3.0, 7.0)])
        tryl = T("SYN, SYN again, and again...", 24, GOLD_M).next_to(tl, DOWN, buff=0.3).align_to(tl, LEFT)
        self.beat("On a timeout, your machine resends the SYN a few times, waiting longer each time, before it gives up. So even the waiting is a clue.",
                  Succession(*[FadeIn(d, scale=0.5, run_time=0.9) for d in tries]), run_time=4.4)
        st3 = sticker("never came back", "timed out", GREY_B, w=3.6).scale(0.75).move_to([-1.75, -2.75, 0])
        self.play(FadeOut(VGroup(tl, tlab, r_mark, tries)), FadeIn(st3, shift=DOWN * 0.15), run_time=0.8)

        # ---------- 6. reset or empty reply
        e4 = M("Connection reset by peer   /   Empty reply from server", 22, RED_M).move_to(UP * 3.15)
        desk = Rectangle(width=0.5, height=0.9, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.2), 1).move_to(mach.get_left() + RIGHT * 0.45 + DOWN * 0.35)
        dl = T("forwarder", 22, GOLD_M).next_to(desk, DOWN, buff=0.12)
        self.beat("One more sticker. Connection reset, or an empty reply. Something accepted the parcel at the front desk, then shut the door.",
                  ReplacementTransform(e3, e4), FadeIn(desk), FadeIn(dl), run_time=2.0)
        self.beat("Proxies, and Docker's port forwarder, do this when the app behind them is unreachable. For example, an app inside a container that's bound to 127.0.0.1.",
                  Indicate(dl, color=GOLD_M), Succession(Wait(4.0), Indicate(d1[2], color=RED_M, scale_factor=1.3)), run_time=6.0)
        st4 = sticker("taken in, door shut", "Connection reset", BLUE_M, w=3.6).scale(0.75).move_to([1.5, -2.75, 0])
        self.play(FadeIn(st4, shift=UP * 0.15), run_time=0.6)
        rule = T("Read the error before you fix anything.", 30, YELLOW_M).move_to(UP * 3.15)
        self.beat("So here is the rule. Read the error before you fix anything. Each one names a different step.",
                  ReplacementTransform(e4, rule), run_time=1.6)

        # ---------- 7. guardrails on the toolbox
        scene_all = VGroup(app, mach, mt, d1, d2, red, book, n1, ask, addr, road, n2, n3, desk, dl, rule)
        self.play(FadeOut(scene_all), VGroup(st1, st2, st3, st4).animate.set_opacity(0), run_time=0.7)
        self.remove(st1, st2, st3, st4)
        t1 = VGroup(M("ping", 26, GOLD_M), T("uses ICMP, which many firewalls block: a failed ping proves little", 26)).arrange(RIGHT, buff=0.4)
        t2 = VGroup(M("dig", 26, DNSC), T("asks DNS directly and ignores /etc/hosts", 26)).arrange(RIGHT, buff=0.4)
        t3 = T("These tools show whether a message arrived, not what it said.", 28, GREY_B)
        tg = VGroup(t1, t2, t3).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(ORIGIN)
        fit(tg, 12.6)
        self.beat("Two cautions about the toolbox. ping uses a small protocol called ICMP, which many firewalls block. So a failed ping proves little.",
                  FadeIn(t1, shift=RIGHT * 0.2), run_time=1.6)
        self.beat("And dig asks DNS servers directly, and ignores /etc/hosts, a local file that beats DNS. Your apps read that file first. So if dig and your app disagree about a name, look there.",
                  FadeIn(t2, shift=RIGHT * 0.2), run_time=1.6)
        self.beat("And every one of these tools has the same limit. They tell you whether a message arrived, not what it said. That's the next lesson.",
                  FadeIn(t3, shift=RIGHT * 0.2), run_time=1.6)
        self.play(FadeOut(tg), run_time=0.6)

        # ---------- 8. moral: four stickers, three steps
        grid = VGroup(
            VGroup(sticker("no such street", "Name or service not known"), T("1  the name", 26, DNSC)).arrange(DOWN, buff=0.25),
            VGroup(sticker("nobody at this apartment", "Connection refused", w=4.0), T("3  the door", 26, DOOR)).arrange(DOWN, buff=0.25),
            VGroup(sticker("never came back", "timed out", GREY_B), T("2  dropped on the way", 26, GREY_B)).arrange(DOWN, buff=0.25),
            VGroup(sticker("taken in, door shut", "Connection reset", BLUE_M), T("the app behind the desk", 26, BLUE_M)).arrange(DOWN, buff=0.25),
        ).arrange_in_grid(rows=2, cols=2, buff=(1.0, 0.55)).move_to(DOWN * 0.1)
        self.beat("So, the moral of the story. An error isn't a mood, it's a location. No such street means the name. Nobody home means the door. Silence means something dropped it on the way. And a shut door means the app behind the desk.",
                  LaggedStart(*[FadeIn(g, shift=UP * 0.15) for g in grid], lag_ratio=0.9), run_time=12.0)
        self.play(FadeOut(grid), run_time=0.6)
        c1 = M("$ nc -zv db.internal 22     succeeds at once", 26)
        c2 = M("$ nc -zv db.internal 5432   waits 30 s, times out", 26)
        cq = T("Which step broke?", 32, YELLOW_M)
        cg = VGroup(c1, c2, cq).arrange(DOWN, buff=0.45).move_to(UP * 0.6)
        self.beat("A quick check. nc -zv db.internal 22 succeeds at once. Port 5432, the database port, waits thirty seconds, then times out. Which step broke? Pause and guess.",
                  FadeIn(c1), Succession(Wait(3.2), FadeIn(c2)), Succession(Wait(8.0), FadeIn(cq)), run_time=10.0, after=2.2)
        ans = T("A firewall is dropping traffic to 5432.", 30, GREEN_M).move_to(DOWN * 1.9)
        self.beat("The name resolved, and the host answered on port 22. A stopped database would be refused fast. So the silence points to a firewall dropping traffic to 5432.",
                  Succession(Wait(5.6), FadeIn(ans, shift=UP * 0.1)), run_time=7.0)
        self.wait(1.5)
