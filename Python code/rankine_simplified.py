from tespy.networks import Network

# create a network object with R134a as fluid
my_plant = Network()
my_plant.set_attr(T_unit='C', p_unit='bar', h_unit='kJ / kg')

from tespy.components import (
    CycleCloser, Pump, Condenser, Turbine, SimpleHeatExchanger, Source, Sink
)

# data imput

T_tu_in = 384       # temperature turbine inlet
p_tu_in = 104       # pressure turbine inlet
mf = 54             # mass flow
p_tu_out = 0.05     # pressure turbine outlet

T_coo_in = 16       # temperature cooling water in
T_coo_out = 26      # temperature cooling water out

cc = CycleCloser('cycle closer')
sg = SimpleHeatExchanger('steam generator')
mc = Condenser('main condenser')
tu = Turbine('steam turbine')
fp = Pump('feed pump')

cwso = Source('cooling water source')
cwsi = Sink('cooling water sink')

from tespy.connections import Connection

c1 = Connection(cc, 'out1', tu, 'in1', label='1')
c2 = Connection(tu, 'out1', mc, 'in1', label='2')
c3 = Connection(mc, 'out1', fp, 'in1', label='3')
c4 = Connection(fp, 'out1', sg, 'in1', label='4')
c0 = Connection(sg, 'out1', cc, 'in1', label='0')

my_plant.add_conns(c1, c2, c3, c4, c0)

c11 = Connection(cwso, 'out1', mc, 'in2', label='11')
c12 = Connection(mc, 'out2', cwsi, 'in1', label='12')

my_plant.add_conns(c11, c12)

mc.set_attr(pr1=1, pr2=1)
sg.set_attr(pr=1)
tu.set_attr(eta_s=0.80)         # Turbine isentropic efficiency
fp.set_attr(eta_s=0.90)         # Feed pump isentropic efficiency

c11.set_attr(T=T_coo_in, p=1.2, fluid={'water': 1})
c12.set_attr(T=T_coo_out)
c1.set_attr(T=T_tu_in, p=p_tu_in, m=mf, fluid={'water': 1})
c2.set_attr(p=p_tu_out)


from tespy.connections import Bus

powergen = Bus("electrical power output")
heat_input = Bus('heat input')
heat_input.add_comps({'comp': sg, 'base': 'bus'})

powergen.add_comps(
    {"comp": tu, "char": 0.98 * 0.95, "base": "component"},     # eff_mecc = 0.98, eff_gen = 0.95
    {"comp": fp, "char": 0.95, "base": "bus"},                          # eff_el = 0.95
)

my_plant.add_busses(heat_input, powergen)

my_plant.solve(mode='design')
my_plant.print_results()
