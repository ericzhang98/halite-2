import hlt
import logging
import time
import math

game = hlt.Game("ezboi")
logging.info("Starting my dope bot!")

# -------------- Cache ----------------- #

def get_nearby_entities(ship):
    if ship.id in nearby_entities_cache:
        return nearby_entities_cache[ship]
    else:
        nearby_entities_cache[ship] = game_map.nearby_entities_by_distance(ship)
        return nearby_entities_cache[ship]

def get_entity_dist(ship):
    if ship.id in entities_dist_cache:
        return entities_dist_cache[ship]
    else:
        nearby_entities = get_nearby_entities(ship)
        entity_dist = {}
        for distance in nearby_entities:
            for entity in nearby_entities[distance]:
                entity_dist[entity] = distance
        entities_dist_cache[ship] = entity_dist
        return entities_dist_cache[ship]

def closest(ship, entities):
    return closest_list(ship, entities)[0]

def closest_dist(ship, entities):
    entity_dist_tuples = []
    entity_dist = get_entity_dist(ship)
    for e in entities:
        entity_dist_tuples.append(entity, (entity_dist[ship])-entity.radius)
    entity_dist_tuples.sort(key = lambda tup: tup[1])
    return entity_dist_tuples

def closest_list(ship, entities):
    entity_dist_tuples = closest_dist(ship, entities)
    return [tup[0] for tup in entity_dist_tuples]

# returns list of ships within dist and planet with surfaces within dist, extra fudge of 0.6
def entities_within_distance(ship, dist):
    entities = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and ship.calculate_distance_between(entity) < dist+0.6:
                entities.append(entity)
            if isinstance(entity, hlt.entity.Planet) and ship.calculate_distance_between(entity) < dist+entity.radius+0.6:
                entities.append(entity)
    return entities


# -------------- Closest Planets ----------------- #

def closest_dockable_side_planet(ship, me):
    cd_list = closest_dockable_side_planet_list(ship, me)
    return cd_list[0]

def closest_dockable_side_planet_list(ship, me):
    map_center = hlt.entity.Position(map_width/2, map_height/2)
    planet_dist_tuples = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and not entity.is_full() and (not entity.is_owned() or entity.owner == me):
                planet_dist_tuples.append((entity, distance-entity.radius))
    planet_dist_tuples.sort(key = lambda tup: tup[1])
    nearest_planet_list = [tup[0] for tup in planet_dist_tuples]
    return nearest_planet_list

def closest_dockable_planet(ship, me):
    cd_list = closest_dockable_planet_list(ship, me)
    return cd_list[0]

def closest_dockable_planet_list(ship, me):
    planet_dist_tuples = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and not entity.is_full() and (not entity.is_owned() or entity.owner == me):
                planet_dist_tuples.append((entity, distance-entity.radius))
    planet_dist_tuples.sort(key = lambda tup: tup[1])
    nearest_planet_list = [tup[0] for tup in planet_dist_tuples]
    return nearest_planet_list

def closest_dockable_center_planet_list(ship, me):
    cd_list = closest_dockable_planet_list(ship, me)
    cd_center_list = [cd for cd in cd_list if cd.id < 4]
    return cd_center_list

def closest_enemy_planet(ship, me):
    planet_dist_tuples = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and entity.is_owned() and entity.owner != me:
                planet_dist_tuples.append((entity, distance-entity.radius))
    planet_dist_tuples.sort(key = lambda tup: tup[1])
    nearest_planet_list = [tup[0] for tup in planet_dist_tuples]
    return nearest_planet_list[0] if len(nearest_planet_list) > 0 else None


# -------------- Closest Ships ----------------- #

