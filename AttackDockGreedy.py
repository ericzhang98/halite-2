import hlt
import logging
import time

game = hlt.Game("attack_dock_greedy")
logging.info("Starting my dope bot!")

def closest_planet(ship):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_planet = None
    for distance in sorted(entities_by_distance):
        nearest_planet = next((nearest_entity for nearest_entity in entities_by_distance[distance] if isinstance(nearest_entity, hlt.entity.Planet)), None)
        if nearest_planet:
            break
    return nearest_planet

def closest_open_planet(ship):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_planet = None
    for distance in sorted(entities_by_distance):
        nearest_planet = next((nearest_entity for nearest_entity in
            entities_by_distance[distance] if isinstance(nearest_entity,
                hlt.entity.Planet) and not nearest_entity.is_full()), None)
        if nearest_planet:
            break
    return nearest_planet

def closest_open_neutral_planet(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_planet = None
    for distance in sorted(entities_by_distance):
        nearest_planet = next((nearest_entity for nearest_entity in
            entities_by_distance[distance] if isinstance(nearest_entity,
                hlt.entity.Planet) and not nearest_entity.is_full() and
                not nearest_entity.is_owned()), None)
        if nearest_planet:
            break
    return nearest_planet

def closest_open_nonenemy_planet(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_planet = None
    for distance in sorted(entities_by_distance):
        nearest_planet = next((nearest_entity for nearest_entity in
            entities_by_distance[distance] if isinstance(nearest_entity,
                hlt.entity.Planet) and not nearest_entity.is_full() and
                (not nearest_entity.is_owned() or nearest_entity.owner == me)), None)
        if nearest_planet:
            break
    return nearest_planet

def collide_entity(ship, entity):
    navigate_command = ship.navigate(ship.closest_point_to(entity,
        min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED))
    if ship.calculate_distance_between(entity) < entity.radius + 7:
        navigate_command = ship.navigate(ship.closest_point_to(entity,
            min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED),
            ignore_planets = True)

    return navigate_command

def attack_ship(ship, enemy_ship):
    navigate_command = ship.navigate(ship.closest_point_to(enemy_ship,
        min_distance=0), game_map, speed=int(hlt.constants.MAX_SPEED))
    return navigate_command


def attack_docked_planet(ship, planet):
    docked_ships = planet.all_docked_ships()
    target_ship = None
    closest_dist= 999999999
    for ds in docked_ships:
        dist = ship.calculate_distance_between(ds)
        if dist < closest_dist:
            target_ship = ds
            closest_dist = dist
    return attack_ship(ship, target_ship)


while True:
    game_map = game.update_map()
    start_time = time.time()
    me = game_map.get_me()
    
    command_queue = []

    ships = [ship for ship in game_map.get_me().all_ships() if ship.docking_status == ship.DockingStatus.UNDOCKED]
    all_planets = game_map.all_planets()
    unowned_planets = [planet for planet in all_planets if not planet.is_owned()]
    enemy_planets = [planet for planet in all_planets if planet.is_owned() and planet.owner != me]
    my_planets = [planet for planet in all_planets if planet.owner == me]


    for i in range(0, len(ships)):
        ship = ships[i]
        
        # go for closest nonenemy planets
        target_planet = closest_open_nonenemy_planet(ship, me)

        if target_planet:
            # dock or approach to dock
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                navigate_command = ship.navigate(ship.closest_point_to(target_planet,
                    min_distance=3), game_map, speed=int(hlt.constants.MAX_SPEED))
                if navigate_command:
                    command_queue.append(navigate_command)

        else:
            # no more nonenemy planets to fill up, go ham on enemy
            if len(enemy_planets) > 0:
                ep_radius = [p.radius for p in enemy_planets]
                ep_radius.sort()
                # will pick the center planets when equal sized
                planets_with_lowest_radius = [p for p in enemy_planets if p.radius == ep_radius[0]]
                target_planet = planets_with_lowest_radius[0]
                navigate_command = attack_docked_planet(ship, target_planet)
                if navigate_command:
                    command_queue.append(navigate_command)

        if time.time() >= start_time + 1.8:
            logging.info("1.8 s exceeded")
            break;

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
