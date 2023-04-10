import sc2
from sc2 import run_game, maps, Race, Difficulty, Result
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, STALKER, STARGATE, VOIDRAY
import random


class SentdeBot(sc2.BotAI):
    def __init__(self, MAX_STALKER, MAX_VOIDRAY):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50
        self.MAX_STALKER = MAX_STALKER
        self.MAX_VOIDRAY = MAX_VOIDRAY


    async def on_step(self, iteration):
        self.iteration = iteration

        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def build_workers(self):
        if (len(self.units(NEXUS)) * 16) > len(self.units(PROBE)) and len(self.units(PROBE)) < self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.idle:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))


    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR, vaspene))

    async def expand(self):
        if self.units(NEXUS).amount < (self.iteration / self.ITERATIONS_PER_MINUTE) and self.can_afford(NEXUS):
            await self.expand_now()

    async def offensive_force_buildings(self):
        #print(self.iteration / self.ITERATIONS_PER_MINUTE)
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

            elif len(self.units(GATEWAY)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)):
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        await self.build(STARGATE, near=pylon)

    async def build_offensive_force(self):
        for gw in self.units(GATEWAY).ready.idle:
            if not self.units(STALKER).amount > self.units(VOIDRAY).amount and self.units(CYBERNETICSCORE):
                if self.can_afford(STALKER) and self.supply_left > 0:
                    await self.do(gw.train(STALKER))

        for sg in self.units(STARGATE).ready.idle:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(VOIDRAY))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {STALKER: self.MAX_STALKER,
                            VOIDRAY: self.MAX_VOIDRAY}
        
        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

            else:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))

max_stalker = 10
max_voidray = 5

for i in range(5):
    wins = 0
    losses = 0

    for j in range(10):
        results = run_game(maps.get("AbyssalReefLE"), [ Bot(Race.Protoss, SentdeBot(max_stalker,max_voidray)), Computer(Race.Terran, Difficulty.Hard)], realtime=False)
        if results == Result.Victory:
            wins += 1
        else:
            losses += 1
    
    f = open("sc2_results.txt","a")
    f.write("----- Experiment Results ------\n")
    f.write("Max Stalker/Voidray : " + str(max_stalker) + "/" + str(max_voidray) + "\n")
    f.write("Total Games: " + str(wins+losses) + "\n")
    f.write("Wins: " + str(wins) + "\n")
    f.write("Losses: " + str(losses) + "\n")
    f.write("Difficulty: Harder\n")
    f.write("Computer Race: Terran\n")
    f.write("*************************\n")
    f.close()

    print ("----- Experiment Results ------")
    print ("Total Games: " + str(wins+losses))
    print ("Wins: " + str(wins))
    print ("Losses: " + str(losses))

    max_stalker += 2
    max_voidray += 1
