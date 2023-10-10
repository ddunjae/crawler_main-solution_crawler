def auction_result(winning_bid, start_bid, estimate_min, estimate_max, cancel = 0):
    bid_class, competition = None, None
    if cancel == 1.0:
        return "w/d", competition
    if str(winning_bid).lower().strip() in ["nan", "none", ""]:
        return bid_class, competition
    if str(start_bid).lower().strip() not in ["nan", "none", "", "0", "0.0"]:
        competition = float(winning_bid) / float(start_bid) - 1
    else: competition = 0
    if str(estimate_min).lower().strip() not in ["nan", "none", ""]:
        if estimate_min > winning_bid:
            bid_class = "BELOW"
        else:
            bid_class = "WITHIN"
    if str(estimate_max).lower().strip() not in ["nan", "none", ""] and bid_class !="BELOW":
        if estimate_max < winning_bid:
            bid_class = "ABOVE"
        else:
            bid_class = "WITHIN"
    if not bid_class:
        bid_class = "WITHIN"
    return bid_class, competition