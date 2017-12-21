"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
import hlt
import logging

game = hlt.Game("Settler")
logging.info("Starting my Settler bot!")

while True:
    game_map = game.update_map()
    command_queue = []

    for ship in game_map.get_me().all_ships():
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        for planet in game_map.all_planets():
            if planet.is_owned():
                continue

            if ship.can_dock(planet):
                command_queue.append(ship.dock(planet))
            else:
                navigate_command = ship.navigate(
                        ship.closest_point_to(planet),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED/2),
                        ignore_ships=True)
                if navigate_command:
                    command_queue.append(navigate_command)
            break

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
