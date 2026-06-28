def calculate_dca_score(rsi, sto, price, sma):

    score = 0

    if rsi < 30:
        score += 50
    if sto < 20:
        score += 30
    if price < sma:
        score += 20

    return score