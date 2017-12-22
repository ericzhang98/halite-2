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

"""
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
"""

def closest_dockable_planet(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and not entity.is_full() and (not entity.is_owned() or entity.owner == me):
                return entity

def closest_dockable_planet_list(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_planet_list = []
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and not entity.is_full() and (not entity.is_owned() or entity.owner == me):
                nearest_planet_list.append(entity)
    return nearest_planet_list

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
        min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    if ship.calculate_distance_between(entity) < entity.radius + 7:
        navigate_command = ship.navigate(ship.closest_point_to(entity,
            min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED),
            ignore_planets = True, angular_step=1)

    return navigate_command

def attack_ship(ship, enemy_ship):
    navigate_command = ship.navigate(ship.closest_point_to(enemy_ship,
        min_distance=0), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
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

    # ship and planet lists
    friendly_ships = game_map.get_me().all_ships() # Don't use friendly_ships since it includes docked ships
    free_ships = [ship for ship in friendly_ships if ship.docking_status == ship.DockingStatus.UNDOCKED]
    enemy_ships = [ship for ship in game_map._all_ships() if ship.owner != me]
    all_planets = game_map.all_planets()
    unowned_planets = [planet for planet in all_planets if not planet.is_owned()]
    enemy_planets = [planet for planet in all_planets if planet.is_owned() and planet.owner != me]
    my_planets = [planet for planet in all_planets if planet.owner == me]
    nonenemy_planets = unowned_planets + my_planets
    dockable_planets = [planet for planet in nonenemy_planets if not planet.is_full()]

    # build closest ship lists and engage distance thresholds for all planets
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

    # find weighted planet center
    pc = hlt.entity.Entity(game_map.width, game_map.height, 0, None, None, None)
    total_x = 0
    total_y = 0
    num_docked = 0
    for p in my_planets:
        p_num = len(p.all_docked_ships())
        p_location = (p.x, p.y)
        num_docked += p_num
        total_x += p_num*p_location[0]
        total_y += p_num*p_location[1]
    if num_docked > 0:
        pc.x = total_x/num_docked
        pc.y = total_y/num_docked
    logging.info("Planet center: %s, %s" % (pc.x, pc.y))

    # build priority level for attacking enemy planets based on planet center
    ep_priority = []
    ep_attack = None
    if len(enemy_planets) > 0:
        for ep in enemy_planets:
            dist = pc.calculate_distance_between(ep)
            ep_priority.append((ep, dist))
        ep_priority.sort(key = lambda tup: tup[1])
        ep_attack = ep_priority[0][0]
        logging.info("Priority ep: %s with dist %s" % (ep_attack.id, ep_priority[0][1]))
    else:
        logging.info("No enemy planets")

    # jank but gets rid of early game collision
    if len(friendly_ships) <= 3 and round_counter < 3:
        for i in range(0, len(free_ships)):
            ship = free_ships[i]
            # in order of closeness for dockable planets
            for cd in closest_dockable_planet_list(ship, me):
                dist = ship.calculate_distance_between(cd)
                # only send dockable number of ships
                if dist <= planet_threshold[cd]:
                    if ship.can_dock(cd):
                        command_queue.append(ship.dock(cd))
                        logging.info("docking")
                    elif closest_ship_to_planet[cd][0][0] == ship:
                        point = ship.closest_point_to(cd, min_distance=0)
                        cmd = ship.navigate(point, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
                        command_queue.append(cmd)
                    elif closest_ship_to_planet[cd][1][0] == ship:
                        point = ship.closest_point_to(cd, min_distance=0)
                        cmd = ship.navigate(point, game_map, speed=int(hlt.constants.MAX_SPEED-1), angular_step=1)
                        command_queue.append(cmd)
                    else:
                        point = ship.closest_point_to(cd, min_distance=0)
                        cmd = ship.navigate(point, game_map, speed=int(hlt.constants.MAX_SPEED-2), angular_step=1)
                        command_queue.append(cmd)
                    break


    # Commands for ships
    else:
        for i in range(0, len(free_ships)):
            if time.time() >= start_time + 1.8:
                logging.info("1.8 s exceeded")
                break;
            
            ship = free_ships[i]
            
            ce = closest_enemy_planet(ship, me)

            # if there's an enemy near, go ham
            if ce and ship.calculate_distance_between(ce) < 30:
                cmd = attack_docked_planet(ship, ce)
                if cmd:
                    command_queue.append(cmd)
                else:
                    logging.info("ship %s couldn't move to attack planet %s" % (ship.id, ce.id))
                    logging.info("attempt to move to es %s at location %s" % (ce.id, (ce.x, ce.y)))
                    logging.info("angle %s dist %s" % (ship.calculate_angle_between(ce), ship.calculate_distance_between(ce)))
                continue

            # otherwise, go for closest nonenemy planet if it exists
            #cd = closest_dockable_planet(ship, me)
            cont = False
            for cd in closest_dockable_planet_list(ship, me):
                # and the ship is nth closest or closer (n = num docking spots left)
                dist = ship.calculate_distance_between(cd)
                threshold = planet_threshold[cd]
                if dist < 100 and dist <= threshold:

                    # consider docking if we can dock
                    if ship.can_dock(cd):
                        es = closest_enemy_ship(ship, me)
                        # make sure we aren't close to an enemy ship when docking
                        if ship.calculate_distance_between(es) > 15:
                            command_queue.append(ship.dock(cd))
                            logging.info("docking")
                        # if an enemy ship is close, docking isn't safe, so go ham
                        else:
                            cmd = attack_ship(ship, es)
                            if cmd:
                                command_queue.append(cmd)
                            else:
                                logging.info("ship %s couldn't move to attack ship %s" % (ship.id, es.id))

                    # go towards a position where we can dock
                    else:
                        cmd = ship.navigate(ship.closest_point_to(cd,
                            min_distance=3.5), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
                        if cmd:
                            command_queue.append(cmd)
                        else:
                            logging.info("ship %s couldn't move to planet %s" % (ship.id, cd.id))
                    cont = True
                    break
            if cont:
                continue

            # no close nonenemy planets to fill up, go ham on enemy
            # go for planet closest to center of my planets
            if len(enemy_planets) > 0:
                target_planet = ep_attack
                cmd = attack_docked_planet(ship, target_planet)
                if cmd:
                    command_queue.append(cmd)
                else:
                    logging.info("ship %s couldn't move to attack planet %s" % (ship.id, target_planet.id))
                continue

            # no more enemy planets (lol) so might as well go for enemy ships
            closest_es = None
            closest_dist = 999999999
            for es in enemy_ships:
                dist = ship.calculate_distance_between(es)
                if dist < closest_dist:
                    closest_es = es
                    closest_dist = dist
            if closest_es:
                cmd = attack_ship(ship, closest_es)
                if cmd:
                    command_queue.append(cmd)
                else:
                    logging.info("ship %s couldn't move to attack closest ship %s" % (ship.id, closest_es.id))
            else:
                logging.info("weird... couln't find closest_es when no enemy planets")


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
