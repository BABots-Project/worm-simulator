import mesa
from player import SolitaryWorm, SocialWorm, Food, SPSocialWorm, SPSolitaryWorm
from environment import WormEnvironment
import math
from typing import Tuple

class WormSimulator(mesa.Model):
    def __init__(self, n_agents: int, n_food: int, clustering: float, dim_grid: int, social: bool,
                  multispot: bool, num_spots: int, clustered: bool, strain_specific: bool):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = WormEnvironment(dim_grid, torus=True)

        if clustered:
            self.clustered_agents(n_agents, social, strain_specific, multispot, num_spots)
        else:
            grid_coords = [pos for _, pos in self.grid.coord_iter()]
            positions = self.random.sample(grid_coords, n_agents)
            for i in range(n_agents):
                a = WormSimulator.create_agent(self, social, strain_specific, i, positions[i])
                self.schedule.add(a)
                self.grid.place_agent(a, a.pos)

        total_food = n_food
        if multispot:
            self.multispot_food(total_food, num_spots)
        else:
            gamma = clustering
            self.smoothly_varying_food(total_food, gamma)

        self.datacollector = mesa.DataCollector(model_reporters={"Food": self.grid.get_total_food},
                                                agent_reporters={"ConsumedFood": lambda agent: agent.consumed_food,
                                                                 "ForagingEfficiency": lambda agent: round(agent.consumed_food/(agent.model.schedule.steps + 1),2)})
        self.datacollector.collect(self)

    def step(self) -> None:
        self.datacollector.collect(self)
        self.schedule.step()
        self.datacollector.collect(self)

    def smoothly_varying_food(self, total_food: int, gamma: float = 0) -> None:
        """Implements the smoothly varying inhomogeneous food distribution from the paper"""
        if gamma > 0:
            foods = []
            coords = (self.random.randrange(0, self.grid.dim_grid), self.random.randrange(0, self.grid.dim_grid))
            f = Food(f'food_{0}', self, coords)
            self.grid.place_food(coords, f)
            foods.append(f)
            for i in range(1, total_food):
                d = self.random.uniform(0, 1) ** (-1 / gamma)
                if d > (self.grid.dim_grid / math.sqrt(2)):
                    d = self.random.uniform(1, self.grid.dim_grid / math.sqrt(2))
                starting_pos = self.random.choice(foods).pos
                angle = self.random.uniform(0, 2 * math.pi)
                x = (starting_pos[0] + int(d * math.cos(angle))) % self.grid.dim_grid
                y = (starting_pos[1] + int(d * math.sin(angle))) % self.grid.dim_grid
                coords = (x, y)
                f = Food(f'food_{i}', self, coords)
                self.grid.place_food(coords, f)
                foods.append(f)
        elif gamma == 0:
            for i in range(total_food):
                coords = (self.random.randrange(0, self.grid.dim_grid), self.random.randrange(0, self.grid.dim_grid))
                f = Food(f'food_{i}', self, coords)
                self.grid.place_food(coords, f)

    def multispot_food(self, total_food: int, num_spots: int) -> None:
        """Implements the multispot food distribution from the paper"""
        if num_spots == 1:
            dx = self.grid.dim_grid / 2
            dy = self.grid.dim_grid / 2
            spot_pos = [(round(dx), round(dy))]
            radius = round(self.grid.dim_grid / 6)
        if num_spots == 2:
            dx = self.grid.dim_grid / 4
            dy = self.grid.dim_grid / 4
            spot_pos = [(round(dx), round(dy)), (round(3*dx), round(3*dy))]
            radius = round(self.grid.dim_grid / 8)
        if num_spots == 4:
            dx = self.grid.dim_grid / 4
            dy = self.grid.dim_grid / 4
            spot_pos = [(round(dx), round(dy)), (round(3*dx), round(dy)), (round(dx), round(3*dy)), (round(3*dx), round(3*dy))]
            radius = round(self.grid.dim_grid / 12)

        for i in range(num_spots):
            neighborhood = self.grid.get_neighborhood(spot_pos[i], True, True, radius)
            food_per_cell = total_food // num_spots // len(neighborhood)
            for cell in neighborhood:
                f = Food(f'food_{i}', self, cell, quantity=food_per_cell)
                self.grid.place_food(cell, f)

    def clustered_agents(self, num_agents: int, social: bool, strain_specific: bool = False,
                          multispot: bool = False, num_spots: int = 1) -> None:
        """Implements the clustered initial positions for the worms"""
        radius = math.ceil(math.sqrt(num_agents) / 2)
        if multispot:
            if num_spots == 1 or num_spots == 2:
                cluster_position = (self.grid.dim_grid - radius - 1, radius)
            else:
                cluster_position = (self.grid.dim_grid // 2, self.grid.dim_grid // 2)
        else:
            cluster_position = (self.random.randrange(0, self.grid.dim_grid), self.random.randrange(0, self.grid.dim_grid))
        neighborhood = self.grid.get_neighborhood(cluster_position, True, True, radius)
        positions = self.random.sample(neighborhood, num_agents)
        for i in range(num_agents):
            a = WormSimulator.create_agent(self, social, strain_specific, i, positions[i])
            self.schedule.add(a)
            self.grid.place_agent(a, a.pos)

    @staticmethod
    def create_agent(model: mesa.Model, social: bool, strain_specific: bool, n: int, pos: Tuple[int]) -> mesa.Agent:
        agent = None
        if strain_specific:
            if social:
                agent = SPSocialWorm(n, model, pos)
            else:
                agent = SPSolitaryWorm(n, model, pos)
        else:
            if social:
                agent = SocialWorm(n, model, pos)
            else:
                agent = SolitaryWorm(n, model, pos)
        return agent