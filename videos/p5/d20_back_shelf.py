import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fg import *

SAY.extend([(r"\bdocker rm -f\b", "docker R M"), (r"\bdocker rm\b", "docker R M"), (r"\btmpfs\b", "temp F S"), (r"\bwget\b", "W get"),
            (r"\b127\.0\.0\.11\b", "one two seven, dot zero, dot zero, dot eleven"), (r"\b172\.23\.0\.2\b", "one seven two, dot two three, dot zero, dot two"),
            (r"\b172\.17\.0\.5\b", "one seven two, dot one seven, dot zero, dot five"), (r"\bREDIS_HOST\b", "redis host"), (r"\blocalhost\b", "local host")])


def tint(c, k=0.16):
    return interpolate_color(ManimColor("#000000"), ManimColor(c), k)


def cylinder(color=GREEN_M, w=1.5, h=1.5):
    top = Ellipse(width=w, height=0.4, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.3), opacity=1)
    body = Rectangle(width=w, height=h, stroke_width=0).set_fill(tint(color, 0.14), opacity=1)
    bot = Ellipse(width=w, height=0.4, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.14), opacity=1)
    top.move_to(body.get_top()); bot.move_to(body.get_bottom())
    sides = VGroup(Line(body.get_corner(UL), body.get_corner(DL)), Line(body.get_corner(UR), body.get_corner(DR))).set_stroke(color, 3)
    return VGroup(bot, body, sides, top)


def ctr(name, color, w=2.2, h=1.2):
    r = RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=3).set_fill(tint(color, 0.1), opacity=1)
    return VGroup(r, M(name, 24, color).move_to(r))


