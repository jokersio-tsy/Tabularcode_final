from collections import defaultdict

class AccuracyTracker:
    def __init__(self):
        self.type_stats = defaultdict(lambda: {"sum_acc": 0, "count": 0})
        self.total_stats = {"sum_acc": 0, "count": 0}

    def update(self, type, acc):
        # 更新type统计
        self.type_stats[type]["sum_acc"] += acc
        self.type_stats[type]["count"] += 1
        # 更新总体统计
        self.total_stats["sum_acc"] += acc
        self.total_stats["count"] += 1

    def get_averages(self):
        # 计算每个type的平均acc
        type_avg = {
            t: (s["sum_acc"] / s["count"], s["count"]) 
            for t, s in self.type_stats.items()
        }
        # 计算总体平均acc
        total_avg = (
            self.total_stats["sum_acc"] / self.total_stats["count"] 
            if self.total_stats["count"] > 0 
            else 0
        )
        return type_avg, total_avg