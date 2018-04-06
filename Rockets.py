#Name:   Rockets.py
#Author: William Miller
#Date:   6-4-18

import tkinter as tk
import time
import random
import math
import sys

def add_vectors(*args):
   #vector format: [mag,dir]

   #Adds X & Y components of all vectors
   #Returns magnitude and direction of resulting vector
   
   xdir = 0
   ydir = 0
   for vector in args:    
      xdir += round(math.cos(vector[1]) * vector[0], 5)   #cos(direction) * magnitude
      ydir += round(math.sin(vector[1]) * vector[0], 5)   #sin(direction) * magnitude

   magnitude = round(math.sqrt(xdir**2 + ydir**2), 5)

   if magnitude == 0:
      return [0,0]
   else:
      sine = round(ydir / magnitude, 5)

      #+- acute angles ok. Must use reference angles for obtuse angles.
      if xdir > 0:
         direction = round(math.asin(sine), 5)
      else:
         direction = round((math.pi   - math.asin(sine)), 5)
         
      return [magnitude, direction]

def compute_distance(pt1, pt2):
   #Point format: [X,Y

   #Returns distance between 2 points using Pythagorean Theorem

   return math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)

def eval_fitness(member):
   #Pass in organism and evaluate its fitness
   #closest = [distance, frame]

   member.fitness = 1000 / (8*member.distance + 3*member.closest[0] + 1*member.closest[1] - 2*member.gene_index)


class Window:
   def __init__(self):

      #Create window
      self.root = tk.Tk()
      self.root.geometry("520x700")
      self.root.title("Rocket Test...")
   
      #Creating canvas
      self.screen = tk.Canvas(self.root, width = 500, height = 600, background = "grey",
                              highlightthickness = 3, highlightbackground = "#525252")
      self.screen.grid(columnspan = 4, row = 0, column = 0, padx = 5)
      
      #Create gravity scroll bar
      self.gravity_var = tk.DoubleVar()
      self.gravity_scale = tk.Scale(self.root, variable = self.gravity_var, label = "Gravity", 
                                    orient = "horizontal", from_ = 0.3, to = 0.6, resolution = 0.01)
      self.gravity_scale.set(0.5)
      self.gravity_scale.grid(column = 0, row = 1)

      #Mutation rate scroll bar
      self.mutation_var = tk.DoubleVar()
      self.mutation_scale = tk.Scale(self.root, variable = self.mutation_var, label = "Mutation Rate", 
                                    orient = "horizontal", from_ = 0, to = 1, resolution = 0.01)
      self.mutation_scale.set(0.45)
      self.mutation_scale.grid(column = 1, row = 1)

      #Population size scroll bar
      self.pop_size_var = tk.DoubleVar()
      self.pop_size_scale = tk.Scale(self.root, variable = self.pop_size_var, label = "Population Size", 
                                    orient = "horizontal", from_ = 3, to = 100, resolution = 1)
      self.pop_size_scale.set(75)
      self.pop_size_scale.grid(column = 2, row = 1)

      #Frame time scroll bar
      self.frame_time_var = tk.DoubleVar()
      self.frame_time_scale = tk.Scale(self.root, variable = self.frame_time_var, label = "Frame Time", 
                                    orient = "horizontal", from_ = 0.001, to = 0.05, resolution = 0.001)
      self.frame_time_scale.set(0.03)
      self.frame_time_scale.grid(column = 3, row = 1)
      self.frame_time = self.frame_time_var.get()

      #Reset Button:
      self.reset = tk.Button(self.root, text = "Reset", command = self.reset_pressed)
      self.reset.grid(columnspan = 4, column = 0, row = 2, pady = 5, sticky = "s")

      #Create target
      self.target = [250,150] #[X,Y]
      self.target_marker = self.screen.create_oval(250,150,255,155, fill = "red")
      self.screen.bind('<Button-1>', self.move_target)

      #Update screen
      self.root.update()

      #Variables
      self.gravity = [self.gravity_var.get(), math.pi/2]
      self.bound = [0, self.screen.winfo_width(), 0, self.screen.winfo_height()]  #[LRTB]
      self.rockets = Population(self.screen, int(self.pop_size_var.get()))

   def update_window(self):
      #Updates screen & gets user input & manages population size

      self.root.update()
      self.gravity = [self.gravity_var.get(), 1/2 * math.pi]
      self.rockets.mutation_rate = self.mutation_var.get()
      self.rockets.size = int(self.pop_size_var.get())
      self.frame_time = self.frame_time_var.get()


      if len(self.rockets.members) < self.rockets.size:
         self.rockets.members.append(self.rockets.generate_new_member())

   def move_target(self, event):
      #Event based function changes coordinates of target & marker when mouse is clicked

      x,y = event.x, event.y
      self.target = [x,y]
      self.screen.coords(self.target_marker, x-2, y-2, x+2, y+2)

   def check_position(self, rocket):
      #Calculates rockets distance from target
      #  Updates its closest distance if necessary
      #Checks to see if rocket is outside bounds
      #  removes rocket from population if out of bounds (death) 

      rocket.distance = compute_distance(self.target, rocket.pos)
      
      if rocket.distance < rocket.closest[0]:
         rocket.closest[0] = rocket.distance

      if (rocket.pos[0] > self.bound[1] or rocket.pos[0] < self.bound[0] or 
          rocket.pos[1] < self.bound[2] or rocket.pos[1] > self.bound[3] or 
          rocket.gene_index == rocket.lifespan-1):
         self.rockets.members.remove(rocket)
         self.screen.delete(rocket.ID)

   def apply_forces(self, rocket):
      #Applies forces to rocket: gravity & 3 thrusters
      bottom = [rocket.genes["bottom_engine"][rocket.gene_index], (3/2 * math.pi)]
      left   = [rocket.genes["left_engine"][rocket.gene_index], 0]
      right  = [rocket.genes["right_engine"][rocket.gene_index], math.pi]
      rocket.vel = add_vectors(rocket.vel, self.gravity, bottom, left, right)

   def step(self, frame_time):
      #Steps through 1 "frame" of simulation

      self.update_window()
      self.update_rockets()
      time.sleep(frame_time)

   def update_rockets(self):        
      #Updates information for each rocket & finds fittest member

      fittest = self.rockets.members[0]
      for rocket in self.rockets.members:
         if rocket.fitness > fittest.fitness:
            fittest = rocket

         self.check_position(rocket)
         eval_fitness(rocket)
         self.apply_forces(rocket)
         rocket.update()

      self.screen.itemconfig(fittest.ID, fill = "#AA0000")
      self.root.update()

   def reset_pressed(self):
      #Erases rockets currently on screen & generates a new population

      for member in self.rockets.members:
         self.screen.delete(member.ID)

      self.rockets = Population(self.screen, int(self.pop_size_var.get()))      


