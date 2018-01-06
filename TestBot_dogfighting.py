import hlt
import logging
import time
import math

game = hlt.Game("ezboi")
logging.info("Starting my dope bot!")

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

def closest_dockable_center_planet_list(ship, me):
    nearest_planet_list = []
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Planet) and not entity.is_full() and (not entity.is_owned() or entity.owner == me):
                if entity.id < 4:
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

def closest_enemy_free_ship(ship, me):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and entity.owner != me and entity.docking_status == ship.DockingStatus.UNDOCKED:
                return entity
    return None

def closest_enemy_free_ships_dist(ship, me, dist=100, sort=False):
    enemy_ships_dist = []
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
        if distance < dist:
            for entity in entities_by_distance[distance]:
                if isinstance(entity, hlt.entity.Ship) and entity.owner != me and entity.docking_status == ship.DockingStatus.UNDOCKED:
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


# -------------- Geometry ----------------- #

# returns list of ships within dist and planet with surfaces within dist, extra fudge of 0.6
def entities_within_distance(ship, dist):
    entities = []
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    for distance in entities_by_distance:
        for entity in entities_by_distance[distance]:
            if isinstance(entity, hlt.entity.Ship) and ship.calculate_distance_between(entity) < dist+0.6:
                entities.append(entity)
            if isinstance(entity, hlt.entity.Planet) and ship.calculate_distance_between(entity) < dist+entity.radius+0.6:
                entities.append(entity)
    return entities

def trajectories_intersect(line1, line2):
    max_t = 100 # could do high_accuracy setting and change back down to 30
    startx_1, starty_1, endx_1, endy_1 = line1[0], line1[1], line1[2], line1[3]
    startx_2, starty_2, endx_2, endy_2 = line2[0], line2[1], line2[2], line2[3]
    dx_1 = endx_1 - startx_1
    dy_1 = endy_1 - starty_1
    dx_2 = endx_2 - startx_2
    dy_2 = endy_2 - starty_2
    for t in range(max_t+1):
        t_factor = float(t)/max_t
        tx_1 = startx_1 + t_factor*dx_1
        ty_1 = starty_1 + t_factor*dy_1
        tx_2 = startx_2 + t_factor*dx_2
        ty_2 = starty_2 + t_factor*dy_2
        # could change distance setting for high_accuracy as well (to like 1.1)
        if (tx_2-tx_1)**2 + (ty_2-ty_1)**2 <= 1.001:
            return True
    return False

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
            if (tx_2-tx_1)**2 + (ty_2-ty_1)**2 <= 1.001:
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
            if (tx_2-tx_1)**2 + (ty_2-ty_1)**2 <= 1.001:
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
def attempt_nav(ship, target, dist, angle, trajectories, max_corrections=179, angular_step=1):
    if max_corrections <= 0:
        return None
    # gdi, took me forever to figure out.. make angles positive!!
    if angle < 0:
        angle = 360+angle
    # fastest path around planets is the closest to a straight line
    if not game_map.obstacles_between(ship, target, (hlt.entity.Ship)):
        #logging.info("attempting end point: (%s, %s)" % (target.x, target.y))
        # will only return with cmd if it doesn't hit other trajectories
        cmd = move_ship(ship, dist, angle, trajectories)
        if cmd:
            return cmd
    # if planet/trajectory blocking, recursively look for another angle
    sign = 1 if (180-max_corrections) % 2 == 1 else -1
    new_target_dangle = sign*(180-max_corrections)*angular_step
    new_target_dx = math.cos(math.radians(angle + new_target_dangle)) * dist 
    new_target_dy = math.sin(math.radians(angle + new_target_dangle)) * dist
    new_target = hlt.entity.Position(ship.x + new_target_dx, ship.y + new_target_dy)
    return attempt_nav(ship, new_target, dist, angle+new_target_dangle, trajectories, max_corrections - 1, angular_step)

# given the ultimate destination, move the ship to the closest point possible this turn 
# without hitting the trajectories of other friendly ships or planets
def smart_nav(ship, target, game_map, speed, avoid_obstacles=True, max_corrections=179, angular_step=1,
    ignore_ships=False, ignore_planets=False):
    logging.info("ATTEMPTING SMART NAV FOR %s AT %s TO %s" % (ship.id, (ship.x, ship.y), (target.x, target.y)))
    logging.info("trajectories:")
    fs_trajectories = []
    close_fs = [fs for fs in entities_within_distance(ship, 15) if (isinstance(fs, hlt.entity.Ship) and fs.owner == me)]
    for fs in close_fs:
        fs_trajectories.append(trajectories[fs.id])
        logging.info("%s: %s" % (fs.id, str(trajectories[fs.id])))
    dist = ship.calculate_distance_between(target)
    angle = ship.calculate_angle_between(target)
    return attempt_nav(ship, target, dist, angle, fs_trajectories)


# -------------- Actions ----------------- #

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
    dist_from_es = 0
    num_free_es_4 = len(closest_enemy_free_ships_dist(ship, me, dist=4))
    if enemy_ship.docking_status != ship.DockingStatus.UNDOCKED:
        dist_from_es = 1
    if ship.health < 64 and num_free_es_4 > 0:
        dist_from_es = -0.5 # go for the collision
    navigate_command = smart_nav(ship, ship.closest_point_to(enemy_ship, min_distance=dist_from_es), game_map, speed=int(hlt.constants.MAX_SPEED), angular_step=1)
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
    x_amt = 7*math.cos(math.radians(juke_ang))
    y_amt = 7*math.sin(math.radians(juke_ang))
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




# -------------- Round logic ----------------- #

game_map = game.initial_map
two_player = len(game_map.all_players()) == 2
map_width = game_map.width
map_height = game_map.height
me = game_map.get_me()

