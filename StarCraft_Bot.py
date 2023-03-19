import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

# TODO: Come of with a cool name for our bot
class StarCraftBot(sc2.BotAI):
    async def on_step(self, iteration):
    # NOTE: This section tells you what to do at each step
        await self.distribute_workers() # defined in sc2/bot_ai.py

run_game(maps.get("AbyssalReefLE"), [ Bot(Race.Protoss, StarCraftBot()), Computer(Race.Terran, Difficulty.Easy)], realtime=True)