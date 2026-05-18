import math, pandas as pd
Nsq = 0.63354460
Nb = 0.63354460
Cc_b = 0.36645540
kappa_dt = math.pi*Nsq
T_Om = math.exp(-2*math.pi*Nb*Cc_b)  # per UST_v5 formula
inv_TOm = 1/T_Om
# Values reported in docs for sanity check
reported = {
    'kappa_dt_reported': 1.990339,
    'T_Om_reported': 0.23252885,
    'inv_TOm_reported': 4.3005,
    'rOm_rS_reported': 1.578421
}
rOm_rS = 1/Nb
# Build Q-time unit system based on tau_q = kappa_dt (dimensionless tick)
# Define: 1 qsn (q-second) = tau_q ticks; 1 tick is dimensionless; q-time stays dimensionless.
# Provide also an example mapping if one chooses a reference physical rate kappa_ref = 1 Hz (1/s)
# then dt = kappa_dt seconds.

tau_q = kappa_dt
units = [
    ('qtick', 1.0),
    ('qsn (q-saniye)', tau_q),
    ('qdk (q-dakika)', 60*tau_q),
    ('qsaat (q-saat)', 3600*tau_q),
    ('qgün', 86400*tau_q),
    ('qhafta', 7*86400*tau_q),
    ('qay (30 qgün varsayımı)', 30*86400*tau_q),
    ('qyıl (365 qgün varsayımı)', 365*86400*tau_q),
]
df = pd.DataFrame(units, columns=['Birim', 'Tick cinsinden (boyutsuz)'])
# Example in seconds if kappa_ref = 1 Hz
kappa_ref = 1.0
sec_per_tick = 1.0/kappa_ref
sec_per_qsn = tau_q*sec_per_tick
sec_col = [val*sec_per_tick for _,val in units]
df['Örnek: saniye (kappa_ref=1 Hz)'] = sec_col

summary = {
    'kappa_dt (pi*Nsq)': kappa_dt,
    'T_Om (exp(-2pi Nb Cc_b))': T_Om,
    '1/T_Om': inv_TOm,
    'rOm/rS (1/Nb)': rOm_rS,
    'compactness C (Nb*Cc_b)': Nb*Cc_b
}