class D20BackShelf(VoiceScene):
    def steps(self, text, *plays):
        path, dur = voice(text)
        self._cue(text, dur)
        self.add_sound(path)
        t0 = self.renderer.time
        for rt, *anims in plays:
            self.play(*anims, run_time=rt)
        left = dur - (self.renderer.time - t0)
        if left > 0.02:
            self.wait(left)
        self.wait(0.25)

    def construct(self):
        self.title_card("The back shelf and the staff list", "where container data lives, and how containers find each other")

        # 1. the cafe
        till = RoundedRectangle(corner_radius=0.12, width=2.6, height=1.6, stroke_color=GOLD_M, stroke_width=3).set_fill(tint(GOLD_M, 0.1), opacity=1).move_to([-3.4, 0.2, 0])
        tl = T("the till", 26, GOLD_M).next_to(till, DOWN, buff=0.2)
        note = VGroup(Square(0.9, stroke_color=YELLOW_M, stroke_width=2.5).set_fill(tint(YELLOW_M, 0.35), opacity=1))
        nt = M("47", 28, YELLOW_M)
        note.add(nt.move_to(note[0]))
        note.move_to(till.get_corner(UR) + LEFT * 0.55 + DOWN * 0.5)
        self.beat("Picture a small cafe that keeps its count of customers on a sticky note, stuck to the till.",
                  Create(till), FadeIn(tl), FadeIn(note, shift=DOWN * 0.1), run_time=1.8)
        till2 = till.copy().shift(RIGHT * 6.4)
        self.steps("Every night, the cleaners swap the till for a fresh one, note and all. So every morning, the count starts again at zero.",
                   (2.0, Wait(2.0)), (1.2, VGroup(till, note).animate.shift(DOWN * 4.5).set_opacity(0), FadeIn(till2.move_to(till.get_center()))),
                   (0.6, FadeIn(n0 := M("0", 28, YELLOW_M).move_to(note.get_center()))))
        till = till2
        shelf = Line([2.2, -0.3, 0], [5.4, -0.3, 0], stroke_width=4, color=GREEN_M)
        book = Rectangle(width=1.0, height=1.2, stroke_color=GREEN_M, stroke_width=3).set_fill(tint(GREEN_M, 0.25), opacity=1).next_to(shelf, UP, buff=0).shift(LEFT * 0.4)
        bl = T("notebook on the back shelf", 26, GREEN_M).next_to(shelf, DOWN, buff=0.25)
        self.beat("So you move the count into a notebook on the back shelf. It does not go away with the till.",
                  Create(shelf), FadeIn(book, shift=DOWN * 0.1), FadeIn(bl), FadeOut(n0), run_time=1.8)
        cash = Circle(radius=0.26, stroke_color=BLUE_M, stroke_width=3).set_fill(tint(BLUE_M, 0.3), opacity=1).move_to([-0.8, 1.6, 0])
        cq = T("where is the shelf?", 26, BLUE_M).next_to(cash, UP, buff=0.2)
        self.beat("The next morning a new cashier arrives. And nobody has told her where the shelf is.",
                  GrowFromCenter(cash), FadeIn(cq), run_time=1.4)
        two = VGroup(T("1. where do things that must last live?", 28, YELLOW_M), T("2. how do helpers find each other?", 28, YELLOW_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([0, -2.8, 0])
        self.steps("Two separate problems. Where to keep things that must last. And how helpers find each other. It is easy to fix one and forget the other, so let's take them one at a time.",
                   (0.6, FadeIn(two[0], shift=UP * 0.1)), (1.4, Wait(1.4)), (0.6, FadeIn(two[1], shift=UP * 0.1)))
        self.play(FadeOut(VGroup(till, tl, shelf, book, bl, cash, cq, two)), run_time=0.7)

        # 2. map: the till is a container
        c1 = ctr("container", GOLD_M, 3.0, 1.6).move_to([-3.6, 0.6, 0])
        lay = T("its own writable layer", 26, YELLOW_M).next_to(c1, DOWN, buff=0.25)
        self.beat("In Docker, the till is a container. The sticky note is its own thin writable layer, where it keeps what it writes.",
                  FadeIn(c1), FadeIn(lay), run_time=1.6)
        rm = M("$ docker rm", 26, RED_M).next_to(c1, UP, buff=0.35)
        self.steps("And the cleaners are docker rm, followed by a fresh container. You do that on every upgrade, and after a crash. So our visit count from hello-devops started at zero in every new container.",
                   (0.6, FadeIn(rm)), (1.2, c1.animate.set_opacity(0.25)), (2.0, Wait(2.0)), (0.6, c1.animate.set_opacity(1)))
        r0 = T("Treat every container as disposable. Keep the data outside it.", 30, YELLOW_M).move_to([0, -2.9, 0])
        fit(r0, 12.4)
        self.beat("That is fine. You want to be able to throw any container away. So here is the rule. Treat every container as disposable. Keep the data outside it.",
                  FadeIn(r0, shift=UP * 0.1), run_time=1.8)
        self.play(FadeOut(VGroup(rm, r0)), run_time=0.4)

        # 3. the volume is the back shelf; predict, then show
        vol = cylinder(GREEN_M, 1.8, 1.4).move_to([3.4, 0.5, 0])
        vl = VGroup(T("volume: the back shelf", 26, GREEN_M), M("site", 24, GREEN_M)).arrange(DOWN, buff=0.12).next_to(vol, DOWN, buff=0.3)
        mnt = DashedLine(c1.get_right(), vol.get_left(), dash_length=0.12, stroke_width=3, color=GREEN_M)
        cmd = M("$ docker run -v site:/usr/share/nginx/html nginx", 24, GREY_B).move_to([0, 3.0, 0])
        fit(cmd, 12.4)
        self.steps("The back shelf is a volume, storage that Docker creates and looks after. We mount it at one folder inside the container. Here, nginx's web page folder.",
                   (1.4, FadeIn(vol), FadeIn(vl)), (1.2, Wait(1.2)), (0.8, Create(mnt), FadeIn(cmd)), (0.6, Transform(c1[1], M("web", 24, GOLD_M).move_to(c1[1]))))
        page = M("<h1>Served from a volume</h1>", 22, GREEN_M).move_to([0, -1.6, 0])
        self.steps("A throwaway container writes our own page into the volume, and nginx serves it: served from a volume.",
                   (2.4, Wait(2.4)), (0.8, travel(mnt, GREEN_M, 0.8)), (0.6, FadeIn(page, shift=UP * 0.1)))
        rmf = M("$ docker rm -f web", 26, RED_M).move_to(cmd)
        self.steps("Now the cleaners come. We throw the container away, and start a brand new one with the same volume. Is the page still there? Pause and guess.",
                   (0.6, Transform(cmd, rmf)), (0.8, FadeOut(c1), FadeOut(mnt), FadeOut(page), FadeOut(lay)), (1.0, Wait(1.0)),
                   (0.8, FadeIn(c1n := ctr("web", GOLD_M, 3.0, 1.6).move_to(c1)), Create(mnt)))
        self.wait(2.0)
        nid = T("new container, new ID", 26, GOLD_M).next_to(c1n, DOWN, buff=0.25)
        self.steps("Yes. A new container, with a new ID, and the same page, because the page lives on the shelf, not in the till.",
                   (0.6, FadeIn(nid)), (0.8, travel(mnt, GREEN_M, 0.8)), (0.6, FadeIn(page, shift=UP * 0.1)))
        c1 = c1n
        three = VGroup(VGroup(T("volume", 26, GREEN_M), T("Docker owns it: a database's files", 26)).arrange(RIGHT, buff=0.3),
                       VGroup(T("bind mount", 26, TEAL_M), T("you own it: code you edit on your Mac", 26)).arrange(RIGHT, buff=0.3),
                       VGroup(T("tmpfs", 26, PURPLE_M), T("nobody keeps it: memory only", 26)).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([0, -2.4, 0])
        self.steps("Docker has three kinds of these mounts, and you pick by asking who owns the data. Docker owns it, like a database's files: a volume. You own it, like code you edit: a bind mount, a folder from your Mac. Nobody should keep it: tmpfs, which lives in memory only.",
                   (0.6, FadeOut(page), FadeOut(nid)), (2.0, Wait(2.0)), (0.6, FadeIn(three[0], shift=UP * 0.1)), (2.6, Wait(2.6)), (0.6, FadeIn(three[1], shift=UP * 0.1)), (3.0, Wait(3.0)), (0.6, FadeIn(three[2], shift=UP * 0.1)))
        self.play(FadeOut(VGroup(three, cmd)), run_time=0.5)

        # 4. problem two: finding each other
        self.play(VGroup(c1, vol, vl, mnt).animate.scale(0.7).move_to([3.6, 1.7, 0]), run_time=0.8)
        bridge = Line([-5.6, -1.3, 0], [1.6, -1.3, 0], stroke_width=4, color=GREY_B)
        bnl = M("default bridge", 24, GREY_B).next_to(bridge, DOWN, buff=0.2)
        a = ctr("a", BLUE_M, 1.4, 0.9).move_to([-4.4, 0.2, 0])
        b = ctr("b", PURPLE_M, 1.4, 0.9).move_to([-0.2, 0.2, 0])
        ca = Line(a.get_bottom(), [a.get_x(), -1.3, 0], stroke_width=3, color=BLUE_M)
        cb = Line(b.get_bottom(), [b.get_x(), -1.3, 0], stroke_width=3, color=PURPLE_M)
        ipb = M("172.17.0.5", 22, PURPLE_M).next_to(b, UP, buff=0.15)
        self.steps("Now the new cashier. Every container you start plain joins Docker's default network, a virtual switch called the bridge. Each one gets an IP address, its number on that network, such as 172.17.0.5.",
                   (0.8, Create(bridge), FadeIn(bnl)), (1.6, Wait(1.6)), (0.8, FadeIn(a), FadeIn(b), Create(ca), Create(cb)), (2.0, Wait(2.0)), (0.6, FadeIn(ipb)))
        self.beat("By that number, a can reach b. But numbers change when containers restart, so you cannot write them down.",
                  travel(Line(a.get_right(), b.get_left()), BLUE_M, 1.0), Succession(Wait(1.8), Wiggle(ipb)), run_time=3.0)

        # the localhost trap
        lh = M("REDIS_HOST=localhost", 24, RED_M).next_to(a, UP, buff=0.2)
        self.steps("You might think: just use localhost, the name that means this machine. Let's try it. Tell the app that Redis lives at localhost.",
                   (2.4, Wait(2.4)), (0.6, FadeIn(lh, shift=DOWN * 0.1)))
        loop = CurvedArrow(a.get_corner(UR) + LEFT * 0.1, a.get_corner(UL) + RIGHT * 0.1, angle=PI * 1.2, color=RED_M, stroke_width=3)
        self.steps("But inside a container, localhost is the container itself. The app knocks on its own door, where nothing listens on Redis's port.",
                   (2.0, Wait(2.0)), (1.0, Create(loop)), (0.8, Wiggle(a)))
        self.beat("It is the cashier phoning herself to ask where the shelf is.", run_time=None)
        self.play(FadeOut(VGroup(lh, loop)), run_time=0.4)

        # predict: names on the default bridge
        wg = M("$ docker run alpine wget -qO- http://web", 24, GREY_B).move_to([-2.0, 2.0, 0])
        fit(wg, 7.4)
        self.beat("So we want names. From a container on the default bridge, ask for our nginx container by its name, web. Pause and guess.",
                  FadeIn(wg), run_time=1.4)
        self.wait(2.0)
        bad = M("wget: bad address 'web'", 24, RED_M).next_to(bridge, DOWN, buff=0.75)
        self.beat("Bad address. The default bridge has no lookup by name. Numbers only.",
                  FadeIn(bad, shift=UP * 0.1), run_time=1.0)
        self.play(FadeOut(VGroup(bad, ipb, wg)), run_time=0.4)

        # 5. a user-defined network with a staff list
        net = Line([-5.6, -1.3, 0], [5.6, -1.3, 0], stroke_width=4, color=TEAL_M)
        nl = M("demo", 24, TEAL_M).next_to(net, DOWN, buff=0.2).align_to(net, LEFT)
        mk = M("$ docker network create demo", 24, GREY_B).move_to([-2.0, 2.0, 0])
        self.steps("Now make a network of our own. docker network create demo. Then start web on it, and our asking container too.",
                   (0.6, FadeIn(mk)), (1.0, FadeOut(VGroup(bridge, bnl, b, cb)), Create(net), FadeIn(nl)),
                   (1.0, VGroup(c1, vol, vl, mnt).animate.scale(1 / 0.7).scale(0.75).move_to([3.4, 0.9, 0]), ca.animate.set_color(TEAL_M)))
        cw = Line(c1[0].get_bottom(), [c1.get_x(), -1.3, 0], stroke_width=3, color=TEAL_M)
        self.play(Create(cw), run_time=0.5)
        dns = VGroup(RoundedRectangle(corner_radius=0.1, width=2.8, height=1.3, stroke_color=YELLOW_M, stroke_width=3).set_fill(tint(YELLOW_M, 0.1), opacity=1))
        dl = VGroup(T("staff list", 26, YELLOW_M), M("web  172.23.0.2", 22, YELLOW_M)).arrange(DOWN, buff=0.15).move_to(dns[0])
        dns.add(dl).move_to([-0.6, -2.55, 0])
        dnl = M("DNS at 127.0.0.11", 22, YELLOW_M).next_to(dns, RIGHT, buff=0.3)
        self.steps("A network you create comes with something the default bridge lacks. A staff list. Docker's own DNS server, the service that turns names into addresses, waiting inside every container at 127.0.0.11.",
                   (2.6, Wait(2.6)), (0.8, FadeIn(dns[0]), FadeIn(dl[0])), (2.6, Wait(2.6)), (0.6, FadeIn(dnl)))
        self.steps("It knows every name on this network, because Docker handed out the addresses in the first place. Ask for web, and it answers: 172.23.0.2.",
                   (2.4, Wait(2.4)), (0.6, FadeIn(dl[1])), (0.6, Indicate(dl[1], color=YELLOW_M)))
        wg2 = M("$ docker run --network demo alpine wget -qO- http://web", 24, GREY_B).move_to([-1.2, 3.0, 0])
        fit(wg2, 10.0)
        page = M("<h1>Served from a volume</h1>", 22, GREEN_M).move_to([-1.4, 1.1, 0])
        q1 = Line(a.get_bottom() + DOWN * 0.05, dns.get_left() + LEFT * 0.05)
        q2 = Line(a.get_right(), c1.get_left())
        self.steps("Same request, from the demo network. The name goes to the staff list, the address comes back, and the page arrives. Served from a volume.",
                   (0.6, FadeOut(mk), FadeIn(wg2)), (1.0, travel(q1, YELLOW_M, 1.0)), (1.0, travel(q2, TEAL_M, 1.0)), (0.6, FadeIn(page, shift=DOWN * 0.1)))
        r1 = T("Names work only on a network you create. Create one per app.", 28, YELLOW_M).move_to([0, 2.2, 0])
        self.beat("So here is the rule. Containers find each other by name only on a network you create. Create one per app.",
                  FadeOut(page), FadeIn(r1, shift=DOWN * 0.1), run_time=1.4)
        self.play(FadeOut(r1), run_time=0.4)

        # 6. guardrails
        nop = T("same network: no -p needed. -p is for traffic from outside.", 26, TEAL_M).move_to([0, 2.2, 0])
        fit(nop, 12.4)
        self.beat("One more surprise. Containers on the same network reach each other on any port, with no dash p at all. Publishing with dash p is only for traffic from outside, like your browser.",
                  FadeIn(nop, shift=DOWN * 0.1), run_time=1.6)
        lim = VGroup(T("a volume stays on the one machine where you made it", 26, RED_M), T("and every container still needs a long command", 26, RED_M)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0, 2.2, 0])
        self.steps("And the honest limits. A volume stays on the one Docker machine where you made it. And every container still needs its own long command, typed in the right order.",
                   (0.6, FadeOut(nop)), (0.6, FadeIn(lim[0], shift=DOWN * 0.1)), (2.4, Wait(2.4)), (0.6, FadeIn(lim[1], shift=DOWN * 0.1)))
        self.play(FadeOut(lim), FadeOut(wg2), run_time=0.5)

        # 7. moral and quick check
        mor = T("the count on the back shelf, a staff list by the door", 30, GREEN_M).move_to([0, 2.3, 0])
        self.beat("So, back to the cafe. The count lives on the back shelf, a volume that outlives any till. And the new cashier reads the staff list, the network's DNS, to find everyone by name.",
                  FadeIn(mor, shift=DOWN * 0.1), Indicate(vol[3], color=GREEN_M), Succession(Wait(2.4), Indicate(dns[0], color=YELLOW_M)), run_time=4.0)
        self.play(FadeOut(mor), run_time=0.4)
        quiz = T("Quick check: in the web container, REDIS_HOST=localhost. Where does the app look?", 26, YELLOW_M).move_to([0, 2.6, 0])
        fit(quiz, 12.4)
        self.beat("Quick check. Inside the web container, REDIS_HOST is set to localhost. Where does the app look for Redis?",
                  FadeIn(quiz, shift=DOWN * 0.1), run_time=1.4)
        self.wait(2.0)
        ans = T("At itself. Use Redis's name on a shared network.", 28, GREEN_M).next_to(quiz, DOWN, buff=0.3)
        self.beat("At itself. Put both on one network you created, and use Redis's name instead.", FadeIn(ans, shift=DOWN * 0.1), run_time=1.2)
        self.wait(1.2)
