

def is_within_tol(base_val, check_val, percent):
    tol = 1 + 100.0/float(percent)
    if check_val > base_val*(1+tol):
        return False
    if check_val < base_val*(1-tol):
        return False
    return True