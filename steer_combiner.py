from random import uniform
import pygame as pg
from trunc_sum import trunc_sum

"""
Combining steering behaviours, e.g. wander, seek, evade using priorities and weights.

Implements an idea I found here:

https://alastaira.wordpress.com/2013/03/13/methods-for-combining-autonomous-steering-behaviours/

Excerpt from this page below

4. Weighted Prioritised Truncated Sum
--------------------------------------
Apart from having a silly name, this is my favoured approach, as it is a nice balanced hybrid method that makes use of 
both weight and priority assigned to each behaviour. Once again, behaviours are considered in priority order, with the
highest priority behaviour being considered first. Any steering force generated by this behaviour is multiplied by its 
assigned weight and added to a running total. Then, the total (weighted) force accumulated so far is compared to the 
maximum allowed force on the character. If the maximum allowed force has not yet been reached, the next highest priority
behaviour is considered, the steering force it generates is weighted, and then this is added onto the cumulative total. 
And so on, until either all of the steering behaviours have been considered, or the total maximum steering force has 
been assigned, whichever occurs first. If at any point there is still some surplus steering force left, but not enough 
to allocate the whole of the desired steering force from the next highest-priority behaviour, the extra force is 
truncated and what can be accommodated is added to the total (hence the weighted prioritised truncated sum).

"""
vec = pg.math.Vector2


def wander_steer(params, options):
    pos = params["pos"]
    vel = params["vel"]
    max_speed = params["max_speed"]
    ring_radius = options["ring_radius"]
    ring_distance = options["ring_distance"]
    weight = options["weight"]
    if vel.length() == 0:
        vel = vec(uniform(0, max_speed), 0).rotate(uniform(0, 360))
    max_force = params["max_force"]
    future_pos = pos + vel.normalize() * ring_distance
    target_pos = future_pos + vec(ring_radius, 0).rotate(uniform(0, 360))
    desired_vel = (target_pos - pos).normalize() * max_speed
    steer = desired_vel - vel
    if steer.length() > max_force:
        steer.scale_to_length(max_force)
    return weight * steer


def seek_steer(params, options):
    pos = params["pos"]
    vel = params["vel"]
    max_speed = params["max_speed"]
    max_force = params["max_force"]
    target_pos = options["target_pos"]
    target_weight = options["target_weight"]
    detect_radius = options["detect_radius"]
    approach_radius = options["approach_radius"]
    weight = options["weight"]
    steer = vec(0, 0)
    dist = target_pos - pos
    if detect_radius > dist.length() > 0:
        desired_vel = dist.normalize() * max_speed
        if dist.length() < approach_radius:
            desired_vel *= dist.length() / approach_radius
        steer = desired_vel - vel
        if steer.length() > max_force:
            steer.scale_to_length(max_force)
    return target_weight * weight * steer


def evade_steer(params, options):
    steer = vec(0, 0)
    pos = params["pos"]
    vel = params["vel"]
    max_speed = params["max_speed"]
    max_force = params["max_force"]
    target_pos = options["target_pos"]
    target_weight = options["target_weight"]
    detect_radius = options["detect_radius"]
    weight = options["weight"]
    dist = pos - target_pos  # opposite sign to seek
    if detect_radius > dist.length() > 0:
        desired_vel = dist.normalize() * max_speed
        steer = desired_vel - vel
        if steer.length() > max_force:
            steer.scale_to_length(max_force)
    return target_weight * weight * steer


steering_functions = {"wander": wander_steer, "seek": seek_steer, "evade": evade_steer}


def combined_steer(params, priority_ordered_info):
    max_force = params["max_force"]
    total_steer = vec(0, 0)
    steers = []  # to store steer components to be able to return them at end
    for behaviour, options in priority_ordered_info:
        if options["weight"] == 0:
            continue
        steer = steering_functions[behaviour](params, options)
        steers.append((behaviour, steer))
        total_steer += steer
        if total_steer.length() >= max_force:
            # overshoot
            total_steer -= steer
            steers.pop()
            # add as much of this steer as possible up to max_force
            steer_scaled = trunc_sum(total_steer, steer, max_force)
            steers.append((behaviour, steer_scaled))
            total_steer += steer_scaled
            break
    if total_steer.length() < max_force:
        total_steer.scale_to_length(max_force)
    return total_steer, steers