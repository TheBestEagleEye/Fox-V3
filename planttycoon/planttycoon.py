import asyncio
import collections
import datetime
import time
from random import choice

import discord
from redbot.core import commands, Config, bank
from redbot.core.bot import Red
from typing import Any

Cog: Any = getattr(commands, "Cog", object)


class Gardener:
    """Gardener class"""

    def __init__(self, user: discord.User, config: Config):
        self.user = user
        self.config = config
        self.badges = []
        self.points = 0
        self.products = {}
        self.current = {}

    def __str__(self):
        return (
            "Gardener named {}\n"
            "Badges: {}\n"
            "Points: {}\n"
            "Products: {}\n"
            "Current: {}".format(self.user, self.badges, self.points, self.products, self.current)
        )

    def __repr__(self):
        return "{} - {} - {} - {} - {}".format(
            self.user, self.badges, self.points, self.products, self.current
        )

    async def _load_config(self):
        self.badges = await self.config.user(self.user).badges()
        self.points = await self.config.user(self.user).points()
        self.products = await self.config.user(self.user).products()
        self.current = await self.config.user(self.user).current()

    async def save_gardener(self):
        await self.config.user(self.user).badges.set(self.badges)
        await self.config.user(self.user).points.set(self.points)
        await self.config.user(self.user).products.set(self.products)
        await self.config.user(self.user).current.set(self.current)


async def _die_in(gardener, degradation):
    #
    # Calculating how much time in minutes remains until the plant's health hits 0
    #

    return int(gardener.current["health"] / degradation.degradation)


async def _grow_time(gardener):
    #
    # Calculating the remaining grow time for a plant
    #

    now = int(time.time())
    then = gardener.current["timestamp"]
    return (gardener.current["time"] - (now - then)) / 60


async def _send_message(channel, message):
    """Sendsa message"""

    em = discord.Embed(description=message, color=discord.Color.green())
    await channel.send(embed=em)


async def _withdraw_points(gardener: Gardener, amount):
    #
    # Substract points from the gardener
    #

    if (gardener.points - amount) < 0:
        return False
    else:
        gardener.points -= amount
        return True


