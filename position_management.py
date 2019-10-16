class position_manager(object):

    def attempt_trade(self, fail_times=0):
        if fail_times == 0:
            return 0.25
        elif fail_times == 1:
            return 0.5
        elif fail_times == 2:
            return 0.75
        else:
            return 1
