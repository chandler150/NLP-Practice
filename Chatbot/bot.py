#! /usr/bin/env python
#
# Example program using irc.bot.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.
This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.
The known commands are:
    stats -- Prints some channel information.
    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.
    die -- Let the bot cease to exist.
    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import time, random, threading, sys
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import surf1
INITIAL_OUTREACHES = [
    "Howdy, partner!",
    "Yo!",
    "Hey man!",
    "Ahoy, matey!",
    "Hiya!",
    "Greetings.",
    "Whaddup.",
    "GOOOOOD MORNING, VIETNAM!"
]

SECOND_OUTREACHES = [
    "You there partner?",
    "Anybody home?",
    "Ahoy... matey?",
    "I'm trying to greet you, friend.",
    "Excuse me, did you see my greeting?"
]

INITIAL_INQUIRIES = [
    "How've you been?",
    "How's it going?",
    "How are you?",
    "How goes it comrade?",
    "What's the word, hummingbird?",
    "What's cookin', good lookin'?",
    "How you doin'?",
    "What's kickin', little chicken?"
]

SECOND_INQUIRIES = [
    "What about you?",
    "Yourself?",
    "How 'bout you?",
    "And how're you doin'?",
    "But enough about me, what about you?",
    "And what've you been up to?"
    "And how've you been?"
]

INQUIRY_REPLIES = [
    "Not bad.",
    "Been better.",
    "Swell! Thanks for asking.",
    "Livin' it up!",
    "I've seen better days,",
    "I'm alright.",
    "I'm good.",
    "Excellent!"
]

GIVE_UP_STATEMENTS = [
    "Like, whatever man.",
    "Pretty rude, my dude.",
    "Nice chat... I guess.",
    "Forget it...",
    "I've got too many friends anyways..."
]

class State:
    GIVE_UP = -1
    START = 0
    INITIAL_OUTREACH = 1
    SECOND_OUTREACH = 2
    OUTREACH_REPLY = 3
    FIRST_INQUIRY = 4
    SECOND_INQUIRY = 5
    WAIT_FOR_INQUIRY = 6
    END = 7

    SURF1 = 10
    SURF2 = 11
    SURF3 = 12

class ChatBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.state = State.START
        self.speaker = None
        self.timer = None
        self.timed_out = False
        self.sleep_time = 30.0

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        self.timer = threading.Timer(self.sleep_time, self.set_random_user, [c, e])
        self.timer.start()

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            if self.speaker is None:
                self.speaker = e.source.nick
            self.do_command(e, a[1].strip())

    def set_random_user(self, c, e):
        for chname, chobj in self.channels.items():
            users = sorted(chobj.users())
            choice = random.choice(users)
            while choice == sys.argv[3]:
                choice = random.choice(users)

            self.speaker = choice

        self.timer = threading.Timer(self.sleep_time, self.handle_timeout, [c, e])
        self.timer.start()

    def handle_timeout(self, c, e):
        self.timed_out = True
        self.do_command(e, "timeout")
        self.timed_out = False

    def advance_state(self, c, e):
        if self.state == State.START:
            if self.timed_out:
                self.initial_outreach(c, e)
                self.state = State.INITIAL_OUTREACH
            else:
                self.outreach_reply(c, e)
                self.state = State.OUTREACH_REPLY
        elif self.state == State.INITIAL_OUTREACH:
            if self.timed_out:
                self.second_outreach(c, e)
                self.state = State.SECOND_OUTREACH
            else:
                self.initial_inquiry(c, e)
                self.state = State.FIRST_INQUIRY
        elif self.state == State.SECOND_OUTREACH:
            if self.timed_out:
                self.give_up(c, e)
                self.state = State.GIVE_UP
            else:
                self.initial_inquiry(c, e)
                self.state = State.FIRST_INQUIRY
        elif self.state == State.OUTREACH_REPLY:
            if self.timed_out:
                self.give_up(c, e)
                self.state = State.GIVE_UP
            else:
                self.inquiry_reply(c, e)
                time.sleep(random.randint(1, 3))
                self.second_inquiry(c, e)
                self.state = State.SECOND_INQUIRY
        elif self.state == State.FIRST_INQUIRY:
            if self.timed_out:
                self.give_up(c, e)
                self.state = State.GIVE_UP
            else:
                self.state = State.WAIT_FOR_INQUIRY
        elif self.state == State.SECOND_INQUIRY:
            if self.timed_out:
                self.give_up(c, e)
                self.state = State.GIVE_UP
            else:
                self.state = State.END
        elif self.state == State.WAIT_FOR_INQUIRY:
            self.inquiry_reply(c, e)
            self.state = State.END

        elif self.state == State.SURF1:
            self.get_time(c,e)
        elif self.state == State.SURF2:
            self.spot_reply1(c, e)
        elif self.state == State.SURF3:
            self.spot_reply2(c, e)
        else:
            print("Invalid state: ", self.state)

    def get_time(self, c, e):
        text = str(' '.join(e.arguments[0].split()[1:]))
        if text == "today":
            c.notice(self.channel, self.speaker + " Which beach may you want to surf today?")
            self.state = State.SURF2
        elif text == "tomorrow":
            c.notice(self.channel, self.speaker + " Which beach may you want to surf tomorrow?")
            self.state = State.SURF3
        else:
            self.state = State.SURF1

    def spot_reply1(self, c, e):

        text = ' '.join(e.arguments[0].split()[1:])
        hits = surf1.getForecast(text, "today")
        c.notice(self.channel, self.speaker + ": " + hits)

    def spot_reply2(self, c, e):

        text = ' '.join(e.arguments[0].split()[1:])
        hits = surf1.getForecast(text, "tomorrow")
        c.notice(self.channel, self.speaker + ": " + hits)

    def initial_inquiry(self, c, e):
        msg = INITIAL_INQUIRIES[random.randint(0, len(INITIAL_INQUIRIES) - 1)]
        c.notice(self.channel, self.speaker + ": " + msg)

    def second_inquiry(self, c, e):
        msg = SECOND_INQUIRIES[random.randint(0, len(SECOND_INQUIRIES) - 1)]
        c.notice(self.channel, self.speaker + ": " + msg)

    def inquiry_reply(self, c, e):
        msg = INQUIRY_REPLIES[random.randint(0, len(INQUIRY_REPLIES) - 1)]
        c.notice(self.channel, self.speaker + ": " + msg)

    def initial_outreach(self, c, e):
        msg = INITIAL_OUTREACHES[random.randint(0, len(INITIAL_OUTREACHES) - 1)]
        c.notice(self.channel, self.speaker + ": " + msg)

    def second_outreach(self, c, e):
        msg = SECOND_OUTREACHES[random.randint(0, len(SECOND_OUTREACHES) - 1)]
        c.notice(self.channel, self.speaker + ": " + msg)

    def outreach_reply(self, c, e):
        msg = INITIAL_OUTREACHES[random.randint(0, len(INITIAL_OUTREACHES) - 1)]
        c.notice(self.channel, self.speaker + ": " + msg)

    def give_up(self, c, e):
        msg = GIVE_UP_STATEMENTS[random.randint(0, len(GIVE_UP_STATEMENTS) - 1)]
        c.notice(self.channel, self.speaker + ": " + msg)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_dccmsg(self, c, e):
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        time.sleep(random.randint(1, 3))
        sender = e.source.nick

        if sender == self.speaker:
            self.timer.cancel()

        if e.type == "pubmsg":
            dest = e.target
        else:
            dest = sender
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "forget":
            self.timer.cancel()
            self.state = State.START
            self.speaker = None
            c.notice(dest, sender + (": Oh geeze, I've forgotten everything. "
                                     "I hate when that happens. "
                                     "Not that I remember it ever happening "
                                     "before."))
            self.timer = threading.Timer(self.sleep_time, self.set_random_user, [c, e])
            self.timer.start()
        elif cmd == "users":
            for chname, chobj in self.channels.items():
                users = sorted(chobj.users())
                c.notice(dest, sender + ": Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(dest, sender + ": Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(dest, sender + ": Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp(
                "DCC",
                dest,
                "CHAT chat %s %d"
                % (ip_quad_to_numstr(dcc.localaddress), dcc.localport),
            )
        elif cmd == "hello":
            c.notice(dest, sender + ": Hi!")
        elif cmd == "surf":
            self.timer.cancel()
            self.state = State.SURF1
            self.speaker = None
            c.notice(dest, sender + (" Get a surf forecast! Are you surfing today or tomorrow?"))
            self.timer = threading.Timer(self.sleep_time, self.set_random_user, [c, e])
            self.timer.start()

        elif sender == self.speaker or self.timed_out:
            self.advance_state(c, e)

            if self.state not in (State.END, State.GIVE_UP, State.WAIT_FOR_INQUIRY):
                self.timer = threading.Timer(self.sleep_time, self.handle_timeout, [c, e])
                self.timer.start()
        else:

            c.notice(dest, sender + ": Not understood: " + cmd)
            c.notice(dest, sender + " Users: " + ', '.join(users))


def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = ChatBot(channel, nickname, server, port)
    bot.start()


if __name__ == "__main__":
    main()