class PlantTycoon(Cog):
    """Grow your own plants! Be sure to take proper care of it."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=80108971101168412199111111110)

        default_user = {"badges": [], "points": 0, "products": {}, "current": {}}

        self.config.register_user(**default_user)

        self.plants = {
            "plants": [
                {
                    "name": "Poppy",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/S4hjyUX.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Dandelion",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/emqnQP2.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Daisy",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/lcFq4AB.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Chrysanthemum",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/5jLtqWL.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Pansy",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/f7TgD1b.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Lavender",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/g3OmOSK.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Lily",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/0hzy7lO.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Petunia",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/rJm8ISv.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Sunflower",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/AzgzQK9.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Daffodil",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/pnCCRsH.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Clover",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/jNTgirw.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Tulip",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/kodIFjE.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Rose",
                    "article": "a",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/sdTNiOH.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Aster",
                    "article": "an",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/1tN04Hl.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Aloe Vera",
                    "article": "an",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/WFAYIpx.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Orchid",
                    "article": "an",
                    "time": 3600,
                    "rarity": "common",
                    "image": "http://i.imgur.com/IQrQYDC.jpg",
                    "health": 100,
                    "degradation": 0.625,
                    "threshold": 110,
                    "badge": "Flower Power",
                    "reward": 600,
                },
                {
                    "name": "Dragon Fruit Plant",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/pfngpDS.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Mango Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/ybR78Oc.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Lychee Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/w9LkfhX.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Durian Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/jh249fz.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Fig Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/YkhnpEV.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Jack Fruit Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/2D79TlA.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Prickly Pear Plant",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/GrcGAGj.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Pineapple Plant",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/VopYQtr.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Citron Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/zh7Dr23.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Cherimoya Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/H62gQK6.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Mangosteen Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/McNnMqa.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Guava Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/iy8WgPt.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Orange Tree",
                    "article": "an",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/lwjEJTm.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Apple Tree",
                    "article": "an",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/QI3UTR3.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Sapodilla Tree",
                    "article": "a",
                    "time": 5400,
                    "rarity": "uncommon",
                    "image": "http://i.imgur.com/6BvO5Fu.jpg",
                    "health": 100,
                    "degradation": 0.75,
                    "threshold": 110,
                    "badge": "Fruit Brute",
                    "reward": 1200,
                },
                {
                    "name": "Franklin Tree",
                    "article": "a",
                    "time": 7200,
                    "rarity": "rare",
                    "image": "http://i.imgur.com/hoh17hp.jpg",
                    "health": 100,
                    "degradation": 1.5,
                    "threshold": 110,
                    "badge": "Sporadic",
                    "reward": 2400,
                },
                {
                    "name": "Parrot's Beak",
                    "article": "a",
                    "time": 7200,
                    "rarity": "rare",
                    "image": "http://i.imgur.com/lhSjfQY.jpg",
                    "health": 100,
                    "degradation": 1.5,
                    "threshold": 110,
                    "badge": "Sporadic",
                    "reward": 2400,
                },
                {
                    "name": "Koki'o",
                    "article": "a",
                    "time": 7200,
                    "rarity": "rare",
                    "image": "http://i.imgur.com/Dhw9ync.jpg",
                    "health": 100,
                    "degradation": 1.5,
                    "threshold": 110,
                    "badge": "Sporadic",
                    "reward": 2400,
                },
                {
                    "name": "Jade Vine",
                    "article": "a",
                    "time": 7200,
                    "rarity": "rare",
                    "image": "http://i.imgur.com/h4fJo2R.jpg",
                    "health": 100,
                    "degradation": 1.5,
                    "threshold": 110,
                    "badge": "Sporadic",
                    "reward": 2400,
                },
                {
                    "name": "Venus Fly Trap",
                    "article": "a",
                    "time": 7200,
                    "rarity": "rare",
                    "image": "http://i.imgur.com/NoSdxXh.jpg",
                    "health": 100,
                    "degradation": 1.5,
                    "threshold": 110,
                    "badge": "Sporadic",
                    "reward": 2400,
                },
                {
                    "name": "Chocolate Cosmos",
                    "article": "a",
                    "time": 7200,
                    "rarity": "rare",
                    "image": "http://i.imgur.com/4ArSekX.jpg",
                    "health": 100,
                    "degradation": 1.5,
                    "threshold": 110,
                    "badge": "Sporadic",
                    "reward": 2400,
                },
                {
                    "name": "Pizza Plant",
                    "article": "a",
                    "time": 9000,
                    "rarity": "super-rare",
                    "image": "http://i.imgur.com/ASZXr7C.png",
                    "health": 100,
                    "degradation": 2,
                    "threshold": 110,
                    "badge": "Odd-pod",
                    "reward": 3600,
                },
                # {
                #     "name": "tba",
                #     "article": "a",
                #     "time": 9000,
                #     "rarity": "super-rare",
                #     "image": "tba",
                #     "health": 100,
                #     "degradation": 1.5,
                #     "threshold": 110,
                #     "badge": "Odd-pod",
                #     "reward": 3600
                # },
                {
                    "name": "Piranha Plant",
                    "article": "a",
                    "time": 9000,
                    "rarity": "super-rare",
                    "image": "http://i.imgur.com/c03i9W7.jpg",
                    "health": 100,
                    "degradation": 2,
                    "threshold": 110,
                    "badge": "Odd-pod",
                    "reward": 3600,
                },
                # {
                #     "name": "tba",
                #     "article": "a",
                #     "time": 9000,
                #     "rarity": "super-rare",
                #     "image": "tba",
                #     "health": 100,
                #     "degradation": 1.5,
                #     "threshold": 110,
                #     "badge": "Odd-pod",
                #     "reward": 3600
                # },
                {
                    "name": "Peashooter",
                    "article": "a",
                    "time": 9000,
                    "rarity": "super-rare",
                    "image": "https://i.imgur.com/Vo4v2Ry.png",
                    "health": 100,
                    "degradation": 2,
                    "threshold": 110,
                    "badge": "Odd-pod",
                    "reward": 3600,
                },
                {
                    "name": "Eldergleam Tree",
                    "article": "a",
                    "time": 10800,
                    "rarity": "epic",
                    "image": "https://i.imgur.com/pnZYKZc.jpg",
                    "health": 100,
                    "degradation": 2.5,
                    "threshold": 110,
                    "badge": "Greenfingers",
                    "reward": 5400,
                },
                {
                    "name": "Pikmin",
                    "article": "a",
                    "time": 10800,
                    "rarity": "epic",
                    "image": "http://i.imgur.com/sizf7hE.png",
                    "health": 100,
                    "degradation": 2.5,
                    "threshold": 110,
                    "badge": "Greenfingers",
                    "reward": 5400,
                },
                {
                    "name": "Flora Colossus",
                    "article": "a",
                    "time": 10800,
                    "rarity": "epic",
                    "image": "http://i.imgur.com/9f5QzaW.jpg",
                    "health": 100,
                    "degradation": 2.5,
                    "threshold": 110,
                    "badge": "Greenfingers",
                    "reward": 5400,
                },
                {
                    "name": "Plantera Bulb",
                    "article": "a",
                    "time": 10800,
                    "rarity": "epic",
                    "image": "https://i.imgur.com/ExqLLHO.png",
                    "health": 100,
                    "degradation": 2.5,
                    "threshold": 110,
                    "badge": "Greenfingers",
                    "reward": 5400,
                },
                {
                    "name": "Chorus Tree",
                    "article": "an",
                    "time": 10800,
                    "rarity": "epic",
                    "image": "https://i.imgur.com/tv2B72j.png",
                    "health": 100,
                    "degradation": 2.5,
                    "threshold": 110,
                    "badge": "Greenfingers",
                    "reward": 5400,
                },
                {
                    "name": "Money Tree",
                    "article": "a",
                    "time": 35400,
                    "rarity": "legendary",
                    "image": "http://i.imgur.com/MIJQDLL.jpg",
                    "health": 100,
                    "degradation": 8,
                    "threshold": 110,
                    "badge": "Nobel Peas Prize",
                    "reward": 10800,
                },
                {
                    "name": "Truffula Tree",
                    "article": "a",
                    "time": 35400,
                    "rarity": "legendary",
                    "image": "http://i.imgur.com/cFSmaHH.png",
                    "health": 100,
                    "degradation": 8,
                    "threshold": 110,
                    "badge": "Nobel Peas Prize",
                    "reward": 10800,
                },
                {
                    "name": "Whomping Willow",
                    "article": "a",
                    "time": 35400,
                    "rarity": "legendary",
                    "image": "http://i.imgur.com/Ibwm2xY.jpg",
                    "health": 100,
                    "degradation": 8,
                    "threshold": 110,
                    "badge": "Nobel Peas Prize",
                    "reward": 10800,
                },
            ],
            "event": {
                "January": {
                    "name": "Tanabata Tree",
                    "article": "a",
                    "time": 70800,
                    "rarity": "event",
                    "image": "http://i.imgur.com/FD38JJj.jpg",
                    "health": 100,
                    "degradation": 9,
                    "threshold": 110,
                    "badge": "Annualsary",
                    "reward": 21600,
                },
                "February": {
                    "name": "Chocolate Rose",
                    "article": "a",
                    "time": 70800,
                    "rarity": "event",
                    "image": "http://i.imgur.com/Sqg6pcG.jpg",
                    "health": 100,
                    "degradation": 9,
                    "threshold": 110,
                    "badge": "Annualsary",
                    "reward": 21600,
                },
                "March": {
                    "name": "Shamrock",
                    "article": "a",
                    "time": 70800,
                    "rarity": "event",
                    "image": "http://i.imgur.com/kVig04M.jpg",
                    "health": 100,
                    "degradation": 9,
                    "threshold": 110,
                    "badge": "Annualsary",
                    "reward": 21600,
                },
                "April": {
                    "name": "Easter Egg Eggplant",
                    "article": "an",
                    "time": 70800,
                    "rarity": "event",
                    "image": "http://i.imgur.com/5jltGQa.jpg",
                    "health": 100,
                    "degradation": 9,
                    "threshold": 110,
                    "badge": "Annualsary",
                    "reward": 21600,
                },
                "October": {
                    "name": "Jack O' Lantern",
                    "article": "a",
                    "time": 70800,
                    "rarity": "event",
                    "image": "http://i.imgur.com/efApsxG.jpg",
                    "health": 100,
                    "degradation": 9,
                    "threshold": 110,
                    "badge": "Annualsary",
                    "reward": 21600,
                },
                "November": {
                    "name": "Mayflower",
                    "article": "a",
                    "time": 70800,
                    "rarity": "event",
                    "image": "http://i.imgur.com/nntNtoL.jpg",
                    "health": 100,
                    "degradation": 9,
                    "threshold": 110,
                    "badge": "Annualsary",
                    "reward": 21600,
                },
                "December": {
                    "name": "Holly",
                    "article": "a",
                    "time": 70800,
                    "rarity": "event",
                    "image": "http://i.imgur.com/maDLmJC.jpg",
                    "health": 100,
                    "degradation": 9,
                    "threshold": 110,
                    "badge": "Annualsary",
                    "reward": 21600,
                },
            },
        }

        self.products = {
            "water": {
                "cost": 5,
                "health": 10,
                "damage": 45,
                "modifier": 0,
                "category": "water",
                "uses": 1,
            },
            "manure": {
                "cost": 20,
                "health": 20,
                "damage": 55,
                "modifier": -0.035,
                "category": "fertilizer",
                "uses": 1,
            },
            "vermicompost": {
                "cost": 35,
                "health": 30,
                "damage": 60,
                "modifier": -0.5,
                "category": "fertilizer",
                "uses": 1,
            },
            "nitrates": {
                "cost": 70,
                "health": 60,
                "damage": 75,
                "modifier": -0.08,
                "category": "fertilizer",
                "uses": 1,
            },
            "pruner": {
                "cost": 500,
                "health": 40,
                "damage": 90,
                "modifier": -0.065,
                "category": "tool",
                "uses": 10,
            },
        }

        self.defaults = {
            "points": {
                "buy": 5,
                "add_health": 5,
                "fertilize": 10,
                "pruning": 20,
                "pesticide": 25,
                "growing": 5,
                "damage": 25,
            },
            "timers": {"degradation": 1, "completion": 1, "notification": 5},
            "degradation": {"base_degradation": 1.5},
            "notification": {"max_health": 50},
        }

        self.badges = {
            "badges": {
                "Flower Power": {},
                "Fruit Brute": {},
                "Sporadic": {},
                "Odd-pod": {},
                "Greenfingers": {},
                "Nobel Peas Prize": {},
                "Annualsary": {},
            }
        }

        self.notifications = {
            "messages": [
                "The soil seems dry, maybe you could give your plant some water?",
                "Your plant seems a bit droopy. I would give it some fertilizer if I were you.",
                "Your plant seems a bit too overgrown. You should probably trim it a bit.",
            ]
        }

        #
        # Starting loops
        #

        self.completion_task = bot.loop.create_task(self.check_completion())
        self.degradation_task = bot.loop.create_task(self.check_degradation())
        self.notification_task = bot.loop.create_task(self.send_notification())

        #
        # Loading bank
        #

        # self.bank = bot.get_cog('Economy').bank

    async def _gardener(self, user: discord.User) -> Gardener:

        #
        # This function returns an individual gardener namedtuple
        #

        g = Gardener(user, self.config)
        await g._load_config()
        return g

    async def _degradation(self, gardener: Gardener):

        #
        # Calculating the rate of degradation per check_completion() cycle.
        #

        modifiers = sum(
            [
                self.products[product]["modifier"]
                for product in gardener.products
                if gardener.products[product] > 0
            ]
        )

        degradation = (
            100
            / (gardener.current["time"] / 60)
            * (self.defaults["degradation"]["base_degradation"] + gardener.current["degradation"])
        ) + modifiers

        d = collections.namedtuple("degradation", "degradation time modifiers")

        return d(degradation=degradation, time=gardener.current["time"], modifiers=modifiers)

    # async def _get_member(self, user_id):
    #
    #     #
    #     # Return a member object
    #     #
    #
    #     return discord.User(id=user_id)  # I made it a string just to be sure
    #
    # async def _send_notification(self, user_id, message):
    #
    #     #
    #     # Sends a Direct Message to the gardener
    #     #
    #
    #     member = await self._get_member(user_id)
    #     em = discord.Embed(description=message, color=discord.Color.green())
    #     await self.bot.send_message(member, embed=em)

    async def _add_health(self, channel, gardener: Gardener, product, product_category):

        #
        # The function to add health
        #

        product = product.lower()
        product_category = product_category.lower()
        if product in self.products and self.products[product]["category"] == product_category:
            if product in gardener.products:
                if gardener.products[product] > 0:
                    gardener.current["health"] += self.products[product]["health"]
                    gardener.products[product] -= 1
                    if gardener.products[product] == 0:
                        del gardener.products[product.lower()]
                    if product_category == "water":
                        emoji = ":sweat_drops:"
                    elif product_category == "fertilizer":
                        emoji = ":poop:"
                    # elif product_category == "tool":
                    else:
                        emoji = ":scissors:"
                    message = "Your plant got some health back! {}".format(emoji)
                    if gardener.current["health"] > gardener.current["threshold"]:
                        gardener.current["health"] -= self.products[product]["damage"]
                        if product_category == "tool":
                            damage_msg = "You used {} too many times!".format(product)
                        else:
                            damage_msg = "You gave too much of {}.".format(product)
                        message = "{} Your plant lost some health. :wilted_rose:".format(
                            damage_msg
                        )
                    gardener.points += self.defaults["points"]["add_health"]
                    await gardener.save_gardener()
                else:
                    message = "You have no {}. Go buy some!".format(product)
            else:
                if product_category == "tool":
                    message = "You have don't have a {}. Go buy one!".format(product)
                else:
                    message = "You have no {}. Go buy some!".format(product)
        else:
            message = "Are you sure you are using {}?".format(product_category)

        if product_category == "water":
            emcolor = discord.Color.blue()
        elif product_category == "fertilizer":
            emcolor = discord.Color.dark_gold()
        # elif product_category == "tool":
        else:
            emcolor = discord.Color.dark_grey()

        em = discord.Embed(description=message, color=emcolor)
        await channel.send(embed=em)

    @commands.group(name="gardening", autohelp=False)
    async def _gardening(self, ctx: commands.Context):
        """Gardening commands."""
        if ctx.invoked_subcommand is None:
            prefix = ctx.prefix

            title = "**Welcome to Plant Tycoon.**\n"
            description = """'Grow your own plant. Be sure to take proper care of yours.\n
            If it successfully grows, you get a reward.\n
            As you nurture your plant, you gain Thneeds which can be exchanged for credits.\n\n
            **Commands**\n\n
            ``{0}gardening seed``: Plant a seed inside the earth.\n
            ``{0}gardening profile``: Check your gardening profile.\n
            ``{0}gardening plants``: Look at the list of the available plants.\n
            ``{0}gardening plant``: Look at the details of a plant.\n
            ``{0}gardening state``: Check the state of your plant.\n
            ``{0}gardening buy``: Buy gardening supplies.\n
            ``{0}gardening convert``: Exchange Thneeds for credits.\n
            ``{0}shovel``: Shovel your plant out.\n
            ``{0}water``: Water your plant.\n
            ``{0}fertilize``: Fertilize the soil.\n
            ``{0}prune``: Prune your plant.\n"""

            em = discord.Embed(
                title=title, description=description.format(prefix), color=discord.Color.green()
            )
            em.set_thumbnail(url="https://image.prntscr.com/image/AW7GuFIBSeyEgkR2W3SeiQ.png")
            em.set_footer(
                text="This cog was made by SnappyDragon18 and PaddoInWonderland. Inspired by The Lorax (2012)."
            )
            await ctx.send(embed=em)

    @_gardening.command(name="seed")
    async def _seed(self, ctx: commands.Context):
        """Plant a seed inside the earth."""
        author = ctx.author
        # server = context.message.server
        # if author.id not in self.gardeners:
        #     self.gardeners[author.id] = {}
        #     self.gardeners[author.id]['current'] = False
        #     self.gardeners[author.id]['points'] = 0
        #     self.gardeners[author.id]['badges'] = []
        #     self.gardeners[author.id]['products'] = {}
        gardener = await self._gardener(author)

        if not gardener.current:
            d = datetime.date.today()
            month = d.month

            #
            # Event Plant Check start
            #
            plant_options = []

            if month == 1:
                plant_options.append(self.plants["event"]["January"])
            elif month == 2:
                plant_options.append(self.plants["event"]["February"])
            elif month == 3:
                plant_options.append(self.plants["event"]["March"])
            elif month == 4:
                plant_options.append(self.plants["event"]["April"])
            elif month == 10:
                plant_options.append(self.plants["event"]["October"])
            elif month == 11:
                plant_options.append(self.plants["event"]["November"])
            elif month == 12:
                plant_options.append(self.plants["event"]["December"])

            plant_options.append(self.plants["plants"])

            #
            # Event Plant Check end
            #

            plant = choice(plant_options)
            plant["timestamp"] = int(time.time())
            # index = len(self.plants["plants"]) - 1
            # del [self.plants["plants"][index]]
            message = (
                "During one of your many heroic adventures, you came across a mysterious bag that said "
                '"pick one". To your surprise it had all kinds of different seeds in them. '
                "And now that you're home, you want to plant it. "
                "You went to a local farmer to identify the seed, and the farmer "
                "said it was {} **{} ({})** seed.\n\n"
                "Take good care of your seed and water it frequently. "
                "Once it blooms, something nice might come from it. "
                "If it dies, however, you will get nothing.".format(
                    plant["article"], plant["name"], plant["rarity"]
                )
            )
            if "water" not in gardener.products:
                gardener.products["water"] = 0
            gardener.products["water"] += 5
            gardener.current = plant
            await gardener.save_gardener()

            em = discord.Embed(description=message, color=discord.Color.green())
        else:
            plant = gardener.current
            message = "You're already growing {} **{}**, silly.".format(
                plant["article"], plant["name"]
            )
            em = discord.Embed(description=message, color=discord.Color.green())

        await ctx.send(embed=em)

    @_gardening.command(name="profile")
    async def _profile(self, ctx: commands.Context, *, member: discord.Member = None):
        """Check your gardening profile."""
        if member:
            author = member
        else:
            author = ctx.author

        gardener = await self._gardener(author)
        em = discord.Embed(color=discord.Color.green())  # , description='\a\n')
        avatar = author.avatar_url if author.avatar else author.default_avatar_url
        em.set_author(name="Gardening profile of {}".format(author.name), icon_url=avatar)
        em.add_field(name="**Thneeds**", value=str(gardener.points))
        if not gardener.current:
            em.add_field(name="**Currently growing**", value="None")
        else:
            em.set_thumbnail(url=gardener.current["image"])
            em.add_field(
                name="**Currently growing**",
                value="{0} ({1:.2f}%)".format(
                    gardener.current["name"], gardener.current["health"]
                ),
            )
        if not gardener.badges:
            em.add_field(name="**Badges**", value="None")
        else:
            badges = ""
            for badge in gardener.badges:
                badges += "{}\n".format(badge.capitalize())
            em.add_field(name="**Badges**", value=badges)
        if not gardener.products:
            em.add_field(name="**Products**", value="None")
        else:
            products = ""
            for product in gardener.products:
                products += "{} ({}) {}\n".format(
                    product.capitalize(),
                    gardener.products[product] / self.products[product.lower()]["uses"],
                    self.products[product]["modifier"],
                )
            em.add_field(name="**Products**", value=products)
        if gardener.current:
            degradation = await self._degradation(gardener)
            die_in = await _die_in(gardener, degradation)
            to_grow = await _grow_time(gardener)
            em.set_footer(
                text="Total degradation: {0:.2f}% / {1} min (100 / ({2} / 60) * (BaseDegr {3:.2f} + PlantDegr {4:.2f}))"
                " + ModDegr {5:.2f}) Your plant will die in {6} minutes "
                "and {7:.1f} minutes to go for flowering.".format(
                    degradation.degradation,
                    self.defaults["timers"]["degradation"],
                    degradation.time,
                    self.defaults["degradation"]["base_degradation"],
                    gardener.current["degradation"],
                    degradation.modifiers,
                    die_in,
                    to_grow,
                )
            )
        await ctx.send(embed=em)

    @_gardening.command(name="plants")
    async def _plants(self, ctx):
        """Look at the list of the available plants."""
        tick = ""
        tock = ""
        tick_tock = 0
        for plant in self.plants["plants"]:
            if tick_tock == 0:
                tick += "**{}**\n".format(plant["name"])
                tick_tock = 1
            else:
                tock += "**{}**\n".format(plant["name"])
                tick_tock = 0
        em = discord.Embed(title="All plants that are growable", color=discord.Color.green())
        em.add_field(name="\a", value=tick)
        em.add_field(name="\a", value=tock)
        await ctx.send(embed=em)

    @_gardening.command(name="plant")
    async def _plant(self, ctx: commands.Context, *plant):
        """Look at the details of a plant."""
        plant = " ".join(plant)
        t = False
        for p in self.plants["plants"]:
            if p["name"].lower() == plant.lower():
                plant = p
                t = True
                break
        if t:
            em = discord.Embed(
                title="Plant statistics of {}".format(plant["name"]), color=discord.Color.green()
            )
            em.set_thumbnail(url=plant["image"])
            em.add_field(name="**Name**", value=plant["name"])
            em.add_field(name="**Rarity**", value=plant["rarity"].capitalize())
            em.add_field(name="**Grow Time**", value="{0:.1f} minutes".format(plant["time"] / 60))
            em.add_field(name="**Damage Threshold**", value="{}%".format(plant["threshold"]))
            em.add_field(name="**Badge**", value=plant["badge"])
            em.add_field(name="**Reward**", value="{} τ".format(plant["reward"]))
        else:
            message = "What plant?"
            em = discord.Embed(description=message, color=discord.Color.red())
            await ctx.send_help()
        await ctx.send(embed=em)

    @_gardening.command(name="state")
    async def _state(self, ctx):
        """Check the state of your plant."""
        author = ctx.author
        gardener = await self._gardener(author)
        if not gardener.current:
            message = "You're currently not growing a plant."
            em_color = discord.Color.red()
        else:
            plant = gardener.current
            degradation = await self._degradation(gardener)
            die_in = await _die_in(gardener, degradation)
            to_grow = await _grow_time(gardener)
            message = (
                "You're growing {0} **{1}**. "
                "Its health is **{2:.2f}%** and still has to grow for **{3:.1f}** minutes. "
                "It is losing **{4:.2f}%** per minute and will die in **{5:.1f}** minutes.".format(
                    plant["article"],
                    plant["name"],
                    plant["health"],
                    to_grow,
                    degradation.degradation,
                    die_in,
                )
            )
            em_color = discord.Color.green()
        em = discord.Embed(description=message, color=em_color)
        await ctx.send(embed=em)

    @_gardening.command(name="buy")
    async def _buy(self, ctx, product=None, amount: int = 1):
        """Buy gardening supplies."""
        author = ctx.author
        if product is None:
            em = discord.Embed(
                title="All gardening supplies that you can buy:", color=discord.Color.green()
            )
            for product in self.products:
                em.add_field(
                    name="**{}**".format(product.capitalize()),
                    value="Cost: {} τ\n+{} health\n-{}% damage\nUses: {}\nCategory: {}".format(
                        self.products[product]["cost"],
                        self.products[product]["health"],
                        self.products[product]["damage"],
                        self.products[product]["uses"],
                        self.products[product]["category"],
                    ),
                )
            await ctx.send(embed=em)
        else:
            if amount <= 0:
                message = "Invalid amount! Must be greater than 1"
            else:
                gardener = await self._gardener(author)
                if product.lower() in self.products and amount > 0:
                    cost = self.products[product.lower()]["cost"] * amount
                    withdraw_points = await _withdraw_points(gardener, cost)
                    if withdraw_points:
                        if product.lower() not in gardener.products:
                            gardener.products[product.lower()] = 0
                        gardener.products[product.lower()] += amount
                        gardener.products[product.lower()] += (
                            amount * self.products[product.lower()]["uses"]
                        )
                        await gardener.save_gardener()
                        message = "You bought {}.".format(product.lower())
                    else:
                        message = "You don't have enough Thneeds. You have {}, but need {}.".format(
                            gardener.points, self.products[product.lower()]["cost"] * amount
                        )
                else:
                    message = "I don't have this product."
            em = discord.Embed(description=message, color=discord.Color.green())
            await ctx.send(embed=em)

    @_gardening.command(name="convert")
    async def _convert(self, ctx: commands.Context, amount: int):
        """Exchange Thneeds for credits."""
        author = ctx.author
        gardener = await self._gardener(author)

        withdraw_points = await _withdraw_points(gardener, amount)
        plural = ""
        if amount > 0:
            plural = "s"
        if withdraw_points:
            await bank.deposit_credits(author, amount)
            message = "{} Thneed{} successfully exchanged for credits.".format(amount, plural)
            await gardener.save_gardener()
        else:
            message = "You don't have enough Thneed{}. " "You have {}, but need {}.".format(
                plural, gardener.points, amount
            )

        em = discord.Embed(description=message, color=discord.Color.green())
        await ctx.send(embed=em)

    @commands.command(name="shovel")
    async def _shovel(self, ctx: commands.Context):
        """Shovel your plant out."""
        author = ctx.author
        gardener = await self._gardener(author)
        if not gardener.current:
            message = "You're currently not growing a plant."
        else:
            gardener.current = {}
            message = "You sucessfuly shovelled your plant out."
            if gardener.points < 0:
                gardener.points = 0
            await gardener.save_gardener()

        em = discord.Embed(description=message, color=discord.Color.dark_grey())
        await ctx.send(embed=em)

    @commands.command(name="water")
    async def _water(self, ctx):
        """Water your plant."""
        author = ctx.author
        channel = ctx.channel
        gardener = await self._gardener(author)
        product = "water"
        product_category = "water"
        if not gardener.current:
            message = "You're currently not growing a plant."
            await _send_message(channel, message)
        else:
            await self._add_health(channel, gardener, product, product_category)

    @commands.command(name="fertilize")
    async def _fertilize(self, ctx, fertilizer):
        """Fertilize the soil."""
        gardener = await self._gardener(ctx.author)
        channel = ctx.channel
        product = fertilizer
        product_category = "fertilizer"
        if not gardener.current:
            message = "You're currently not growing a plant."
            await _send_message(channel, message)
        else:
            await self._add_health(channel, gardener, product, product_category)

    @commands.command(name="prune")
    async def _prune(self, ctx):
        """Prune your plant."""
        gardener = await self._gardener(ctx.author)
        channel = ctx.channel
        product = "pruner"
        product_category = "tool"
        if not gardener.current:
            message = "You're currently not growing a plant."
            await _send_message(channel, message)
        else:
            await self._add_health(channel, gardener, product, product_category)

    async def check_degradation(self):
        while "PlantTycoon" in self.bot.cogs:
            users = await self.config.all_users()
            for user_id in users:
                user = self.bot.get_user(user_id)
                gardener = await self._gardener(user)
                if gardener.current:
                    degradation = await self._degradation(gardener)
                    gardener.current["health"] -= degradation.degradation
                    gardener.points += self.defaults["points"]["growing"]
                    await gardener.save_gardener()
            await asyncio.sleep(self.defaults["timers"]["degradation"] * 60)

    async def check_completion(self):
        while "PlantTycoon" in self.bot.cogs:
            now = int(time.time())
            users = await self.config.all_users()
            for user_id in users:
                message = None
                user = self.bot.get_user(user_id)
                gardener = await self._gardener(user)
                if gardener.current:
                    then = gardener.current["timestamp"]
                    health = gardener.current["health"]
                    grow_time = gardener.current["time"]
                    badge = gardener.current["badge"]
                    reward = gardener.current["reward"]
                    if (now - then) > grow_time:
                        gardener.points += reward
                        if badge not in gardener.badges:
                            gardener.badges.append(badge)
                        message = (
                            "Your plant made it! "
                            "You are rewarded with the **{}** badge and you have received **{}** Thneeds.".format(
                                badge, reward
                            )
                        )
                    if health < 0:
                        message = "Your plant died!"
                if message is not None:
                    await user.send(message)
                    gardener.current = {}
                    await gardener.save_gardener()
            await asyncio.sleep(self.defaults["timers"]["completion"] * 60)

    async def send_notification(self):
        while "PlantTycoon" in self.bot.cogs:
            users = await self.config.all_users()
            for user_id in users:
                user = self.bot.get_user(user_id)
                gardener = await self._gardener(user)
                if gardener.current:
                    health = gardener.current["health"]
                    if health < self.defaults["notification"]["max_health"]:
                        message = choice(self.notifications["messages"])
                        await user.send(message)
            await asyncio.sleep(self.defaults["timers"]["notification"] * 60)

    def __unload(self):
        self.completion_task.cancel()
        self.degradation_task.cancel()
        self.notification_task.cancel()