trajectories = {}
command_dict = {}
round_counter = 0
early_game = True

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
        dogfighting = True
    

while True:



    # -------------- Setup ----------------- #

    game_map = game.update_map()
    me = game_map.get_me()
    round_counter += 1
    logging.info("processing game on frame %s" % (round_counter-1))
    start_time = time.time()
    
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

    # find weighted planet center
    pc = hlt.entity.Entity(map_width/2, map_height/2, 0, None, None, None)
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


    threat_scores = {}
    strength_scores = {}
    closest_friendlies = {}
    for i in range(len(friendly_ships)):
        ship = friendly_ships[i]
        # do threat/strength scores
        # assess threat level
        threat_score = 0
        closest_es_dist = closest_enemy_ships_dist(ship, me, dist=20)
        has_undocked = False
        for es_dist in closest_es_dist:
            es_score = 1
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
        threat_scores[ship.id] = threat_score

        # assess strength level
        strength_score = 1
        closest_fs_dist = closest_friendly_ships_dist(ship, me, dist=5)
        for fs_dist in closest_fs_dist:
            fs_score = 1
            # 1/4 the threat level of docked ships
            if fs_dist[0].docking_status != ship.DockingStatus.UNDOCKED:
                fs_score = float(fs_score)/4
            strength_score  += fs_score
        logging.info("%s has strength score: %s" % (ship.id, strength_score))
        strength_scores[ship.id] = strength_score

        # save closest friendlies
        closest_friendlies[ship.id] = closest_friendly_ships_dist(ship, me, dist=40, sort=True)


    logging.info("Time used during setup: %s" % (time.time() - start_time))



    # -------------- Early game ----------------- #

    early_game = early_game and ((len(my_planets) < 1 and round_counter < 30) or dogfighting)

    if early_game:
        if two_player:
            if not dogfighting:
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

                    #todo: adjusting dogfighting after killing a single enemy -- check dogfighting each round? closest es within

                # approach and dock target planets
                for ship in free_ships:
                    cd = target_planets[ship.id]
                    # dock if we can
                    if ship.can_dock(cd):
                        # check if closest es is within 50, turn on dogfighting if True (dogfighting case will evaluate and overwrite commands)
                        closest_es = closest_enemy_ship(ship, me)
                        if ship.calculate_distance_between(closest_es) < 50:
                            dogfighting = True
                        cmd = ship.dock(cd)
                        register_command(ship, cmd)
                        logging.info("%s docking" % ship.id)
                    else:
                        cmd = approach_planet(ship, cd)
                        register_command(ship, cmd)

            if dogfighting:
                for ship in free_ships:
                    closest_es = closest_enemy_ship(ship, me)
                    logging.info("%s attempting to dogfight es %s" % (ship.id, closest_es.id))
                    cmd = attack_ship(ship, closest_es)
                    err_msg = "%s failed to dogfight es %s" % (ship.id, closest_es.id)
                    register_command(ship, cmd, err=err_msg)
        else:
            for ship in free_ships:
                # in order of closeness for dockable planets
                for cd in closest_dockable_planet_list(ship, me):
                    dist = ship.calculate_distance_between(cd)
                    if dist <= planet_threshold[cd]:
                        if ship.can_dock(cd):
                            cmd = ship.dock(cd)
                            register_command(ship, cmd)
                            logging.info("%s docking" % ship.id)
                        else:
                            cmd = approach_planet(ship, cd)
                            register_command(ship, cmd)
                        break


    # -------------- Main game ----------------- #

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

        # calculate threatened ships
        threatened_ships = []
        for i in range(len(free_ships)):
            ship = free_ships[i]
            threat_score = threat_scores[ship.id]
            strength_score = strength_scores[ship.id]
            if threat_score > strength_score:
                logging.info("threat level too high, %s will attempt to flock" % ship.id)
                threatened_ships.append(ship)
                # remove from free ships
                free_ships[i] = None

        # check if we should run away in 4-player games
        runaway = False
        if not two_player:
            if round_counter >= 80:
                num_planets_owned = len(game_map.planets_for_player(me))
                for p in game_map.all_players():
                    if len(game_map.planets_for_player(p)) > 2*num_planets_owned:
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
                if time.time() >= start_time + 1.4:
                    logging.info("1.4 s exceeded")
                    break
                ship = free_ships[i]
                efs = closest_enemy_free_ships_dist(ship, me, dist=20)
                fs = closest_friendly_ships_dist(ship, me, dist=3)
                cmd = corner_city(ship, cmd) if len(efs) == 0 or len(fs) > 0 else juke_city(ship, cmd)
                register_command(ship, cmd)
            free_ships = []



        # main loop across free_ships (non threatened)
        for i in range(len(free_ships)):
            if time.time() >= start_time + 1.4:
                logging.info("1.4 s exceeded")
                break
            
            ship = free_ships[i]
            if ship == None:
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
            cont = False
            max_explore_distance = 100 if two_player else 50
            for cd in closest_dockable_planet_list(ship, me):
                # only go if ship is nth closest or closer (n = num docking spots left) or we make single ship investment if num free_ships > 5
                dist = ship.calculate_distance_between(cd)
                threshold = planet_threshold[cd]
                investment_threshold = closest_ship_to_planet[cd][0][1]
                if (dist <= threshold and dist <= max_explore_distance) or (dist <= investment_threshold and not cd.is_owned() and len(free_ships) > 5):

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
                    cont = True
                    break
            if cont:
                continue

            # 4. no close nonenemy planets to fill up, go ham on enemy
            # go for planet closest to center of my planets
            if two_player:
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
                    if dist <= threshold:
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
            if time.time() >= start_time + 1.4:
                logging.info("1.4 s exceeded")
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
