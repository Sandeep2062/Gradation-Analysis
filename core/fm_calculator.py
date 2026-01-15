class FMCalculator:

    def calculate_fm(self, retained_list):
        cumulative = []
        running = 0

        for r in retained_list:
            running += r
            cumulative.append(running)

        if cumulative[-1] == 0:
            return 0.0

        # convert to percentage
        cumulative_pct = [(1 - (c / cumulative[-1])) * 100 for c in cumulative]

        fm = sum(cumulative_pct) / 100
        return fm
