import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from tespy.networks import Network

# create a network object with water as fluid
rankine = Network()
rankine.set_attr(T_unit='C', p_unit='bar', h_unit='kJ / kg')

from tespy.components import (
    CycleCloser, Pump, Condenser, Turbine, SimpleHeatExchanger, Source, Sink
)

# data input

T_tu_in = 384       # temperature turbine inlet
p_tu_in = 104       # pressure turbine inlet
mf = 54             # mass flow
p_tu_out = 0.05     # pressure turbine inlet

T_coo_in = 16       # temperature cooling water in
T_coo_out = 26      # temperature cooling water out


cc = CycleCloser('cycle closer')
sg = SimpleHeatExchanger('steam generator')
sgre = SimpleHeatExchanger('steam generator for reheating')
mc = Condenser('main condenser')
tuhp = Turbine('steam turbine HP')
tulp = Turbine('steam turbine LP')
fp = Pump('feed pump')

cwso = Source('cooling water source')
cwsi = Sink('cooling water sink')

from tespy.connections import Connection

c1 = Connection(cc, 'out1', tuhp, 'in1', label='1')
c2 = Connection(tuhp, 'out1', sgre, 'in1', label='2')
c3 = Connection(sgre, 'out1', tulp, 'in1', label='3')
c4 = Connection(tulp, 'out1', mc, 'in1', label='4')
c5 = Connection(mc, 'out1', fp, 'in1', label='5')
c6 = Connection(fp, 'out1', sg, 'in1', label='6')
c0 = Connection(sg, 'out1', cc, 'in1', label='0')

c11 = Connection(cwso, 'out1', mc, 'in2', label='11')
c12 = Connection(mc, 'out2', cwsi, 'in1', label='12')

rankine.add_conns(c1, c2, c3, c4, c5, c6, c0, c11, c12)

mc.set_attr(pr1=1, pr2=1)       # Pressure losses in the condenser
sg.set_attr(pr=0.9)             # Pressure losses in the heating process
sgre.set_attr(pr=0.946)         # Pressure losses in the reheating process
tuhp.set_attr(eta_s=0.80)       # HP Turbine isentropic efficiency
tulp.set_attr(eta_s=0.80)       # LP Turbine isentropic efficiency
fp.set_attr(eta_s=0.90)         # Feed pump isentropic efficiency

c11.set_attr(T=T_coo_in, p=1.2, fluid={'water': 1})
c12.set_attr(T=T_coo_out)
c1.set_attr(T=T_tu_in, m=mf, p=p_tu_in, fluid={'water': 1})
c3.set_attr(T=383, p=19.4)
c4.set_attr(p=p_tu_out)

from tespy.connections import Bus

powergen = Bus("electrical power output")

heat_input = Bus('heat input')
heat_input.add_comps({'comp': sg, 'base': 'bus'})
heat_input.add_comps({'comp': sgre, 'base': 'bus'})

powergen.add_comps(
    {"comp": tuhp, "char": 0.98 * 0.95, "base": "component"},     # eff_mecc = 0.98, eff_gen = 0.95
    {"comp": tulp, "char": 0.98 * 0.95, "base": "component"},
    {"comp": fp, "char": 0.95, "base": "bus"},                          # eff_el = 0.95
)

rankine.add_busses(heat_input, powergen)

rankine.solve(mode='design')
rankine.print_results()


# --------------------------------------
# -------- Boundaries variation --------
# --------------------------------------
import numpy as np


rankine.set_attr(iterinfo=False)

# make text reasonably sized
plt.rc('font', **{'size': 18})

data = {
    'T_livesteam': np.linspace(330, 450, 7),
    'T_cooling': np.linspace(20, 45, 7),
    'p_livesteam': np.linspace(75, 225, 7)
}
eta = {
    'T_livesteam': [],
    'T_cooling': [],
    'p_livesteam': []
}
power = {
    'T_livesteam': [],
    'T_cooling': [],
    'p_livesteam': []
}

for T in data['T_livesteam']:
    c1.set_attr(T=T)
    c3.set_attr(T=T-1)
    rankine.solve('design')
    eta['T_livesteam'] += [abs(powergen.P.val) / sg.Q.val * 100]
    power['T_livesteam'] += [abs(powergen.P.val) / 1e6]

# reset to base temperature
c1.set_attr(T=T_tu_in)
c3.set_attr(T=T_tu_in-1)
mc.set_attr(ttd_u=4)        # Set to a DT of 4 otherwise conflicts in the condenser
c4.set_attr(p=None)

for T in data['T_cooling']:
    c12.set_attr(T=T + 10)
    c11.set_attr(T=T)
    rankine.solve('design')
    eta['T_cooling'] += [abs(powergen.P.val) / sg.Q.val * 100]
    power['T_cooling'] += [abs(powergen.P.val) / 1e6]

# reset to base temperature and pressure output
mc.set_attr(ttd_u=None)
c12.set_attr(T=T_coo_out)
c11.set_attr(T=T_coo_in)
c4.set_attr(p=p_tu_out)

for p in data['p_livesteam']:
    c1.set_attr(p=p)
    rankine.solve('design')
    eta['p_livesteam'] += [abs(powergen.P.val) / sg.Q.val * 100]
    power['p_livesteam'] += [abs(powergen.P.val) / 1e6]

# reset to base pressure
c1.set_attr(p=p_tu_in)

fig, ax = plt.subplots(2, 3, figsize=(16, 8), sharex='col', sharey='row')

ax = ax.flatten()
[a.grid() for a in ax]

i = 0
for key in data:
    ax[i].scatter(data[key], eta[key], s=100, color="#1f567d")
    ax[i + 3].scatter(data[key], power[key], s=100, color="#18a999")
    i += 1

ax[0].set_ylabel('Efficiency in %')
ax[3].set_ylabel('Power in MW')
ax[3].set_xlabel('Live steam temperature in °C')
ax[4].set_xlabel('Feed water temperature in °C')
ax[5].set_xlabel('Live steam pressure in bar')
plt.tight_layout()
plt.show()


# --------------------------------------
# -------- Part Load Simulation --------
# --------------------------------------


c11.set_attr(offdesign=["v"])
c12.set_attr(design=["T"])
c1.set_attr(design=["p"])
c3.set_attr(design=["p"])
tulp.set_attr(offdesign=["cone"])
tuhp.set_attr(offdesign=["cone"])

rankine.solve("design")
rankine.save("rankine_design")

partload_efficiency = []
partload_m_range = np.linspace(mf, mf/5, 10)

for m in partload_m_range:
    c1.set_attr(m=m)
    rankine.solve("offdesign", design_path="rankine_design")
    partload_efficiency += [abs(powergen.P.val) / sg.Q.val * 100]

with mplstyle.context('ggplot', after_reset=False):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(partload_m_range, partload_efficiency, marker='o', linestyle='-', color="#1f567d", markersize=8,
            linewidth=2)
    ax.grid(True)

    ax.set_xlabel("Mass Flow (kg/s)", fontsize=14)
    ax.set_ylabel("Plant Electrical Efficiency (%)", fontsize=14)
    ax.set_title("Relationship Between Mass Flow and Plant Electrical Efficiency", fontsize=16)

    plt.tight_layout()
    plt.savefig("Part_Load.svg", format='svg', dpi=300)
    plt.show()
