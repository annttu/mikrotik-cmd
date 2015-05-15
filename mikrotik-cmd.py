#!/usr/bin/env python3
# encoding: utf-8

import cmd
import getpass
from mikrotik import Mikrotik, MikrotikAPIError

class colors:
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MikrotikCommandLoop(cmd.Cmd):

    m = None
    prompt = '> '

    def precmd(self, line):
        if self.m and line.startswith("/"):
            line = "run %s" % line
        return cmd.Cmd.precmd(self, line)

    def do_greet(self, line):
        print("Welcome to use Mikrotik remote command line tool")

    def do_EOF(self, line):
        print("")
        return True

    def do_login(self, line):
        """
        Connect to device
        Usage: address user password
        """
        args = line.split()
        if len(args) < 1:
            print("Usage: login address [user] [password]")
            return
        if len(args) < 2:
            user = input("Username: ")
            passwd = getpass.getpass("Password: ")
        elif len(args) < 3:
            user = args[1]
            passwd = getpass.getpass("Password: ")
        else:
            user = args[1]
            passwd = args[2]

        self.m =  Mikrotik(args[0])
        self.m.login(user, passwd)
        self.prompt = '%s> ' % args[0]

    def do_run(self, line):
        """
        Run command on remote Mikrotik.
        """
        if not self.m:
            print("login first!")
            return
        args = line.split()
        if len(args) < 1:
            print("Usage: run [args]")
            return
        arguments = {}
        queries = {}
        argument_dict = arguments
        for i in args[1:]:
            if i.lower() == 'where':
                argument_dict = queries
                continue
            try:
                (a, b) = i.split("=",1)
                argument_dict[a] = b
            except ValueError:
                print("Invalid argument %s" % i)
                return

        response = self.m.run(args[0], attributes=arguments, queries=queries)
        for r in response:
            if r.status == "done":
                continue
            print("!%s%s%s%s %s %s" % (colors.BOLD, colors.MAGENTA, r.status, colors.ENDC, ' '.join(["%s%s%s=%s%s%s" % (colors.BLUE, k, colors.ENDC, colors.GREEN, v, colors.ENDC) for k, v in r.attributes.items()]),
                              ' '.join(r.error)))


    def do_logout(self, line):
        if self.m:
            self.m.disconnect()
            self.prompt = "> "
        else:
            self.prompt = "> "


if __name__ == '__main__':
    MikrotikCommandLoop().cmdloop()