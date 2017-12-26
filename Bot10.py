import hlt
import logging
import time
import math

game = hlt.Game("ezboi")
logging.info("Starting my dope bot!")

def closest_planet(ship):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet):
                return entity
    return None

def closest_dockable_planet(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and not entity.is_full() and (not entity.is_owned() or entity.owner == me):
                return entity
    return None

def closest_dockable_planet_list(ship, me):
    nearest_planet_list = []
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and not entity.is_full() and (not entity.is_owned() or entity.owner == me):
                nearest_planet_list.append(entity)
    return nearest_planet_list

def closest_enemy_planet(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and entity.is_owned() and entity.owner != me:
                return entity
    return None

def closest_enemy_ship(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and entity.owner != me:
                return entity
    return None

def closest_enemy_free_ship(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and entity.owner != me and entity.docking_status == ship.DockingStatus.UNDOCKED:
                return entity
    return None

def closest_enemy_ships_dist(ship, me, dist=100, sort=False):
    enemy_ships_dist = []
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner != me:
                    enemy_ships_dist.append((entity, distance))
    if sort:
        enemy_ships_dist.sort(key = lambda tup: tup[1])
    return enemy_ships_dist

def closest_friendly_ships_dist(ship, me, dist=100, sort=False):
    friendly_ships_dist = []
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner == me:
                    friendly_ships_dist.append((entity, distance))
    if sort:
        friendly_ships_dist.sort(key = lambda tup: tup[1])
    return friendly_ships_dist

def closest_free_ship(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and entity.owner == me and entity.docking_status == ship.DockingStatus.UNDOCKED:
                return entity
    return None

def collide_entity(ship, entity):
    navigate_command = ship.navigate(ship.closest_point_to(entity,
        min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    if ship.calculate_distance_between(entity) < entity.radius + 7:
        navigate_command = ship.navigate(ship.closest_point_to(entity,
            min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED),
            ignore_planets = True, angular_step=1)
    return navigate_command

def attack_ship(ship, enemy_ship, nav=2):
    navigate_command = ship.navigate2(ship.closest_point_to(enemy_ship,
        min_distance=0), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    if nav == 360:
        navigate_command = ship.navigate360(ship.closest_point_to(enemy_ship,
        min_distance=0), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return navigate_command

def attack_docked_planet(ship, planet, nav=2):
    docked_ships = planet.all_docked_ships()
    target_ship = None
    closest_dist= 999999999
    for ds in docked_ships:
        dist = ship.calculate_distance_between(ds)
        if dist < closest_dist:
            target_ship = ds
            closest_dist = dist
    return attack_ship(ship, target_ship, nav)

def lines_interesect(line1, line2):
    startx_1, starty_1, endx_1, endy_1 = line1[0], line1[1], line1[2], line1[3]
    startx_2, starty_2, endx_2, endy_2 = line2[0], line2[1], line2[2], line2[3]
    slope_1 = (endy_1 - starty_1)/(endx_1 - startx_1)
    b_1 = starty_1 - slope_1*startx_1
    slope_2 = (endy_2 - starty_2)/(endx_2 - startx_2)
    b_2 = starty_2 - slope_2*startx_2
    if abs(slope_1 - slope_2) < 0.1:
        if abs(b_1 - b_2) < 0.5:
            if ((startx_1 > startx_2 and startx_1 < endx_2) or (startx_1 < startx_2 and startx_1 > endx_2) or
                    (endx_1 > startx_2 and endx_1 < endx_2) or (endx_1 < startx_2 and endx_1 > endx_2)):
                return True
            else:
                return False
    else:
        x_intersection = (b_2-b_1)/(slope_1-slope_2)
        if (x_intersection > startx_1 and x_intersection < endx_1) or (x_intersection < startx_1 and x_intersection > endx_1):
            return True
        else:
            return False

def trajectories_intersect(line1, line2):
    startx_1, starty_1, endx_1, endy_1 = line1[0], line1[1], line1[2], line1[3]
    startx_2, starty_2, endx_2, endy_2 = line2[0], line2[1], line2[2], line2[3]
    return True


def move_ship(ship, x, y, trajectories):
    dist = sqrt((x-ship.x)**2 + (y-ship.y)**2)
    speed = int(min(dist, 7))
    angle = math.degrees(math.atan2(y - ship.y, x - ship.x)) % 360
    # set new target if old (x, y) has dist longer than 7
    if (dist > 7):
        x = ship.x + 7*math.cos(math.radians(angle))
        y = ship.y + 7*math.sin(math.radians(angle))
    ship_tra = (ship.x, ship.y, x, y)
    for tra in trajectories:
        if lines_intersect((ship.x, ship.y, x, y), tra):
            return None
    return ship.thrust(speed, angle)



def smart_nav(ship, target, game_map, speed, avoid_obstacles=True, max_corrections=90, angular_step=1,
    ignore_ships=False, ignore_planets=False):
    if max_corrections <= 0:
        return None
    distance = self.calculate_distance_between(target)
    angle = self.calculate_angle_between(target)
    ignore = () if not (ignore_ships or ignore_planets) \
            else Ship if (ignore_ships and not ignore_planets) \
            else Planet if (ignore_planets and not ignore_ships) \
            else Entity
    if avoid_obstacles and game_map.obstacles_between(self, target, ignore):
        new_target_dx = math.cos(math.radians(angle + angular_step)) * distance
        new_target_dy = math.sin(math.radians(angle + angular_step)) * distance
        new_target = Position(self.x + new_target_dx, self.y + new_target_dy)
        return self.navigate(new_target, game_map, speed, True, max_corrections - 1, angular_step)
    speed = speed if (distance >= speed) else distance
    return self.thrust(speed, angle)

def register_command(ship, cmd):
    if cmd:
        split = cmd.split()
        action = split[0]
        if action == "d":
            trajetories[ship.id] = (ship.x, ship.y, ship.x, ship.y)
        elif action == "t":
            speed = split[2]
            angle = split[3]
            trajectories[ship.id] = (ship.x, ship.y, ship.x+float(speed)*math.cos(math.radians(float(angle))), 
                    ship.y+float(speed)*math.sin(math.radians(float(angle))))

trajectories = {}
command_queue = []

round_counter = 0
while True:
    game_map = game.update_map()
    round_counter += 1
    logging.info("Round: %s" % round_counter)
    start_time = time.time()
    me = game_map.get_me()
    two_player = len(game_map.all_players()) == 2
    map_width = game_map.width
    map_height = game_map.height
    
    trajectories = {}
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
    for ds in docked_ships:
        trajectories[ds.id] = (ds.x, ds.y, ds.x, ds.y)

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
                        register_command(ship, cmd)
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
                        register_command(ship, cmd)
                    break


    # Commands for ships
    else:
        # calculate list of invaders
        invaders = set()
        defense_target = {}
        for ds in docked_ships:
            closest_invader = closest_enemy_free_ship(ds, me)
            if closest_invader and ds.calculate_distance_between(closest_invader) < 40:
                invaders.add(closest_invader)
        for invader in invaders:
            closest_free = closest_free_ship(invader, me)
            if closest_free and invader.calculate_distance_between(closest_free) < 40:
                # will overwrite last defense target if closest_free already used, should be ok
                defense_target[closest_free.id] = invader
                logging.info("assigning %s to defend against %s" % (closest_free.id, invader.id))
        logging.info("Time used after defense check: %s" % (time.time() - start_time))

        # calculate squads
        squad = {}

            
        for i in range(0, len(free_ships)):
            if time.time() >= start_time + 1.6:
                logging.info("1.6 s exceeded")
                break
            
            ship = free_ships[i]
            ce = closest_enemy_planet(ship, me)

            # 1. check if docked ships need defense
            if ship.id in defense_target:
                cmd = attack_ship(ship, defense_target[ship.id])
                if cmd:
                    command_queue.append(cmd)
                    register_command(ship, cmd)
                else:
                    logging.info("ship %s couldn't move to attack invader %s" % (ship.id, defense_target[ship.id].id))
                continue

            # assess threat level
            threat_score = 0
            closest_es_dist = closest_enemy_ships_dist(ship, me)
            has_undocked = False
            for es_dist in closest_es_dist:
                es_score = 100 - es_dist[1]
                # 1/4 the threat level of docked ships
                if es_dist[0].docking_status != ship.DockingStatus.UNDOCKED:
                    es_score = float(es_score)/4
                else:
                    has_undocked = True
                threat_score  += es_score
            # no undocked ships means no threat, might as well try to kill a docked ship
            if not has_undocked:
                threat_score = 0
            logging.info("%s has threat score: %s" % (ship.id, threat_score))

            # assess strength level
            strength_score = 0 # avoid 1 v 1
            closest_fs_dist = closest_friendly_ships_dist(ship, me)
            closest_fs = None
            closest_dist = 999999999
            for fs_dist in closest_fs_dist:
                fs_score = 100 - fs_dist[1]
                # 1/4 the threat level of docked ships
                if fs_dist[0].docking_status != ship.DockingStatus.UNDOCKED:
                    fs_score = float(fs_score)/4
                if fs_dist[1] < closest_dist:
                    closest_dist = fs_dist[1]
                    closest_fs = fs_dist[0]
                strength_score  += fs_score
            logging.info("%s has strength score: %s" % (ship.id, strength_score))
            
            if threat_score > strength_score:
                logging.info("threat level too high, attempt to flock")
                # add dist cap on closest_fs
                if closest_fs and closest_dist < 40:
                    cmd = ship.navigate2(ship.closest_point_to(closest_fs, min_distance=0.5), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
                    if cmd:
                        command_queue.append(cmd)
                        register_command(ship, cmd)
                    else:
                        logging.info("ship %s couldn't move towards ship %s" % (ship.id, closest_fs.id))
                else:
                    logging.info("JUKE CITY")
                continue

            # 2. if there's an enemy near, go ham
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
                        register_command(ship, cmd)
                    else:
                        logging.info("ship %s couldn't move to attack planet %s docked ship %s" % (ship.id, ce.id, closest_eds.id))
                        logging.info("attempt to move to es %s at location %s" % (ce.id, (ce.x, ce.y)))
                        logging.info("angle %s dist %s" % (ship.calculate_angle_between(ce), ship.calculate_distance_between(ce)))
                    continue

            # 3. otherwise, go for closest nonenemy planet if it exists (in order of closeness)
            cont = False
            for cd in closest_dockable_planet_list(ship, me):
                # only go if ship is nth closest or closer (n = num docking spots left) or we make single ship investment if num free_ships > 5
                dist = ship.calculate_distance_between(cd)
                threshold = planet_threshold[cd]
                investment_threshold = closest_ship_to_planet[cd][0][1]
                if (dist <= threshold and dist <= 100) or (dist <= investment_threshold and not cd.is_owned() and len(free_ships) > 5):

                    # consider docking if we can dock
                    if ship.can_dock(cd):
                        es = closest_enemy_free_ship(ship, me)
                        # make sure we aren't close to an enemy ship when docking, smart dock
                        if es == None or ship.calculate_distance_between(es) > 30:
                            command_queue.append(ship.dock(cd))
                            register_command(ship, cmd)
                            logging.info("docking")
                        # if an enemy ship is close, docking isn't safe, so go ham
                        else:
                            cmd = attack_ship(ship, es)
                            if cmd:
                                command_queue.append(cmd)
                                register_command(ship, cmd)
                            else:
                                logging.info("ship %s couldn't move to attack ship %s" % (ship.id, es.id))

                    # go towards a position where we can dock
                    else:
                        cmd = ship.navigate2(ship.closest_point_to(cd, min_distance=0), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
                        if cmd:
                            command_queue.append(cmd)
                            register_command(ship, cmd)
                        else:
                            logging.info("ship %s couldn't move to planet %s" % (ship.id, cd.id))
                    cont = True
                    break
            if cont:
                continue

            # 4. no close nonenemy planets to fill up, go ham on enemy
            # go for planet closest to center of my planets
            if len(enemy_planets) > 0:
                target_planet = ep_attack
                cmd = attack_docked_planet(ship, target_planet)
                if cmd:
                    command_queue.append(cmd)
                    register_command(ship, cmd)
                else:
                    logging.info("ship %s couldn't move to attack planet %s" % (ship.id, target_planet.id))
                continue

            # 5. no more enemy planets (lol) so might as well go for enemy ships, already won at this point
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
                    register_command(ship, cmd)
                else:
                    logging.info("ship %s couldn't move to attack closest ship %s" % (ship.id, closest_es.id))
            else:
                logging.info("weird... couln't find closest_es when no enemy planets")

    game.send_command_queue(command_queue)
    time_used = time.time() - start_time
    logging.info("Time used: %f" % time_used)
    for key in trajectories:
        logging.info("%s -- %s" % (key, trajectories[key]))
    # TURN END
# GAME END
