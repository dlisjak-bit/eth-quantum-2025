
def placeholder_instructions(N=8):
    A = [[("RX",), ("RY",)] for _ in range(N)]

    for i in range(N):
        for j in range(N):
            if i != j:
                A[i].extend(
                    [("MS", j + 1), ("RX",), ("RY",), ("MS", j + 1), ("RX",), ("RY",)]
                )

    return A
