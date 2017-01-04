import abc

class Program(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run_program(self):
        """Runs a program. That is, actually 
           starts execution and differs from init"""
        return

    @abc.abstractmethod
    def stop_program(self):
        """Stops a program.""" 
        return

    @abc.abstractmethod
    def keybindings(self):
        """Returns a map of keys bound to actions"""
        return

    @abc.abstractmethod
    def name(self):
        return
