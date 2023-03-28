import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, STALKER, STARGATE, VOIDRAY
import random

# TODO: Come of with a cool name for our bot
class StarCraftBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50

    async def on_step(self, iteration):
        # NOTE: This section tells you what to do at each step
        self.iteration = iteration
        await self.distribute_workers() # defined in sc2/bot_ai.py; makes workers collect resources
        await self.build_workers() # build more workers if resources permit
        await self.build_pylons() # build more pylons if resources permit
        await self.build_assimilator() # structur to collect the gas resource
        await self.expand() # expand to new resources area
        await self.build_offensive_buildings() # build offensive buildings
        await self.build_offensive_forces() # build offensive forces
        await self.attack() # attack enemy with build offensive forces

    async def build_workers(self):
        # NOTE: Nexus is the command ceter and Probe are the workers; there can be more than 1 Nexus
        if (len(self.units(NEXUS)) * 16) > len(self.units(PROBE)) and len(self.units(PROBE)) < self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.idle:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        # NOTE: Pylons increases the amount of units you are allowed to have
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)
    
    async def build_assimilator(self):
        # NOTE: only building assimilator thats within 25 units radius of a Nexus
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(25.0, nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break # If you cant afford dont build
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break # If no worker is available dont build
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR, vaspene))
    
    async def expand(self):
        # NOTE: only building 2 Nexus, may want to build more
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_offensive_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)
            elif len(self.units(GATEWAY)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        await self.build(STARGATE, near=pylon)

    async def build_offensive_forces(self):
        for gateway in self.units(GATEWAY).ready.idle:
            if not self.units(STALKER).amount > self.units(VOIDRAY).amount:
                if self.can_afford(STALKER) and self.supply_left > 0:
                    await self.do(gateway.train(STALKER))
        
        for stargate in self.units(STARGATE).ready.idle:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(stargate.train(VOIDRAY))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0] 
    
    async def attack(self):
        aggressive_units = {STALKER: [15,5], VOIDRAY: [8,3]}

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))


run_game(maps.get("AbyssalReefLE"), [ Bot(Race.Protoss, StarCraftBot()), Computer(Race.Terran, Difficulty.Hard)], realtime=False)