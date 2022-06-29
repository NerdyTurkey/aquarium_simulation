"""
Mean value of these properties different for each fish type.
Variance within fish type between min and max valus (either uniform or normal distbn?)
"""

# (min, max) values to allow random assignment using uniform or normal distribution

fish_properties = {
    "1": {
        "description": "large, happy, gormless",
        # animation
        "has_chomp": False,
        "hover_frame_update_interval": (45, 55),  # ms
        "swim_dart_frame_update_distance": (3, 7),  # pix
        # physics
        "max_force": (0.3, 0.50),
        "min_speed_hover": (4, 8),
        "min_speed_swim": (20, 40),
        "min_speed_dart": (100, 140),
        "max_speed_hover": (10, 20),
        "max_speed_swim": (40, 80),
        "max_speed_dart": (200, 280),
        "max_angle_with_horizontal": (5, 15),  # degrees
        # state changes
        "min_state_duration": (1500, 2500),
        "max_state_duration": (80000, 12000),
        "acceleration_duration": (1500, 2500),
        # These need to be normalised to sum to 1
        "prob_swim": (0.4, 0.5),
        "prob_hover": (0.4, 0.50),
        "prob_dart": (0.05, 0.15),
        # modifiers
        "prob_chomp": (0.1, 0.3),
        # wander steering params
        "rand_target_time": (150, 250),
        "wander_ring_distance": (300, 500),
        "wander_ring_radius": (30, 70),
    },
    "2": {
        "description": "large, angry, pompous",
        # animation
        "has_chomp": True,
        "hover_frame_update_interval": (45, 55),  # ms
        "swim_dart_frame_update_distance": (3, 7),  # pix
        # physics
        "max_force": (0.3, 0.50),
        "min_speed_hover": (4, 8),
        "min_speed_swim": (20, 40),
        "min_speed_dart": (100, 140),
        "max_speed_hover": (10, 20),
        "max_speed_swim": (40, 80),
        "max_speed_dart": (200, 280),
        "max_angle_with_horizontal": (5, 15),  # degrees
        # state changes
        "min_state_duration": (1500, 2500),
        "max_state_duration": (80000, 12000),
        "acceleration_duration": (1500, 2500),
        # These need to be normalised to sum to 1
        "prob_swim": (0.4, 0.5),
        "prob_hover": (0.4, 0.50),
        "prob_dart": (0.05, 0.15),
        # modifiers
        "prob_chomp": (0.1, 0.3),
        # wander steering params
        "rand_target_time": (150, 250),
        "wander_ring_distance": (300, 500),
        "wander_ring_radius": (30, 70),
    },
    "3": {
        "description": "large, tired, pompous",
        # animation
        "has_chomp": True,
        "hover_frame_update_interval": (45, 55),  # ms
        "swim_dart_frame_update_distance": (3, 7),  # pix
        # physics
        "max_force": (0.3, 0.50),
        "min_speed_hover": (4, 8),
        "min_speed_swim": (20, 40),
        "min_speed_dart": (100, 140),
        "max_speed_hover": (10, 20),
        "max_speed_swim": (40, 80),
        "max_speed_dart": (200, 280),
        "max_angle_with_horizontal": (5, 15),  # degrees
        # state changes
        "min_state_duration": (1500, 2500),
        "max_state_duration": (80000, 12000),
        "acceleration_duration": (1500, 2500),
        # These need to be normalised to sum to 1
        "prob_swim": (0.4, 0.5),
        "prob_hover": (0.4, 0.50),
        "prob_dart": (0.05, 0.15),
        # modifiers
        "prob_chomp": (0.1, 0.3),
        # wander steering params
        "rand_target_time": (150, 250),
        "wander_ring_distance": (300, 500),
        "wander_ring_radius": (30, 70),
    },
    "4": {
        "description": "large, tired, fed up",
        # animation
        "has_chomp": False,
        "hover_frame_update_interval": (45, 55),  # ms
        "swim_dart_frame_update_distance": (3, 7),  # pix
        # physics
        "max_force": (0.3, 0.50),
        "min_speed_hover": (4, 8),
        "min_speed_swim": (20, 40),
        "min_speed_dart": (100, 140),
        "max_speed_hover": (10, 20),
        "max_speed_swim": (40, 80),
        "max_speed_dart": (200, 280),
        "max_angle_with_horizontal": (5, 15),  # degrees
        # state changes
        "min_state_duration": (1500, 2500),
        "max_state_duration": (80000, 12000),
        "acceleration_duration": (1500, 2500),
        # These need to be normalised to sum to 1
        "prob_swim": (0.4, 0.5),
        "prob_hover": (0.4, 0.50),
        "prob_dart": (0.05, 0.15),
        # modifiers
        "prob_chomp": (0.1, 0.3),
        # wander steering params
        "rand_target_time": (150, 250),
        "wander_ring_distance": (300, 500),
        "wander_ring_radius": (30, 70),
    },
    "5": {
        "description": "medium, pretty, female",
        # animation
        "has_chomp": False,
        "hover_frame_update_interval": (45, 55),  # ms
        "swim_dart_frame_update_distance": (3, 7),  # pix
        # physics
        "max_force": (0.3, 0.50),
        "min_speed_hover": (4, 8),
        "min_speed_swim": (20, 40),
        "min_speed_dart": (100, 140),
        "max_speed_hover": (10, 20),
        "max_speed_swim": (40, 80),
        "max_speed_dart": (200, 280),
        "max_angle_with_horizontal": (5, 15),  # degrees
        # state changes
        "min_state_duration": (1500, 2500),
        "max_state_duration": (80000, 12000),
        "acceleration_duration": (1500, 2500),
        # These need to be normalised to sum to 1
        "prob_swim": (0.4, 0.5),
        "prob_hover": (0.4, 0.50),
        "prob_dart": (0.05, 0.15),
        # modifiers
        "prob_chomp": (0.1, 0.3),
        # wander steering params
        "rand_target_time": (150, 250),
        "wander_ring_distance": (300, 500),
        "wander_ring_radius": (30, 70),
    },
    "6": {
        "description": "big, scary, predatory",
        # animation
        "has_chomp": True,
        "hover_frame_update_interval": (45, 55),  # ms
        "swim_dart_frame_update_distance": (3, 7),  # pix
        # physics
        "max_force": (0.3, 0.50),
        "min_speed_hover": (4, 8),
        "min_speed_swim": (20, 40),
        "min_speed_dart": (100, 140),
        "max_speed_hover": (10, 20),
        "max_speed_swim": (40, 80),
        "max_speed_dart": (200, 280),
        "max_angle_with_horizontal": (5, 15),  # degrees
        # state changes
        "min_state_duration": (1500, 2500),
        "max_state_duration": (80000, 12000),
        "acceleration_duration": (1500, 2500),
        # These need to be normalised to sum to 1
        "prob_swim": (0.4, 0.5),
        "prob_hover": (0.4, 0.50),
        "prob_dart": (0.05, 0.15),
        # modifiers
        "prob_chomp": (0.1, 0.3),
        # wander steering params
        "rand_target_time": (150, 250),
        "wander_ring_distance": (300, 500),
        "wander_ring_radius": (30, 70),
    },
}
