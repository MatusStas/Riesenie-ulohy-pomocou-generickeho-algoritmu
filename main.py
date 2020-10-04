from random import shuffle, randint
import matplotlib.pyplot as plt
from copy import deepcopy
import time


class Garden:
	def __init__(self):
		self.generate()

	def generate(self):
		self.height,self.width = [int(size) for size in input().split()]
		self.garden = [[0 for column in range(self.width)] for row in range(self.height)]
		self.number_of_rocks = 0
		while True:
			try:
				rock_coordinates = [int(i) for i in input().split()]
				rock_y,rock_x = rock_coordinates
				self.garden[rock_y][rock_x] = 'R'
				self.number_of_rocks += 1
			except (EOFError, ValueError):
				break

	def perimeter(self):
		return self.height+self.width

	def show(self):
		for row in self.garden:
			for column in row:
				print("{:>2} ".format(column),end='')
			print()

	def inside(self,y0,x0):
		if y0 >= 0 and y0 < self.height and x0 >= 0 and x0 < self.width:
			return True
		return False

	def rake(self,chromosome):
		# 		vertical		horizontal
		moves = [[[1,0],[-1,0]],[[0,-1],[0,1]]]
		line = 1
		running = True
		for gene in range(len(chromosome)):
			gene_index = chromosome.index(gene)
			first_direction = 1 if gene_index-self.width > 0 else 0
			second_direction = 0
			# calculating starting positions
			y0 = max(0,gene_index-self.width)
			x0 = min(gene_index,self.width-1)
			while running:
				if self.garden[y0][x0] != 0:
					break
				temp_y0 = y0+moves[first_direction][second_direction][0]
				temp_x0 = x0+moves[first_direction][second_direction][1]
				if self.inside(temp_y0,temp_x0) == False:
					self.garden[y0][x0] = line
					break
				elif self.garden[temp_y0][temp_x0] == 0:
					self.garden[y0][x0] = line
					y0 = temp_y0
					x0 = temp_x0
				else:
					first_direction = abs(first_direction-1)
					possible_moves = []
					for move in moves[first_direction]:
						if self.inside(y0+move[0],x0+move[1]):
							if self.garden[y0+move[0]][x0+move[1]] == 0:
								possible_moves.append(move)
					if len(possible_moves) == 0:
						if y0 == 0 or y0 == self.height-1 or x0 == 0 or x0 == self.width-1:
							break
						else:
							self.garden[y0][x0] = line
							running = False
							break
					else:
						shuffle(possible_moves)
						second_direction = moves[first_direction].index(possible_moves[0])
			line += 1



class Chromosome:
	def __init__(self,garden,generate):
		self.grdn = deepcopy(garden)
		self.fitness = 0
		if generate == True:
			self.generate(self.grdn.perimeter())
		else:
			self.chromosome = generate
		self.get_fitness()

	def generate(self, number_of_genes):
		self.chromosome = [gene for gene in range(number_of_genes)]
		shuffle(self.chromosome)

	def show(self):
		print(self.chromosome)

	def get_fitness(self):
		self.grdn.rake(self.chromosome)
		for row in range(self.grdn.height):
			for column in range(self.grdn.width):
				if self.grdn.garden[row][column] != 0:
					self.fitness += 1
		return self.fitness


