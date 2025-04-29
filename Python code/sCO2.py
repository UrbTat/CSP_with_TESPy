from tespy.networks import Network
from tespy.components import (
    Sink, Source, Turbine, SimpleHeatExchanger, Merge, Splitter,
    HeatExchanger, CycleCloser, Compressor, Valve)
from tespy.connections import Connection, Bus
import numpy as np
from matplotlib import pyplot as plt

# setting up network
jouleCycle = Network(fluids=['CO2'])
jouleCycle.set_attr(
    T_unit='C', p_unit='bar', h_unit='kJ / kg', m_unit='kg / s',
    s_unit="kJ / kgK")

# components definition
water_in = Source('Water source')
water_out = Sink('Water sink')

closer = CycleCloser('Cycle closer')

cp1 = Compressor('Compressor 1', fkt_group='CMP')
cp2 = Compressor('Compressor 2', fkt_group='CMP')

rec1 = HeatExchanger('Recuperator 1', fkt_group='REC')
rec2 = HeatExchanger('Recuperator 2', fkt_group='REC')

cooler = SimpleHeatExchanger('Water cooler')
heater = SimpleHeatExchanger('Heater')

turb = Turbine('Turbine')

sp1 = Splitter('Splitter 1', fkt_group='REC')
m1 = Merge('Merge 1', fkt_group='REC')

# connections definition
# power cycle
c1 = Connection(cooler, 'out1', cp1, 'in1', label='1')
c2 = Connection(cp1, 'out1', rec1, 'in2', label='2')
c3 = Connection(rec2, 'out2', heater, 'in1', label='3')

c0 = Connection(heater, 'out1', closer, 'in1', label='0')
c4 = Connection(closer, 'out1', turb, 'in1', label='4')
c5 = Connection(turb, 'out1', rec2, 'in1', label='5')
c6 = Connection(sp1, 'out1', cooler, 'in1', label='6')

c10 = Connection(sp1, 'out2', cp2, 'in1', label='10')
c11 = Connection(cp2, 'out1', m1, 'in2', label='11')
c12 = Connection(rec1, 'out2', m1, 'in1', label='12')
c13 = Connection(m1, 'out1', rec2, 'in2', label='13')

c14 = Connection(rec2, 'out1', rec1, 'in1', label='14')
c15 = Connection(rec1, 'out1', sp1, 'in1', label='15')

# add connections to network
jouleCycle.add_conns(c0, c1, c2, c3, c4, c5, c6, c10, c11, c12, c13, c14, c15)

# power bus
power = Bus('total output power')
power.add_comps({'comp': turb, 'char': 0.99 * 0.99, 'base': 'component'},
                {'comp': cp1, 'char': 0.98 * 0.97, 'base': 'bus'},
                {'comp': cp2, 'char': 0.98 * 0.97, 'base': 'bus'})

heat_input_bus = Bus('heat input')
heat_input_bus.add_comps({'comp': heater, 'base': 'bus'})

jouleCycle.add_busses(heat_input_bus, power)

# connection parameters
c1.set_attr(T=35, p=75, fluid={'CO2': 1})
#c3.set_attr(T=520)
c4.set_attr(T=700, p=258, m=54)
c5.set_attr(p=78)
rec1.set_attr(pr1=0.977, pr2=0.998, ttd_l=10, ttd_u=25)
rec2.set_attr(pr1=0.987, pr2=0.997, ttd_l=10)
heater.set_attr(pr=0.973)

# component parameters
turb.set_attr(eta_s=0.9)
cp1.set_attr(eta_s=0.85)
cp2.set_attr(eta_s=0.85)

# solve final state
jouleCycle.solve(mode='design')

# print results to prompt and generate model documentation
jouleCycle.print_results()

W_net = abs(power.P.val)
Q_in = heater.Q.val
print("Efficiency:", W_net/Q_in)

# --------------------------------------
# -------- Boundaries variation --------
# --------------------------------------

jouleCycle.set_attr(iterinfo=False)

# make text reasonably sized
plt.rc('font', **{'size': 18})

data = {
    'T_livesteam': np.linspace(350, 850, 10)
}
eta = {
    'T_livesteam': []
}
power = {
    'T_livesteam': []
}

for T in data['T_livesteam']:
    c4.set_attr(T=T)
    jouleCycle.solve('design')
    eta['T_livesteam'] += [abs(turb.P.val + cp1.P.val + cp2.P.val) / heater.Q.val * 100]
    power['T_livesteam'] += [abs(turb.P.val + cp1.P.val + cp2.P.val) / 1e6]

# reset to base temperature
c4.set_attr(T=700)

fig, ax = plt.subplots(2, 1, figsize=(16, 8), sharex='col', sharey='row')

ax = ax.flatten()
[a.grid() for a in ax]

i = 0
for key in data:
    # Plotting lines
    ax[i].plot(data[key], eta[key], color="#1f567d")
    ax[i + 1].plot(data[key], power[key], color="#18a999")
    # Plotting points
    ax[i].scatter(data[key], eta[key], s=100, color="#1f567d")
    ax[i + 1].scatter(data[key], power[key], s=100, color="#18a999")
    i += 1

ax[0].set_ylabel('Efficiency in %')
ax[1].set_ylabel('Power in MW')
ax[1].set_xlabel('Turbine inlet temperature in °C')
plt.tight_layout()
plt.show()



