# Copyright (c) 2017-2020 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Synfire chain example
"""
import matplotlib.pyplot as plt
import pyNN.spiNNaker as sim
from spynnaker.pyNN.utilities import neo_convertor

# number of neurons in each population
n_neurons = 100
n_populations = 10
weights = 0.5
delays = 17.0
simtime = 1000

sim.setup(timestep=1.0, min_delay=1.0)

spikeArray = {'spike_times': [[0]]}
stimulus = sim.Population(1, sim.SpikeSourceArray, spikeArray,
                          label='stimulus')

chain_pops = [
    sim.Population(n_neurons, sim.IF_curr_exp, {}, label='chain_{}'.format(i))
    for i in range(n_populations)
]
for pop in chain_pops:
    pop.record("spikes")

connector = sim.FixedNumberPreConnector(10)
for i in range(n_populations):
    sim.Projection(chain_pops[i], chain_pops[(i + 1) % n_populations],
                   connector,
                   synapse_type=sim.StaticSynapse(weight=weights,
                                                  delay=delays))

sim.Projection(stimulus, chain_pops[0], sim.AllToAllConnector(),
               synapse_type=sim.StaticSynapse(weight=5.0))

sim.run(simtime)
# None PyNN method which is faster
# spikes = [pop.spinnaker_get_data("spikes") for pop in chain_pops]

# Pynn method and support method
neos = [pop.get_data("spikes") for pop in chain_pops]
spikes = map(neo_convertor.convert_spikes, neos)

sim.end()


try:
    plt.figure()
    plt.xlabel('Time (ms)')
    plt.ylabel('Neuron')
    plt.title('Spikes Sent By Chain')
    offset = 0
    for pop_spikes in spikes:
        plt.plot(
            [i[1] for i in pop_spikes],
            [i[0] + offset for i in pop_spikes], "."
        )
        offset += n_neurons
    plt.show()
except Exception as ex:
    print(spikes)
    raise ex

    # Way to plot the spikes without neo converter but without the colours
    # try:
    #     import matplotlib.pyplot as plt
    #     import pyNN.utility.plotting as plotting
    #     spike_trains = [neo.segments[0].spiketrains for neo in neos]
    #     offset = 0
    #     for spike_train_list in spike_trains:
    #         for spike_train in spike_train_list:
    #             spike_train.annotations["source_index"] += offset
    #         offset += n_neurons
    #     spike_trains = [
    #         spike_train for spike_train_list in spike_trains
    #         for spike_train in spike_train_list]
    #     panel = plotting.Panel(
    #         spike_trains,
    #         yticks=True, markersize=2, xlim=(0, simtime),
    #         line_properties=[
    #             {"color": colour}
    #             for i, colour in enumerate(colours)])
    #     plotting.Figure(
    #         panel, title="Synfire Example",
    #         annotations="Simulated with {}".format(sim.name()))
    #     plt.show()
    # except Exception as ex:
    #     print(ex)
    #     for neo in neos:
    #         print(neo.segments[0].spiketrains)
    #         print("====")
