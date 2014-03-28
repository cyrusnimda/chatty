# -*- coding: utf-8 -*-


class BaseController():
    def save(self):
        print "save"

class TemporalUserController(BaseController):
    def save(self):
        print "temp save"