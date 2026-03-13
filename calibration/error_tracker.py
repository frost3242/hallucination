import numpy as np

def expected_calibration_error(confidences, correctness):

    bins = np.linspace(0,1,10)

    ece = 0

    for i in range(len(bins)-1):

        mask = (confidences >= bins[i]) & (confidences < bins[i+1])

        if np.sum(mask) == 0:
            continue

        bin_acc = np.mean(correctness[mask])
        bin_conf = np.mean(confidences[mask])

        ece += np.abs(bin_acc - bin_conf)

    return ece