def closest_enemy_ship(ship, me):
    entities_by_distance = get_nearby_entities(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and entity.owner != me:
                return entity
    return None

def closest_enemy_free_ship(ship, me):
    entities_by_distance = get_nearby_entities(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and entity.owner != me and entity.docking_status == hlt.entity.Ship.DockingStatus.UNDOCKED:
                return entity
    return None



def closest_enemy_ships_dist(ship, me, dist=100, sort=False):
    enemy_ships_dist = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner != me:
                    enemy_ships_dist.append((entity, distance))
    if sort:
        enemy_ships_dist.sort(key = lambda tup: tup[1])
    return enemy_ships_dist

def closest_enemy_free_ships_dist(ship, me, dist=100, sort=False):
    enemy_ships_dist = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner != me and entity.docking_status == hlt.entity.Ship.DockingStatus.UNDOCKED:
                    enemy_ships_dist.append((entity, distance))
    if sort:
        enemy_ships_dist.sort(key = lambda tup: tup[1])
    return enemy_ships_dist

def closest_enemy_docked_ships_dist(ship, me, dist=100, sort=False):
    enemy_ships_dist = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner != me and entity.docking_status != hlt.entity.Ship.DockingStatus.UNDOCKED:
                    enemy_ships_dist.append((entity, distance))
    if sort:
        enemy_ships_dist.sort(key = lambda tup: tup[1])
    return enemy_ships_dist

def closest_friendly_ships_dist(ship, me, dist=100, sort=False):
    friendly_ships_dist = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner == me:
                    friendly_ships_dist.append((entity, distance))
    if sort:
        friendly_ships_dist.sort(key = lambda tup: tup[1])
    return friendly_ships_dist

def closest_free_ships_dist(ship, me, dist=100, sort=False):
    free_ships_dist = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner == me and entity.docking_status == hlt.entity.Ship.DockingStatus.UNDOCKED:
                    free_ships_dist.append((entity, distance))
    if sort:
        free_ships_dist.sort(key = lambda tup: tup[1])
    return free_ships_dist

def closest_docked_ships_dist(ship, me, dist=100, sort=False):
    free_ships_dist = []
    entities_by_distance = get_nearby_entities(ship)
    for distance in entities_by_distance:
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner == me and entity.docking_status != hlt.entity.Ship.DockingStatus.UNDOCKED:
                    free_ships_dist.append((entity, distance))
    if sort:
        free_ships_dist.sort(key = lambda tup: tup[1])
    return free_ships_dist


# -------------- Geometry ----------------- #

def avg_pos(entities):
    if len(entities) == 0:
        return hlt.entity.Position(map_width/2, map_height/2)
    e_x = 0
    e_y = 0
    for e in entities:
        e_x += e.x
        e_y += e.y
    e_x = e_x/len(entities)
    e_y = e_y/len(entities)
    return hlt.entity.Position(e_x, e_y)

def trajectories_intersect_t(line1, trajectories):
    max_t = 100 # could do high_accuracy setting and change back down to 30
    startx_1, starty_1, endx_1, endy_1 = line1[0], line1[1], line1[2], line1[3]
    dx_1 = endx_1 - startx_1
    dy_1 = endy_1 - starty_1
    # cache the ship line
    discrete_line1 = [0 for i in range(max_t+1)]
    for t in range(max_t+1):
        t_factor = float(t)/max_t
        tx_1 = startx_1 + t_factor*dx_1
        ty_1 = starty_1 + t_factor*dy_1
        discrete_line1[t] = (tx_1, ty_1)
    # for each t in [0, max_t+1], evaluate each trajectory
    for t in range(max_t+1):
        t_factor = float(t)/max_t
        for tra in trajectories:
            startx_2 = tra[0]
            starty_2 = tra[1]
            dx_2 = tra[2]-tra[0]
            dy_2 = tra[3]-tra[1]
            tx_2 = startx_2 + t_factor*dx_2
            ty_2 = starty_2 + t_factor*dy_2
            tx_1 = discrete_line1[t][0]
            ty_1 = discrete_line1[t][1]
            # could change distance setting for high_accuracy as well (to like 1.1)
            if (tx_2-tx_1)**2 + (ty_2-ty_1)**2 <= 1.01:
                return True
    return False

def trajectories_intersect_l(line1, trajectories):
    max_t = 100 # could do high_accuracy setting and change back down to 30
    startx_1, starty_1, endx_1, endy_1 = line1[0], line1[1], line1[2], line1[3]
    dx_1 = endx_1 - startx_1
    dy_1 = endy_1 - starty_1
    # cache the ship line
    discrete_line1 = [0 for i in range(max_t+1)]
    for t in range(max_t+1):
        t_factor = float(t)/max_t
        tx_1 = startx_1 + t_factor*dx_1
        ty_1 = starty_1 + t_factor*dy_1
        discrete_line1[t] = (tx_1, ty_1)
    # for each trajectory, evaluate each t in [0, max_t+1]
    for tra in trajectories:
        startx_2 = tra[0]
        starty_2 = tra[1]
        dx_2 = tra[2]-tra[0]
        dy_2 = tra[3]-tra[1]
        for t in range(max_t+1):
            t_factor = float(t)/max_t
            tx_2 = startx_2 + t_factor*dx_2
            ty_2 = starty_2 + t_factor*dy_2
            tx_1 = discrete_line1[t][0]
            ty_1 = discrete_line1[t][1]
            # could change distance setting for high_accuracy as well (to like 1.1)
            if (tx_2-tx_1)**2 + (ty_2-ty_1)**2 <= 1.01:
                return True
    return False

# which is better: a for loop across time or across lines?
# across time is better when: % along the line where intersection occurs < % lines intersect
# across lines is better when: % lines intersect < % along the line where intersection occurs
# main scenario I want to save time in is when there's a fuckton of ships
# if there's a fuckton of ships, then they're likely hella clumped together
# which means trajectories will probably intersect earlier along the line?
# percentage of lines intersecting might not actually change that much


# -------------- Movement ----------------- #

# returns thrust cmd if there aren't any intersecting trajectories, otherwise returns None
# takes in any angle (in degrees), but will calculate with discrete angle
def move_ship(ship, dist, angle, trajectories):
    speed = int(min(dist, 7))
    angle = round(angle) # round to get the precise game engine angle that will be used
    # find the reachable x and y
    reachable_x = ship.x + speed*math.cos(math.radians(angle))
    reachable_y = ship.y + speed*math.sin(math.radians(angle))
    ship_tra = (ship.x, ship.y, reachable_x, reachable_y)
    if trajectories_intersect_l(ship_tra, trajectories):
        return None
    logging.info("SENDING CMD FOR %s TO (%s, %s)" % (ship.id, reachable_x, reachable_y))
    return ship.thrust(speed, angle)

# same as navigate2, but checks ships collision according to trajectories, caches distance and angle
def attempt_nav(ship, target, dist, angle, trajectories, bad_angle_tuples, max_corrections=179, angular_step=1):
    if max_corrections <= 0:
        return None
    # gdi, took me forever to figure out.. make angles positive!!
    if angle < 0:
        angle = 360+angle

    safe_dist = dist
    safe_angle = angle
    if target.x < 1 or target.y < 1 or target.x > map_width-1 or target.y > map_height-1:
        target.x = max(1, min(map_width-1, target.x))
        target.y = max(1, min(map_height-1, target.y))
        safe_dist = math.floor(ship.calculate_distance_between(target))
        safe_angle = ship.calculate_angle_between(target)

    obstacle_between = False
    for tup in bad_angle_tuples:
        logging.info("SAFE_ANGLE: %s", angle)
        direct_angle = tup[0]
        angle_range = tup[1]
        angle_diff = abs(direct_angle-safe_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        logging.info("DIRECT ANGLE: %s ANGLE_RANGE: %s" % (direct_angle, angle_range))
        if angle_diff <= (angle_range+1):
            obstacle_between = True

    if not obstacle_between:
    #if not game_map.obstacles_between(ship, target, (hlt.entity.Ship)):
        logging.info("FINAL ANGLE: %s" % safe_angle)
        # will only return with cmd if it doesn't hit other trajectories
        cmd = move_ship(ship, safe_dist, safe_angle, trajectories)
        if cmd:
            return cmd

    # if planet/trajectory blocking, recursively look for another angle
    sign = 1 if (180-max_corrections) % 2 == 1 else -1
    new_target_dangle = sign*(180-max_corrections)*angular_step
    new_target_dx = math.cos(math.radians(angle + new_target_dangle)) * dist 
    new_target_dy = math.sin(math.radians(angle + new_target_dangle)) * dist
    new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
    return attempt_nav(ship, new_target, dist, angle+new_target_dangle, trajectories, bad_angle_tuples, max_corrections - 1, angular_step)

# given the ultimate destination, move the ship to the closest point possible this turn 
# without hitting the trajectories of other friendly ships or planets
def smart_nav(ship, target, game_map, speed, avoid_obstacles=True, max_corrections=179, angular_step=1,
    ignore_ships=False, ignore_planets=False):
    logging.info("ATTEMPTING SMART NAV FOR %s AT %s TO %s" % (ship.id, (ship.x, ship.y), (target.x, target.y)))
    #logging.info("trajectories:")
    fs_trajectories = []
    close_fs = [fs for fs in entities_within_distance(ship, 15) if (isinstance(fs, hlt.entity.Ship) and fs.owner == me)]
    for fs in close_fs:
        fs_trajectories.append(trajectories[fs.id])
        #logging.info("%s: %s" % (fs.id, str(trajectories[fs.id])))
    dist = ship.calculate_distance_between(target)
    angle = ship.calculate_angle_between(target)
    # cap lookahead distance at 8
    dist = min(dist, 8)
    lookahead_target = hlt.entity.Position(ship.x+dist*math.cos(math.radians(angle)), ship.y+dist*math.sin(math.radians(angle)))

    bad_angle_tuples = []
    close_planets = [e for e in entities_within_distance(ship, dist) if isinstance(e, hlt.entity.Planet)]
    for cp in close_planets:
        d = ship.calculate_distance_between(cp)
        r = cp.radius + ship.radius + 0.1
        sin = r/d
        if sin > 1.0:
            sin = 1.0
        bad_angle_range = math.degrees(math.asin(sin))
        direct_angle = ship.calculate_angle_between(cp)
        bad_angle_tuples.append((direct_angle, bad_angle_range))
    #logging.info("BAD ANGLE TUPLES: %s" % bad_angle_tuples)
    #logging.info("OG ANGLE: %s" % angle)

    return attempt_nav(ship, lookahead_target, dist, angle, fs_trajectories, bad_angle_tuples)


def attempt_nav_swarm(ship, target, dist, angle, trajectories, max_corrections=179, angular_step=1):
    if max_corrections <= 0:
        return None
    # gdi, took me forever to figure out.. make angles positive!!
    if angle < 0:
        angle = 360+angle

    safe_dist = dist
    safe_angle = angle
    if target.x < 1 or target.y < 1 or target.x > map_width-1 or target.y > map_height-1:
        target.x = max(1, min(map_width-1, target.x))
        target.y = max(1, min(map_height-1, target.y))
        safe_dist = math.floor(ship.calculate_distance_between(target))
        safe_angle = ship.calculate_angle_between(target)

    if not game_map.obstacles_between(ship, target, (hlt.entity.Ship)):
        logging.info("FINAL ANGLE: %s" % safe_angle)
        # will only return with cmd if it doesn't hit other trajectories
        cmd = move_ship(ship, safe_dist, safe_angle, trajectories)
        if cmd:
            return cmd

    # if planet/trajectory blocking, recursively look for another angle
    sign = 1 if (180-max_corrections) % 2 == 1 else -1
    new_target_dangle = sign*(180-max_corrections)*angular_step
    new_target_dx = math.cos(math.radians(angle + new_target_dangle)) * dist 
    new_target_dy = math.sin(math.radians(angle + new_target_dangle)) * dist
    new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
    return attempt_nav_swarm(ship, new_target, dist, angle+new_target_dangle, trajectories, max_corrections - 1, angular_step)


def smart_nav_swarm(swarm, swarm_ids, target, game_map, speed, avoid_obstacles=True, max_corrections=179, angular_step=1,
    ignore_ships=False, ignore_planets=False):
    fs_trajectories = []
    close_fs = [fs for fs in entities_within_distance(ship, 14+swarm.radius*2) if (isinstance(fs, hlt.entity.Ship) and fs.owner == me and fs.id not in swarm_ids)]
    for fs in close_fs:
        fs_trajectories.append(trajectories[fs.id])
    dist = swarm.calculate_distance_between(target)
    angle = swarm.calculate_angle_between(target)
    dist = min(dist, 7+swarm.radius*2)
    lookahead_target = hlt.entity.Position(swarm.x+dist*math.cos(math.radians(angle)), swarm.y+dist*math.sin(math.radians(angle)))
    return attempt_nav_swarm(swarm, lookahead_target, dist, angle, fs_trajectories)

def generate_swarm_ship(ships):
    logging.info([(s.x, s.y) for s in ships])
    ship_x = [s.x for s in ships]
    ship_y = [s.y for s in ships]
    min_x = min(ship_x)
    max_x = max(ship_x)
    min_y = min(ship_y)
    max_y = max(ship_y)
    center_x = (min_x + max_x)/2
    center_y = (min_y + max_y)/2
    radius = max((max_x-min_x)/2, (max_y-min_y)/2) + 0.7
    fake_ship = hlt.entity.Ship(None, -1, center_x, center_y, len(ships), None, None, None, None, None, None)
    fake_ship.radius = radius
    logging.info(fake_ship)
    return fake_ship

def attack_ship_swarm(swarm, enemy_ship):
    dist_from_es = swarm.radius
    num_free_es_4 = len(closest_enemy_free_ships_dist(swarm, me, dist=4))
    if num_free_es_4 < ship.health:
        dist_from_es = -ship.radius # go for the collision if we're up in numbers
    navigate_command = smart_nav(ship, ship.closest_point_to(enemy_ship, min_distance=dist_from_es), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return navigate_command


# -------------- Actions ----------------- #

def collide_entity(ship, entity):
    navigate_command = ship.navigate(ship.closest_point_to(entity,
        min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    if ship.calculate_distance_between(entity) < entity.radius + 7:
        navigate_command = ship.navigate(ship.closest_point_to(entity,
            min_distance=-entity.radius), game_map, speed=int(hlt.constants.MAX_SPEED),
            ignore_planets = True, angular_step=1)
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

def attack_ship(ship, enemy_ship, nav=2):
    dist_from_es = 0.5
    num_free_es_4 = len(closest_enemy_free_ships_dist(ship, me, dist=4))
    if enemy_ship.docking_status != ship.DockingStatus.UNDOCKED:
        dist_from_es = 1
    if ship.health < 64 and num_free_es_4 > 0:
        dist_from_es = -0.5 # go for the collision
    p = enemy_prediction_loc[enemy_ship.id]
    prediction_pos = hlt.entity.Position(p[0], p[1])
    target_pos = ship.closest_point_to(prediction_pos, min_distance=dist_from_es)
    #target_pos = ship.closest_point_to(enemy_ship, min_distance=dist_from_es)
    navigate_command = smart_nav(ship, target_pos, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return navigate_command

def kite_ship(ship, enemy_ship, nav=2):
    dist_from_es = 5
    p = enemy_prediction_loc[enemy_ship.id]
    prediction_pos = hlt.entity.Position(p[0], p[1])
    logging.info(prediction_pos)
    target_pos = ship.closest_point_to(prediction_pos, min_distance=dist_from_es)
    #target_pos = ship.closest_point_to(enemy_ship, min_distance=dist_from_es)
    navigate_command = smart_nav(ship, target_pos, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return navigate_command

def flock(ship, closest_fs):
    cmd = smart_nav(ship, ship.closest_point_to(closest_fs, min_distance=0.01), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return cmd

def flock_pos(ship, pos):
    cmd = smart_nav(ship, pos, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return cmd

def flock_trajectory(ship, fs):
    fs_tra = trajectories[fs.id]
    end_x = fs_tra[2]
    end_y = fs_tra[3]
    end_pos = hlt.entity.Position(end_x, end_y)
    return flock_pos(ship, end_pos)

def approach_planet(ship, cd):
    cmd = smart_nav(ship, ship.closest_point_to(cd, min_distance=0), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return cmd

def corner_city(ship, me):
    juke_x = 3 if ship.x < map_width/2 else map_width-3
    juke_y = 3 if ship.y < map_height/2 else map_height-3
    juke_x = max(3, min(map_width-3, juke_x))
    juke_y = max(3, min(map_height-3, juke_y))
    juke_target = hlt.entity.Position(juke_x, juke_y)
    cmd = smart_nav(ship, juke_target, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return cmd

def juke_city(ship, me):
    efs_x = 0
    efs_y = 0
    efs = closest_enemy_free_ships_dist(ship, me, dist=20)
    if len(efs) == 0:
        return None
    for e in efs:
        efs_x += e[0].x
        efs_y += e[0].y
    efs_x = efs_x/len(efs)
    efs_y = efs_y/len(efs)
    efs_pos = hlt.entity.Position(efs_x, efs_y)
    efs_ang = ship.calculate_angle_between(efs_pos)
    juke_ang = (180+efs_ang) % 360
    x_amt = 7.00001*math.cos(math.radians(juke_ang))
    y_amt = 7.00001*math.sin(math.radians(juke_ang))
    juke_x = ship.x + x_amt
    juke_y = ship.y + y_amt

    overshoot_x = juke_x - max(1, min(map_width-1, juke_x))
    overshoot_y = juke_y - max(1, min(map_height-1, juke_y))

    # overshooting both x and y (near corner)
    if abs(overshoot_x) > 0 and abs(overshoot_y) > 0:
        # mainly vertical
        if abs(y_amt) > abs(x_amt):
            dy = y_amt - overshoot_y
            dx = math.sqrt(49 - dy**2 + 0.0001)
            sign = 1 if x_amt < 0 else -1
            juke_x = ship.x + sign*dx
            juke_y = ship.y + dy
        # mainly horizontal
        else:
            dx = x_amt - overshoot_x
            dy = math.sqrt(49 - dx**2 + 0.0001)
            sign = 1 if y_amt < 0 else -1
            juke_x = ship.x + dx
            juke_y = ship.y + sign*dy

    # overshooting x only (near left or right)
    elif abs(overshoot_x) > 0:
        dx = x_amt - overshoot_x
        dy = math.sqrt(49 - dx**2 + 0.0001)
        sign = -1 if abs(270-juke_ang) <= 90 else 1
        juke_x = ship.x + dx
        juke_y = ship.y + sign*dy
    # overshooting y only (near up or down)
    elif abs(overshoot_y) > 0:
        dy = y_amt - overshoot_y
        dx = math.sqrt(49 - dy**2 + 0.0001)
        sign = -1 if abs(180-juke_ang) <= 90 else 1
        juke_x = ship.x + sign*dx
        juke_y = ship.y + dy

    juke_x = max(1, min(map_width-1, juke_x))
    juke_y = max(1, min(map_height-1, juke_y))
    juke_target = hlt.entity.Position(juke_x, juke_y)
    cmd = smart_nav(ship, juke_target, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
    return cmd


# -------------- Command networking and caching ----------------- #

def register_trajectory(ship, cmd):
    if cmd:
        split = cmd.split()
        action = split[0]
        if action == "d":
            trajectories[ship.id] = (ship.x, ship.y, ship.x, ship.y)
        elif action == "t":
            speed = split[2]
            angle = split[3]
            trajectories[ship.id] = (ship.x, ship.y, ship.x+float(speed)*math.cos(math.radians(float(angle))), 
                    ship.y+float(speed)*math.sin(math.radians(float(angle))))
        logging.info("registering trajectory for %s as %s" % (ship.id, trajectories[ship.id]))

def register_command(ship, cmd, err=None):
    if cmd:
        command_dict[ship.id] = cmd
        register_trajectory(ship, cmd)
    else:
        if err:
            logging.info(err)

def thrust_info(thrust_cmd):
    split = thrust_cmd.split()
    logging.info(split)
    action = split[0]
    shipid = split[1]
    speed = int(split[2])
    angle = int(split[3])
    return (speed, angle)



# -------------- Round logic ----------------- #

game_map = game.initial_map
two_player = len(game_map.all_players()) == 2
map_width = game_map.width
map_height = game_map.height
me = game_map.get_me()

previous_enemy_loc = {}
enemy_prediction_loc = {}
nearby_entities_cache = {}
entities_dist_cache = {}
trajectories = {}
command_dict = {}
round_counter = 0
early_game = True
err_msg = "no crash plz"
winning = False

rushing = False
dogfighting = False

if two_player:
    enemy_player = [p for p in game_map.all_players() if p != me][0]
    enemy_ships = [ship for ship in game_map._all_ships() if ship.owner != me]
    es_x = 0
    es_y = 0
    cd_es = []
    for es in enemy_ships:
        es_x += es.x
        es_y += es.y
        logging.info(closest_dockable_planet(es, me))
        cd_es.append(closest_dockable_planet(es, me))
    es_x = es_x/len(enemy_ships)
    es_y = es_y/len(enemy_ships)

    friendly_ships = me.all_ships()
    fs_x = 0
    fs_y = 0
    for fs in friendly_ships:
        fs_x += fs.x
        fs_y += fs.y
    fs_x = fs_x/len(friendly_ships)
    fs_y = fs_y/len(friendly_ships)

    es_center = hlt.entity.Position(es_x, es_y)
    fs_center = hlt.entity.Position(fs_x, fs_y)

    fs_es_dist = fs_center.calculate_distance_between(es_center)

    # don't attack if they're gonna be bunched up in a 3-spot planet
    same_planet = (cd_es[0].id == cd_es[1].id) and (cd_es[1].id == cd_es[2].id) and (cd_es[0].num_docking_spots >= 3)

    if fs_es_dist <= 120 and not same_planet:
        rushing = False
    
while True:



    # -------------- Setup ----------------- #

    game_map = game.update_map()
    me = game_map.get_me()
    round_counter += 1
    logging.info("processing game on frame %s" % (round_counter-1))
    start_time = time.time()

    nearby_entities_cache = {}
    entities_dist_cache = {}
    trajectories = {}
    command_dict = {}

    # ship and planet lists
    friendly_ships = me.all_ships()
    free_ships = [ship for ship in friendly_ships if ship.docking_status == ship.DockingStatus.UNDOCKED]
    docked_ships = [ship for ship in friendly_ships if ship.docking_status != ship.DockingStatus.UNDOCKED]
    enemy_ships = [ship for ship in game_map._all_ships() if ship.owner != me]
    all_planets = game_map.all_planets()
    unowned_planets = [planet for planet in all_planets if not planet.is_owned()]
    enemy_planets = [planet for planet in all_planets if planet.is_owned() and planet.owner != me]
    my_planets = [planet for planet in all_planets if planet.owner == me]
    nonenemy_planets = unowned_planets + my_planets
    dockable_planets = [planet for planet in nonenemy_planets if not planet.is_full()]
    for fs in friendly_ships:
        trajectories[fs.id] = (fs.x, fs.y, fs.x, fs.y)

    # build closest ship lists
    closest_ship_to_planet = {} # closest_ship_to_planet[planet] = [(ship, ship dist)...]
    for p in all_planets:
        ship_dists = []
        for s in free_ships:
            ship_dists.append((s, s.calculate_distance_between(p)))
        ship_dists.sort(key = lambda tup: tup[1])
        closest_ship_to_planet[p] = ship_dists

    # engage docking distance thresholds for all planets
    planet_threshold = {}
    EXTRA = 0
    for p in all_planets:
        planet_threshold[p] = 999999999
        ship_dists = closest_ship_to_planet[p]
        if len(ship_dists) > 0:
            num_free_spots = p.num_docking_spots - len(p.all_docked_ships())
            threshold_index = num_free_spots-1+EXTRA if num_free_spots-1+EXTRA < len(ship_dists) else len(ship_dists)-1
            planet_threshold[p] = ship_dists[threshold_index][1] #genius

    # find ship center
    pc = avg_pos(friendly_ships)

    # build priority level for attacking enemy planets based on planet center
    ep_priority = []
    for ep in enemy_planets:
        dist = pc.calculate_distance_between(ep)
        ep_priority.append((ep, dist))
    ep_priority.sort(key = lambda tup: tup[1])

    # engage attacking distance thresholds for enemy planets for 4-player games
    attack_threshold = {}
    ep_attack_1 = None
    if len(enemy_planets) > 0:
        ep_attack_1 = ep_priority[0][0]
        logging.info("Priority ep1: %s with dist %s" % (ep_attack_1.id, ep_priority[0][1]))
        ship_dists = closest_ship_to_planet[ep_attack_1]
        if len(ship_dists) > 0:
            attack_threshold[ep_attack_1] = ship_dists[int(len(ship_dists)/2)][1]

    ep_attack_2 = None
    if len(enemy_planets) > 1:
        ep_attack_2 = ep_priority[1][0]
        logging.info("Priority ep2: %s with dist %s" % (ep_attack_2.id, ep_priority[1][1]))
        ship_dists = closest_ship_to_planet[ep_attack_2]
        if len(ship_dists) > 0:
            attack_threshold[ep_attack_2] = ship_dists[int(len(ship_dists)/2)][1]

    logging.info("Time used during first setup: %s" % (time.time() - start_time))

    for es in enemy_ships:
        current = (es.x, es.y)
        previous = previous_enemy_loc[es.id] if es.id in previous_enemy_loc else current
        dist_squared = (current[0]-previous[0])**2 + (current[1]-previous[1])**2
        dist = math.sqrt(dist_squared)
        angle = math.atan2(current[0]-previous[0], current[1]-previous[1])
        enemy_prediction_loc[es.id] = (current[0]+math.cos(angle)*dist/2, current[1]+math.sin(angle)*dist/2)
        previous_enemy_loc[es.id] = current

    threat_scores = {}
    strength_scores = {}
    closest_friendlies = {}
    if len(friendly_ships) > len(enemy_ships) + 20 or (not two_player and len(friendly_ships) > 150):
        for ship in friendly_ships:
            threat_scores[ship.id] = 0
            strength_scores[ship.id] = 99999
    else:
        for i in range(len(friendly_ships)):
            ship = friendly_ships[i]
            closest_efs = closest_enemy_free_ship(ship, me)
            if closest_efs and ship.calculate_distance_between(closest_efs) < 225:
                threat_score = 0
                closest_es_dist = closest_enemy_ships_dist(ship, me, dist=20)
                for es_dist in closest_es_dist:
                    es_score = 1
                    if es_dist[0].docking_status != ship.DockingStatus.UNDOCKED:
                        es_score = 0.25
                    threat_score  += es_score
                threat_scores[ship.id] = threat_score
            else:
                threat_scores[ship.id] = 0

            strength_score = 1
            closest_fs_dist = closest_friendly_ships_dist(ship, me, dist=10)
            for fs_dist in closest_fs_dist:
                fs_score = 1
                if fs_dist[0].docking_status != ship.DockingStatus.UNDOCKED:
                    fs_score = 0.25
                strength_score  += fs_score
            strength_scores[ship.id] = strength_score

            # save closest friendlies
            closest_friendlies[ship.id] = closest_friendly_ships_dist(ship, me, dist=40, sort=True)


    logging.info("Time used during setup: %s" % (time.time() - start_time))



    # -------------- Early game ----------------- #

    # reevaluate dogfighting if it's on (to turn off)
    if dogfighting:
        dogfighting = False
        rushing = False
        for ship in friendly_ships:
            closest_es = closest_enemy_free_ship(ship, me)
            if ship.calculate_distance_between(closest_es) < 80:
                dogfighting = True
    else:
        if len(friendly_ships) < 5:
            for ship in friendly_ships:
                # check if three es are within 80
                num_es_3 = closest_enemy_free_ships_dist(ship, me, dist=80)
                if len(num_es_3) >= 3:
                    dogfighting = True
                    rushing = False

    early_game = early_game and ((len(my_planets) < 3 and round_counter < 20) or rushing or dogfighting)
    if early_game:
        if not two_player and len(friendly_ships) > 3:
            early_game = False

    if early_game:
        logging.info("EARLY GAME %s" % round_counter)
        if not (rushing or dogfighting):
            # make target planets
            target_planets = {}
            # set initial target_planets to closest dockable w/o over-docking
            for ship in free_ships:
                cd_list = closest_dockable_planet_list(ship, me)
                for cd in cd_list:
                    dist = ship.calculate_distance_between(cd)
                    # only send dockable number of ships
                    if dist <= planet_threshold[cd]:
                        target_planets[ship.id] = cd
                        break

            # send other ships to center planets if any ships going to center
            if two_player:
                for sid in target_planets:
                    if target_planets[sid].id < 4:
                        # reassign ships to center planets
                        for ship in free_ships:
                            cd_list = closest_dockable_center_planet_list(ship, me)
                            for cd in cd_list:
                                dist = ship.calculate_distance_between(cd)
                                # only send dockable number of ships
                                if dist <= planet_threshold[cd]:
                                    target_planets[ship.id] = cd
                                    break

            # approach and dock target planets
            for ship in free_ships:
                cd = target_planets[ship.id]
                # dock if we can
                if ship.can_dock(cd):
                    cmd = ship.dock(cd)
                    register_command(ship, cmd)
                    logging.info("%s docking" % ship.id)
                else:
                    cmd = approach_planet(ship, cd)
                    register_command(ship, cmd)

        else:
            for ship in docked_ships:
                if ship.docking_status == hlt.entity.Ship.DockingStatus.DOCKED:
                    logging.info("undocking %s" % ship.id)
                    cmd = ship.undock()
                    register_command(ship, cmd)
            # check if we need to group up
            group_up = False
            for s1 in free_ships:
                for s2 in free_ships:
                    if s1.calculate_distance_between(s2) > 2.5:
                        group_up = True
            if group_up:
                group_pos = avg_pos(free_ships)
                for ship in free_ships:
                    cmd = flock_pos(ship, group_pos)
                    register_command(ship, cmd)
            else:
                # check to see if friendly ships are grouped up and need to navigate as a swarm
                swarm_it = True
                for s1 in free_ships:
                    for s2 in free_ships:
                        if s1.calculate_distance_between(s2) > 2.5:
                            swarm_it = False
                # if friendly ships are grouped up, stay grouped up and navigate as a swarm
                if swarm_it and len(free_ships) > 1:
                    fighting_swarm = generate_swarm_ship(free_ships)
                    swarm_ids = [s.id for s in free_ships]
                    # attack closest es
                    closest_es = closest_enemy_ship(fighting_swarm, me)

                    if False and closest_es.docking_status == hlt.entity.Ship.DockingStatus.UNDOCKED and ship.calculate_distance_between(closest_es) < 15:
                        logging.info("KITING")
                        dist_from_es = 4
                        for ship in free_ships:
                            cmd = attack_ship(ship, closest_es)
                            register_command(ship, cmd)

                    else:
                        dist_from_es = fighting_swarm.radius
                        target_pos = fighting_swarm.closest_point_to(closest_es, min_distance=dist_from_es)
                        swarm_cmd = smart_nav_swarm(fighting_swarm, swarm_ids, target_pos, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
                        if swarm_cmd != None:
                            cmd_info = thrust_info(swarm_cmd)
                            speed = cmd_info[0]
                            angle = cmd_info[1]
                            for ship in free_ships:
                                register_command(ship, ship.thrust(speed, angle))

                # otherwise if friendly ships are split up, just attack individually
                else:
                    for ship in free_ships:
                        closest_es = closest_enemy_ship(ship, me)
                        cmd = attack_ship(ship, closest_es)
                        err_msg = "%s failed to dogfight es %s" % (ship.id, closest_es.id)
                        register_command(ship, cmd, err=err_msg)



    # -------------- Main game ----------------- #

    else:
        logging.info("MAIN GAME %s" % round_counter)
        # check if we should run away in 4-player games
        runaway = False
        if not two_player:
            if round_counter >= 80:
                num_planets_owned = len(game_map.planets_for_player(me))
                for p in game_map.all_players():
                    num_enemy_planets = len(game_map.planets_for_player(p)) 
                    if num_enemy_planets > 2*num_planets_owned and num_enemy_planets > 10:
                        logging.info("aborting offense, juke city time")
                        runaway = True
            
        # run away if conditions in a 4-player game are met
        if runaway:
            for i in range(len(docked_ships)):
                ship = docked_ships[i]
                cmd = ship.undock()
                register_command(ship, cmd)
            docked_ships = []
            for i in range(len(free_ships)):
                if time.time() >= start_time + 1.5:
                    logging.info("1.5 s exceeded")
                    break
                ship = free_ships[i]
                efs = closest_enemy_free_ships_dist(ship, me, dist=20)
                fs = closest_friendly_ships_dist(ship, me, dist=3)
                cmd = corner_city(ship, cmd) if len(efs) == 0 or len(fs) > 0 else juke_city(ship, cmd)
                register_command(ship, cmd)
            free_ships = []

        # calculate list of invaders and ships to defend against invaders
        invaders = set()
        defense_target = {}
        for p in my_planets:
            p_docked_ships = p.all_docked_ships()
            ds_pos = avg_pos(p_docked_ships)
            safe_zone = 30 + p.radius
            invaders = [inv[0] for inv in closest_enemy_free_ships_dist(ds_pos, me, dist=safe_zone, sort=True)]
            num_invaders = len(invaders)
            if num_invaders > 0:
                closest_free_ships = [cfs[0] for cfs in closest_free_ships_dist(ds_pos, me, dist=safe_zone, sort=True)]
                closest_free_ships = closest_free_ships[0:num_invaders+1]
                for cfs in closest_free_ships:
                    defense_target[cfs.id] = invaders[0]
                    # make defender stronger
                    strength_scores[cfs.id] += 3

        # calculate threatened ships
        threatened_ships = []
        for i in range(len(free_ships)):
            ship = free_ships[i]
            threat_score = threat_scores[ship.id]
            strength_score = strength_scores[ship.id]
            if threat_score > strength_score or (round_counter < 100 and threat_score > 0.75*strength_score):
                logging.info("threat level too high, %s will attempt to flock" % ship.id)
                threatened_ships.append(ship)
                # remove from free ships
                free_ships[i] = None

        # main loop across free_ships (non threatened)
        for i in range(len(free_ships)):
            if time.time() >= start_time + 1.5:
                logging.info("1.5 s exceeded")
                break
            
            ship = free_ships[i]
            if ship == None:
                continue

            # follow closest friendly if it has a movement action when near enemy
            closest_es = closest_enemy_ship(ship, me)
            if ship.calculate_distance_between(closest_es) < 30:
                followable_friendlies = closest_friendly_ships_dist(ship, me, dist=3, sort=True)
                will_follow = False
                for ff_tup in followable_friendlies:
                    ff = ff_tup[0]
                    #logging.info("ff id %s" % ff.id)
                    if ff.id in trajectories:
                        tra = trajectories[ff.id]
                        if tra[0] != tra[2] and tra[1] != tra[3]:
                            logging.info("%s is following %s" % (ship.id, ff.id))
                            dx = ship.x - ff.x
                            dy = ship.y - ff.y
                            end_pos = hlt.entity.Position(tra[2]+dx, tra[3]+dy)
                            cmd = smart_nav(ship, end_pos, game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
                            register_command(ship, cmd)
                            will_follow = True
                            break
                if will_follow:
                    continue

            # attack a close ship if we're within 50 of a planet
            go_ham = False
            for p in all_planets:
                if ship.calculate_distance_between(p) < 50:
                    go_ham = True
                    break
            if go_ham:
                closest_es = closest_enemy_ship(ship, me)
                if ship.calculate_distance_between(closest_es) < 10:
                    cmd = attack_ship(ship, closest_es)
                    register_command(ship, cmd)
                    continue

            # 1. check if docked ships need defense
            if ship.id in defense_target:
                cmd = attack_ship(ship, defense_target[ship.id])
                err_msg = "ship %s couldn't move to attack invader %s" % (ship.id, defense_target[ship.id].id)
                register_command(ship, cmd, err=err_msg)
                continue

            # 2. if there's an enemy near, go ham
            max_ham_distance = 30
            ce = closest_enemy_planet(ship, me)
            if ce:
                # find closest docked ship on ce
                closest_eds = None
                closest_dist = 999999999
                for eds in ce.all_docked_ships():
                    dist = ship.calculate_distance_between(eds)
                    if dist < closest_dist:
                        closest_eds = eds
                        closest_dist = dist

                if closest_eds and ship.calculate_distance_between(closest_eds) <= max_ham_distance:
                    cmd = attack_ship(ship, closest_eds)
                    err_msg = "ship %s couldn't move to attack planet %s docked ship %s" % (ship.id, ce.id, closest_eds.id)
                    register_command(ship, cmd, err=err_msg)
                    continue

            # 3. otherwise, go for closest nonenemy planet if it exists (in order of closeness)
            target_planet = None
            max_explore_distance = 100 if two_player else 50
            for cd in closest_dockable_planet_list(ship, me):
                # only go if ship is nth closest or closer (n = num docking spots left) or we make single ship investment if num free_ships > 5
                if not two_player and len(my_planets) < 5 and cd.id < 4:
                    continue
                dist = ship.calculate_distance_between(cd)
                threshold = planet_threshold[cd]
                investment_threshold = closest_ship_to_planet[cd][0][1]
                if (dist <= threshold and dist <= max_explore_distance) or (dist <= investment_threshold and not cd.is_owned() and len(free_ships) > 5):
                    target_planet = cd
                    break
            if target_planet:
                # consider docking if we can dock
                if ship.can_dock(cd):
                    es = closest_enemy_free_ship(ship, me)
                    # make sure we aren't close to an enemy ship when docking, smart dock
                    if es == None or ship.calculate_distance_between(es) > 30:
                        cmd = ship.dock(cd)
                        register_command(ship, cmd)
                        logging.info("%s docking" % ship.id)
                    # if an enemy ship is close, docking isn't safe, so go ham
                    else:
                        cmd = attack_ship(ship, es)
                        err_msg = "ship %s couldn't move to attack ship %s" % (ship.id, es.id)
                        register_command(ship, cmd, err=err_msg)

                # go towards a position where we can dock
                else:
                    cmd = approach_planet(ship, cd)
                    err_msg = "ship %s couldn't move to planet %s" % (ship.id, cd.id)
                    register_command(ship, cmd, err=err_msg)
                continue

            # 4. no close nonenemy planets to fill up, go ham on enemy
            # go for planet closest to center of my planets
            if len(free_ships) < 30:
                if len(enemy_planets) > 0:
                    target_planet = ep_attack_1
                    cmd = attack_docked_planet(ship, target_planet)
                    err_msg = "ship %s couldn't move to attack planet %s" % (ship.id, target_planet.id)
                    register_command(ship, cmd, err=err_msg)
                    continue
            else:
                if len(enemy_planets) > 0:
                    target_planet = ep_attack_1
                    dist = ship.calculate_distance_between(target_planet)
                    threshold = attack_threshold[target_planet]
                    if dist <= threshold:
                        cmd = attack_docked_planet(ship, target_planet)
                        err_msg = "ship %s couldn't move to attack planet %s" % (ship.id, target_planet.id)
                        register_command(ship, cmd, err=err_msg)
                        continue

                if len(enemy_planets) > 1:
                    target_planet = ep_attack_2
                    dist = ship.calculate_distance_between(target_planet)
                    threshold = attack_threshold[target_planet]
                    #if dist <= threshold:
                    if True:
                        cmd = attack_docked_planet(ship, target_planet)
                        err_msg = "ship %s couldn't move to attack planet %s" % (ship.id, target_planet.id)
                        register_command(ship, cmd, err=err_msg)
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
                err_msg = "ship %s couldn't move to attack closest ship %s" % (ship.id, closest_es.id)
                register_command(ship, cmd, err=err_msg)
            else:
                logging.info("weird... couln't find closest_es when no enemy planets")

        # flock threatened_ships to closest swarm_ship's trajectory
        for ship in threatened_ships:
            if time.time() >= start_time + 1.5:
                logging.info("1.5 s exceeded")
                break
            cf_dists = closest_friendlies[ship.id]
            # want to choose the closest friendly that has strength > threat
            swarm_ship = None
            for cf_tup in cf_dists:
                cf_ship = cf_tup[0]
                cf_strength = strength_scores[cf_ship.id]
                cf_threat = threat_scores[cf_ship.id]
                if cf_strength > cf_threat:
                    swarm_ship = cf_ship
                    break
            # go towards closest friendly with strength > threat (range capped at 40)
            if swarm_ship:
                cmd = flock_trajectory(ship, swarm_ship)
                err_msg = "ship %s couldn't move towards ship %s" % (ship.id, swarm_ship.id)
                register_command(ship, cmd, err=err_msg)
            # otherwise juke city
            else:
                cmd = juke_city(ship, me)
                err_msg = "attempt juke city"
                register_command(ship, cmd, err=err_msg)
                logging.info("JUKE CITY")


    command_queue = []
    for sid in command_dict:
        command_queue.append(command_dict[sid])
    game.send_command_queue(command_queue)
    """
    logging.info("Trajectories")
    for key in trajectories:
        logging.info("%s -- %s" % (key, trajectories[key]))
    logging.info("Commands")
    for cmd in command_queue:
        split = cmd.split()
        action = split[0]
        shipid = split[1]
        if action == "d":
            trajectories[ship.id] = (ship.x, ship.y, ship.x, ship.y)
            logging.info("%s: docking" % shipid)
        elif action == "t":
            speed = split[2]
            angle = split[3]
            logging.info("%s: thrust %s %s" % (shipid, speed, angle))
    """
    time_used = time.time() - start_time
    logging.info("Time used: %f" % time_used)
    # TURN END
# GAME END
