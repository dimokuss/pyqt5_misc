#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from sip import SIP_VERSION_STR

from dselib.baseui.dseapp import DseApp
from dselib.baseui.appcontext import AppContext


def main():

    app = QApplication(sys.argv)
    app_context = AppContext()
    app_context.initialize(sys.argv)
    dse_app = DseApp(app_context)

    # if a perspective name was passed on the command line, start ACES in that perspective
    if len(sys.argv) > 1:
        initial_perspective = sys.argv[1]
    else:
        initial_perspective = 'ItemManager'

    dse_app.create_view(initial_perspective)

    return_code = app.exec_()

    app_context.close()

    sys.exit(return_code)

if __name__ == '__main__':
    main()
