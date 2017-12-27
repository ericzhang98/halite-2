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

def closest_free_ship(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_ship = None
    for distance in sorted(entities_by_distance):
        nearest_ship = next((nearest_entity for nearest_entity in
            entities_by_distance[distance] if isinstance(nearest_entity,
                hlt.entity.Ship) and nearest_entity.owner == me and 
                nearest_entity.docking_status == ship.DockingStatus.UNDOCKED), None)
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
    navigate_command = ship.navigate2(ship.closest_point_to(enemy_ship,
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
    docked_ships = [ship for ship in friendly_ships if ship.docking_status != ship.DockingStatus.UNDOCKED]
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
    pc = hlt.entity.Entity(game_map.width/2, game_map.height/2, 0, None, None, None)
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
    #logging.info("Planet center: %s, %s" % (pc.x, pc.y))

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

    logging.info("Time used during setup: %s" % (time.time() - start_time))

    # get rid of early game collision
    if len(my_planets) < 1 and round_counter < 30:
        for i in range(0, len(free_ships)):
            ship = free_ships[i]
            # in order of closeness for dockable planets
            for cd in closest_dockable_planet_list(ship, me):
                dist = ship.calculate_distance_between(cd)
                # only send dockable number of ships
                if dist <= planet_threshold[cd]:
                    # dock if we can
                    if ship.can_dock(cd):
                        command_queue.append(ship.dock(cd))
                        logging.info("docking")
                    # approach with the same angle as the closest ship
                    else:
                        cs = closest_ship_to_planet[cd][0][0]
                        angle = cs.calculate_angle_between(cd)
                        dist_to_surface = dist - cd.radius
                        logging.info("dist to surface: %s" % dist_to_surface)
                        # extra -1 buffer to round dist_to_surface down
                        speed = 7 if dist_to_surface >= 8 else dist_to_surface-1
                        angle_to_cs = ship.calculate_angle_between(cs) - angle
                        dx = ship.x - cs.x
                        dy = ship.y - cs.y
                        fake_target = hlt.entity.Entity(cd.x+dx, cd.y+dy, 0, None, None, None)
                        if game_map.obstacles_between(ship, fake_target, (hlt.entity.Planet)):
                            # if angle_to_cs is positive(starboard) change angle by -5(port), if negative(port) change angle by 5(starboard)
                            angle_buffer = -10 if angle_to_cs >= 0 else 10
                            angle = angle + angle_buffer
                            logging.info("will collide eventually, so changing angle by %s" % angle_buffer)
                        cmd = ship.thrust(speed, angle)
                        command_queue.append(cmd)
                    break


    # Commands for ships
    else:
        invaders = set()
        defense_target = {}
        for ds in docked_ships:
            closest_invader = closest_enemy_ship(ds, me)
            if ds.calculate_distance_between(closest_invader) < 20:
                invaders.add(closest_invader)
        for invader in invaders:
            closest_free = closest_free_ship(invader, me)
            if closest_free and invader.calculate_distance_between(closest_free) < 20:
                # will overwrite last defense target if closest_free already used, should be ok
                defense_target[closest_free.id] = invader
                logging.info("assigning %s to defend against %s" % (closest_free.id, invader.id))
        logging.info("Time used after defense check: %s" % (time.time() - start_time))
            
        for i in range(0, len(free_ships)):
            if time.time() >= start_time + 1.8:
                logging.info("1.8 s exceeded")
                break
            
            ship = free_ships[i]
            
            ce = closest_enemy_planet(ship, me)

            # first check if docked ships need defense
            if ship.id in defense_target:
                cmd = attack_ship(ship, defense_target[ship.id])
                if cmd:
                    command_queue.append(cmd)
                else:
                    logging.info("ship %s couldn't move to attack invader %s" % (ship.id, defense_target[ship.id].id))
                continue

            # if there's an enemy near, go ham
            if ce:
                closest_eds = None
                closest_dist = 999999999
                for eds in ce.all_docked_ships():
                    dist = ship.calculate_distance_between(eds)
                    if dist < closest_dist:
                        closest_eds = eds
                        closest_dist = dist

                if closest_eds and ship.calculate_distance_between(closest_eds) < 30:
                    cmd = attack_ship(ship, closest_eds)
                    if cmd:
                        command_queue.append(cmd)
                    else:
                        logging.info("ship %s couldn't move to attack planet %s docked ship %s" % (ship.id, ce.id, closest_eds.id))
                        logging.info("attempt to move to es %s at location %s" % (ce.id, (ce.x, ce.y)))
                        logging.info("angle %s dist %s" % (ship.calculate_angle_between(ce), ship.calculate_distance_between(ce)))
                    continue

            # otherwise, go for closest nonenemy planet if it exists
            #cd = closest_dockable_planet(ship, me)
            cont = False
            for cd in closest_dockable_planet_list(ship, me):
                # and the ship is nth closest or closer (n = num docking spots left) or we make investment if num free_ships > 5
                dist = ship.calculate_distance_between(cd)
                threshold = planet_threshold[cd]
                investment_threshold = closest_ship_to_planet[cd][0][1]
                if (dist <= threshold and dist <= 100) or (dist <= investment_threshold and not cd.is_owned() and len(free_ships) > 5):

                    # consider docking if we can dock
                    if ship.can_dock(cd):
                        es = closest_enemy_ship(ship, me)
                        # make sure we aren't close to an enemy ship when docking, smart dock
                        if ship.calculate_distance_between(es) > 30:
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
                        cmd = ship.navigate2(ship.closest_point_to(cd,
                            min_distance=0), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
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