class Population:
   def __init__(self, screen, size):
      self.screen = screen
      self.mutation_rate = 0.08
      self.size = size
      self.members = [Rocket(self.screen) for i in range(self.size)]

   def calc_probability(self):
      #Calculates the-probability-of-being-chosen for all members of population
      #(member fitness) / (fitness of entire population)

      total = 0
      for member in self.members:
         total += member.fitness

      for member in self.members:
         member.probability = member.fitness / total

   def select_member(self):
      #Returns a member chosen based on its probability

      self.calc_probability()
      r = round(random.random(), 5)
      index = 0
      while r > 0:
         r -= round(self.members[index].probability, 5)
         index += 1

      return self.members[index - 1]

   def generate_new_member(self):
      #generates a "child" with the genes of two parents

      parent1 = self.select_member()
      parent2 = self.select_member()
      child = Rocket(self.screen)
      
      for key in child.genes:
         for i in range(min(len(child.genes[key]), len(parent1.genes[key]), len(parent2.genes[key]))):
            if i%2 == 0:
               child.genes[key][i] = parent1.genes[key][i]
            else:
               child.genes[key][i] = parent2.genes[key][i]

      #Mutation:
      chance = random.random()
      if chance <= self.mutation_rate:
         for i in range(50):
            index = random.randint(0, len(child.genes["left_engine"]) - 1)
            mutation = random.random()
            child.genes[random.choice(list(child.genes.keys()))][index] = mutation

      return child


class Rocket:
   def __init__(self, screen):
      self.screen = screen
      self.gene_index = 0
      self.fitness = 0
      self.probability = .003
      self.pos = [250,590]       #[x,y]
      self.vel = [0,0]           #[mag, dir]
      self.distance = 10000
      self.closest  = [10000, 0] #[distance, frame]
      self.lifespan = 500
      self.size = 5
      self.color = "#553355"
      self.ID = screen.create_rectangle(self.pos[0], self.pos[1], (self.pos[0] + self.size), (self.pos[1] + self.size), fill = self.color)
      self.genes = {"bottom_engine" : [random.random() for i in range(self.lifespan)],
                    "left_engine"   : [random.random() for i in range(self.lifespan)],
                    "right_engine"  : [random.random() for i in range(self.lifespan)]}

   def update(self):
      #Updates attributes of rocket on screen

      self.move()
      self.gene_index += 1

   def move(self):  
      #Updates rocket's position on screen

      self.pos[0] += math.cos(self.vel[1]) * self.vel[0]
      self.pos[1] += math.sin(self.vel[1]) * self.vel[0]

      self.screen.coords(self.ID, self.pos[0], self.pos[1], (self.pos[0] + self.size), (self.pos[1] + self.size))





window = Window()

while True:
   window.step(window.frame_time)