class Evolution:
	def __init__(self,garden,number_of_species,elite,new_blood,cross_percentage,mutation_percetange):
		self.number_of_species = number_of_species
		self.elite = elite
		self.new_blood = new_blood
		self.cross_percentage = cross_percentage
		self.mutation_percetange = mutation_percetange
		self.generate_population(garden)

	def generate_population(self,garden):
		self.population = []
		for chromosome in range(self.number_of_species):
			self.population.append(Chromosome(garden,True))
		self.population.sort(key=lambda chromosome: chromosome.fitness,reverse=True)

	def turnaj(self):
		arr = []
		n = int(self.number_of_species*(1-self.new_blood))
		for i in range(n):
			for j in range(n-i):
				arr.append(i)
		shuffle(arr)
		return self.population[arr[0]]

	def ruleta(self):
		arr = []
		n = int(self.number_of_species*(1-self.new_blood))
		for i in range(n):
			for j in range(self.population[i].fitness):
				arr.append(i)
		shuffle(arr)
		return self.population[arr[0]]

	def mutation(self,new_one):
		for i in range(randint(1,3)):
			swap_1 = randint(0,len(new_one)-1)
			swap_2 = randint(0,len(new_one)-1)
			# swapping genes
			new_one[swap_1],new_one[swap_2] = new_one[swap_2],new_one[swap_1]
		return new_one


	def start_evolution(self,garden):
		new_population = []

		# elite
		for i in range(int(self.number_of_species*self.elite)):
			new_population.append(self.population[i])

		# new blood
		for i in range(int(self.number_of_species*self.new_blood)):
			new_population.append(Chromosome(garden,True))

		# 2 parents
		parents = []
		parents.append(self.turnaj())
		parents.append(self.ruleta())

		# crossing
		cross = [[] for i in range(len(parents))]
		s = int(self.number_of_species*self.elite)
		e = int(self.number_of_species*(1-self.new_blood))
		for i in range(s,e):
			cross[i%len(parents)].append(self.population[i])

		for parent in range(len(parents)):
			for child in range(len(cross[parent])):
				percentage = randint(0,100)
				if percentage < self.cross_percentage*100:

					start = len(parents[parent].chromosome)//2
					end = len(parents[parent].chromosome)
					new_one = parents[parent].chromosome[0:start]
					for i in range(start,end):
						if cross[parent][child].chromosome[i] not in new_one:
							new_one.append(cross[parent][child].chromosome[i])
						else:
							new_one.append(parents[parent].chromosome[i])

					miss = []
					for i in range(len(new_one)):
						if i not in new_one:
							miss.append(i)
					chodec = 0
					for i in range(len(new_one)):
						if new_one.count(i) > 1:
							new_one[new_one.index(i)] = miss[chodec]
							chodec += 1

					percentage = randint(0,100)
					if percentage < self.mutation_percetange*100:
						new_one = self.mutation(new_one)

					new_population.append(Chromosome(garden,new_one))						
				else:
					new_population.append(Chromosome(garden,cross[parent][child].chromosome))
		
		new_population.sort(key=lambda x: x.fitness,reverse=True)
		self.population = new_population
		average = 0
		for chromosome in self.population:
			average += chromosome.fitness
		average //= len(self.population)
		return new_population[0],average


def chart(arr_of_best_individuals,arr_of_average):
	plt.plot(arr_of_best_individuals)
	plt.plot(arr_of_average)
	plt.ylabel("fitness")
	plt.xlabel("generation")
	plt.show()


def test():
	garden = Garden()
	
	arr_of_generations = []
	arr_of_death = []
	for i in range(100):
		# ae2
		# evolution = Evolution(garden,20,0.12,0.15,80,15)
		# ae3
		# evolution = Evolution(garden,20,0.05,0.10,70,10)
		# ae4
		# evolution = Evolution(garden,30,0.10,0.15,85,10)
		# ae5
		# evolution = Evolution(garden,30,0.05,0.15,100,10)
		# ae6
		# evolution = Evolution(garden,30,0.1,0.15,90,10)
		# ae7
		# evolution = Evolution(garden,15,0.15,0.15,85,15)
		# ae8
		# evolution = Evolution(garden,50,0.10,0.15,80,7)
		# ae9
		evolution = Evolution(garden,20,0.10,0.15,80,10)

		generation = 0
		while True:
			best_individual = evolution.start_evolution(garden)
			print("{} {:>4} {}".format(i,best_individual.fitness,generation))
			generation += 1
			if best_individual.fitness == garden.height*garden.width:
				arr_of_death.append(1000)
				arr_of_generations.append(generation)
				break
			if generation == 1000:
				arr_of_death.append(1000)
				arr_of_generations.append(generation)
				break
	ave = 0
	for i in arr_of_generations:
		ave += i

	ave = ave//len(arr_of_generations)
	average = [ave for i in range(len(arr_of_generations))]
	print(ave)
	plt.plot(arr_of_generations)
	plt.plot(arr_of_death)
	plt.plot(average)
	plt.show()

if __name__ == '__main__':
	garden = Garden()
	evolution = Evolution(garden,20,0.10,0.10,0.80,0.15)
	arr_of_best_individuals = []	
	arr_of_average = []
	generation = 0
	while True:
		best_individual,average = evolution.start_evolution(garden)
		arr_of_best_individuals.append(best_individual.fitness)
		arr_of_average.append(average)
		print("{:>4} {}".format(best_individual.fitness,generation))
		generation += 1
		if best_individual.fitness == garden.height*garden.width:
			break

	best_individual.grdn.show()
	chart(arr_of_best_individuals,arr_of_average)
	# test()