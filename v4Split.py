import hlt
import logging
import time

game = hlt.Game("ezboi")
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

def closest_dockable_planet(ship, me):
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

def closest_enemy_planet(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_planet = None
    for distance in sorted(entities_by_distance):
        nearest_planet = next((nearest_entity for nearest_entity in
            entities_by_distance[distance] if isinstance(nearest_entity,
                hlt.entity.Planet) and nearest_entity.is_owned() and nearest_entity.owner != me), None)
        if nearest_planet:
            break
    return nearest_planet

def closest_enemy_ship(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_ship = None
    for distance in sorted(entities_by_distance):
        nearest_ship = next((nearest_entity for nearest_entity in
            entities_by_distance[distance] if isinstance(nearest_entity,
                hlt.entity.Ship) and nearest_entity.owner != me), None)
        if nearest_ship:
            break
    return nearest_ship

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

def attack_closest_enemy_planet(ship, enemy_planets):
    closest_dist = 999999999
    target_planet = None
    for ep in enemy_planets:
        dist = ship.calculate_distance_between(ep)
        if dist < closest_dist:
            target_planet = ep
            closest_dist = dist
    return attack_docked_planet(ship, target_planet)

round_counter = 0
while True:
    game_map = game.update_map()
    round_counter += 1
    logging.info("Round: %s" % round_counter)
    start_time = time.time()
    me = game_map.get_me()
    
    command_queue = []

    all_ships = game_map.get_me().all_ships()
    free_ships = [ship for ship in game_map.get_me().all_ships() if ship.docking_status == ship.DockingStatus.UNDOCKED]

    all_planets = game_map.all_planets()
    unowned_planets = [planet for planet in all_planets if not planet.is_owned()]
    enemy_planets = [planet for planet in all_planets if planet.is_owned() and planet.owner != me]
    my_planets = [planet for planet in all_planets if planet.owner == me]
    nonenemy_planets = unowned_planets + my_planets
    dockable_planets = [planet for planet in nonenemy_planets if not planet.is_full()]

    closest_ship_to_planet = {}
    planet_threshold = {}
    for p in all_planets:
        ship_dists = []
        for s in free_ships:
            ship_dists.append((s, s.calculate_distance_between(p)))
        ship_dists.sort(key = lambda tup: tup[1])
        closest_ship_to_planet[p] = ship_dists

        EXTRA = 0
        planet_threshold[p] = 999999999
        if len(ship_dists) > 0:
            num_free_spots = p.num_docking_spots - len(p.all_docked_ships())
            threshold_index = num_free_spots-1+EXTRA if num_free_spots-1+EXTRA < len(ship_dists) else len(ship_dists)-1
            planet_threshold[p] = ship_dists[threshold_index][1] #genius

    # todo get rid of early game collision
    # todo: assign a certain amt (spots + 1) of (closest) ships to each dockable planet, rest of ship do other stuff
    for i in range(0, len(free_ships)):
        if time.time() >= start_time + 1.8:
            logging.info("1.8 s exceeded")
            break;
        
        ship = free_ships[i]
        
        cd = closest_dockable_planet(ship, me)
        ce = closest_enemy_planet(ship, me)

        # if there's an enemy near, go ham
        if ce and ship.calculate_distance_between(ce) < 30:
            cmd = attack_docked_planet(ship, ce)
            if cmd:
                command_queue.append(cmd)
            else:
                logging.info("ship %s couldn't move to attack planet %s" % (ship.id, ce.id))
            continue

        # otherwise, go for closest nonenemy planet if it exists
        if cd:
            # and the ship is nth closest or closer (n = num docking spots left + 1)
            dist = ship.calculate_distance_between(cd)
            threshold = planet_threshold[cd]
            if dist < 100 and dist <= threshold:

                # consider docking if we can dock
                if ship.can_dock(cd):
                    command_queue.append(ship.dock(cd))

                # go towards a position where we can dock
                else:
                    cmd = ship.navigate(ship.closest_point_to(cd,
                        min_distance=3), game_map, speed=int(hlt.constants.MAX_SPEED))
                    if cmd:
                        command_queue.append(cmd)
                    else:
                        logging.info("ship %s couldn't move to planet %s" % (ship.id, cd.id))

                continue

        # no more nonenemy planets to fill up, go ham on enemy
        # todo: go for planet closest to center
        if len(enemy_planets) > 0:
            ep_radius = [p.radius for p in enemy_planets]
            ep_radius.sort()
            # will pick the center planets when equal sized
            planets_with_lowest_radius = [p for p in enemy_planets if p.radius == ep_radius[0]]
            target_planet = planets_with_lowest_radius[0]
            cmd = attack_docked_planet(ship, target_planet)
            if cmd:
                command_queue.append(cmd)
            else:
                logging.info("ship %s couldn't move to attack planet %s" % (ship.id, target_planet.id))
            continue


    game.send_command_queue(command_queue)
    time_used = time.time() - start_time
    logging.info("Time used: %f" % time_used)
    # TURN END
# GAME END


#rushing
"""
    if len(enemy_planets) > 0 and len(all_ships) > 4 and len(all_ships) < 10:
        # should be closest to an enemy planet
        rusher = free_ships[0]

        cmd = attack_closest_enemy_planet(rusher, enemy_planets)
        if cmd:
            free_ships.pop(0)
            command_queue.append(cmd)
        else:
            logging.info("can't move for rushing")
"""
