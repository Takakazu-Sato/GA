import math
import random
import matplotlib.pyplot as plt


random.seed(5)

class City:
   def __init__(self, x=None, y=None):
      self.x = None
      self.y = None
      if x is not None:
         self.x = x
      else:
         self.x = int(random.random() * 200)
      if y is not None:
         self.y = y
      else:
         self.y = int(random.random() * 200)
   
   def getX(self):
      return self.x
   
   def getY(self):
      return self.y
   
   def distanceTo(self, city):
      xDistance = abs(self.getX() - city.getX())
      yDistance = abs(self.getY() - city.getY())
      distance = math.sqrt( (xDistance*xDistance) + (yDistance*yDistance) )
      return distance
   
   def __repr__(self):
      return str(self.getX()) + ", " + str(self.getY())


class TourManager:
   destinationCities = []
   
   def addCity(self, city):
      self.destinationCities.append(city)
   
   def getCity(self, index):
      return self.destinationCities[index]
   
   def numberOfCities(self):
      return len(self.destinationCities)


class Tour:
   def __init__(self, tourmanager, tour=None):
      self.tourmanager = tourmanager
      self.tour = []
      self.fitness = 0.0
      self.distance = 0
      if tour is not None:
         self.tour = tour
      else:
         for i in range(0, self.tourmanager.numberOfCities()):
            self.tour.append(None)
   
   def __len__(self):
      return len(self.tour)
   
   def __getitem__(self, index):
      return self.tour[index]
   
   def __setitem__(self, key, value):
      self.tour[key] = value
   
   def __repr__(self):
      geneString = "|"
      for i in range(0, self.tourSize()):
         geneString += str(self.getCity(i)) + "|"
      return geneString
   
   def generateIndividual(self):
      for cityIndex in range(0, self.tourmanager.numberOfCities()):
         self.setCity(cityIndex, self.tourmanager.getCity(cityIndex))
      random.shuffle(self.tour)
   
   def getCity(self, tourPosition):
      return self.tour[tourPosition]
   
   def setCity(self, tourPosition, city):
      self.tour[tourPosition] = city
      self.fitness = 0.0
      self.distance = 0
   
   def getFitness(self):
      if self.fitness == 0:
         self.fitness = 1/float(self.getDistance())
      return self.fitness
   
   def getDistance(self):
      if self.distance == 0:
         tourDistance = 0
         for cityIndex in range(0, self.tourSize()):
            fromCity = self.getCity(cityIndex)
            destinationCity = None
            if cityIndex+1 < self.tourSize():
               destinationCity = self.getCity(cityIndex+1)
            else:
               destinationCity = self.getCity(0)
            tourDistance += fromCity.distanceTo(destinationCity)
         self.distance = tourDistance
      return self.distance
   
   def tourSize(self):
      return len(self.tour)
   
   def containsCity(self, city):
      return city in self.tour


 #人口
class Population:
   def __init__(self, tourmanager, populationSize, initialise):
      self.tours = []
      for i in range(0, populationSize):
         self.tours.append(None)
      
      if initialise:
         for i in range(0, populationSize):
            newTour = Tour(tourmanager)
            newTour.generateIndividual()
            self.saveTour(i, newTour)
      
   def __setitem__(self, key, value):
      self.tours[key] = value
   
   def __getitem__(self, index):
      return self.tours[index]
   
   def saveTour(self, index, tour):
      self.tours[index] = tour
   
   def getTour(self, index):
      return self.tours[index]
   
   def getFittest(self):
      fittest = self.tours[0]
      for i in range(0, self.populationSize()):
         if fittest.getFitness() <= self.getTour(i).getFitness():
            fittest = self.getTour(i)
      return fittest
   
   def populationSize(self):
      return len(self.tours)


class GA:
   def __init__(self, tourmanager):
      self.tourmanager = tourmanager
      self.mutationRate = 0.015
      self.tournamentSize = 5
      self.elitism = True
   
   def evolvePopulation(self, pop):
      newPopulation = Population(self.tourmanager, pop.populationSize(), False)
      elitismOffset = 0
      if self.elitism:
         newPopulation.saveTour(0, pop.getFittest())
         elitismOffset = 1
      
      for i in range(elitismOffset, newPopulation.populationSize()):
         parent1 = self.tournamentSelection(pop)
         parent2 = self.tournamentSelection(pop)
         child = self.crossover(parent1, parent2)
         newPopulation.saveTour(i, child)
      
      for i in range(elitismOffset, newPopulation.populationSize()):
         self.mutate(newPopulation.getTour(i))
      
      return newPopulation
   
   def crossover(self, parent1, parent2):
      child = Tour(self.tourmanager)
      
      startPos = int(random.random() * parent1.tourSize())
      endPos = int(random.random() * parent1.tourSize())
      
      for i in range(0, child.tourSize()):
         if startPos < endPos and i > startPos and i < endPos:
            child.setCity(i, parent1.getCity(i))
         elif startPos > endPos:
            if not (i < startPos and i > endPos):
               child.setCity(i, parent1.getCity(i))
      
      for i in range(0, parent2.tourSize()):
         if not child.containsCity(parent2.getCity(i)):
            for ii in range(0, child.tourSize()):
               if child.getCity(ii) == None:
                  child.setCity(ii, parent2.getCity(i))
                  break
      
      return child
   
   def mutate(self, tour):
      for tourPos1 in range(0, tour.tourSize()):
         if random.random() < self.mutationRate:
            tourPos2 = int(tour.tourSize() * random.random())
            
            city1 = tour.getCity(tourPos1)
            city2 = tour.getCity(tourPos2)
            
            tour.setCity(tourPos2, city1)
            tour.setCity(tourPos1, city2)
   
   def tournamentSelection(self, pop):
      tournament = Population(self.tourmanager, self.tournamentSize, False)
      for i in range(0, self.tournamentSize):
         randomId = int(random.random() * pop.populationSize())
         tournament.saveTour(i, pop.getTour(randomId))
      fittest = tournament.getFittest()
      return fittest



if __name__ == '__main__':
   
   tourmanager = TourManager()
   x_list = []
   y_list = []
   
   # Create and add our cities
   city = City(1150, 1760)
   tourmanager.addCity(city)
   #x_list.append(1150)
   #y_list.append(1760)

   city2 = City(630, 1660)
   tourmanager.addCity(city2)
   #x_list.append(630)
   #y_list.append(1660)

   city3 = City(40, 2090)
   tourmanager.addCity(city3)
   #x_list.append(40)
   #y_list.append(2090)

   city4 = City(750, 1100)
   tourmanager.addCity(city4)
   #x_list.append(750)
   #y_list.append(1100)

   city5 = City(750, 2030)
   tourmanager.addCity(city5)
   #x_list.append(750)
   #y_list.append(2030)

   city6 = City(1030, 2070)
   tourmanager.addCity(city6)
   #x_list.append(1030)
   #y_list.append(2070)

   city7 = City(1650, 650)
   tourmanager.addCity(city7)
   #x_list.append(1650)
   #y_list.append(650)

   city8 = City(1490, 1630)
   tourmanager.addCity(city8)
   #x_list.append(1490)
   #y_list.append(1630)

   city9 = City(790, 2260)
   tourmanager.addCity(city9)
   #x_list.append(790)
   #y_list.append(2260)

   city10 = City(710, 1310)
   tourmanager.addCity(city10)
   #x_list.append(710)
   #y_list.append(1310)

   city11 = City(840, 550)
   tourmanager.addCity(city11)
   #x_list.append(840)
   #y_list.append(550)

   city12 = City(1170, 2300)
   tourmanager.addCity(city12)
   #x_list.append(1170)
   #y_list.append(2300)

   city13 = City(970, 1340)
   tourmanager.addCity(city13)
   #x_list.append(970)
   #y_list.append(1340)

   city14 = City(510, 700)
   tourmanager.addCity(city14)
   #x_list.append(510)
   #y_list.append(700)

   city15 = City(750, 900)
   tourmanager.addCity(city15)
   #x_list.append(750)
   #y_list.append(900)

   city16 = City(1280, 1200)
   tourmanager.addCity(city16)
   #x_list.append(1280)
   #y_list.append(1200)

   city17 = City(230, 590)
   tourmanager.addCity(city17)
   #x_list.append(230)
   #y_list.append(590)

   city18 = City(460, 860)
   tourmanager.addCity(city18)
   #x_list.append(460)
   #y_list.append(860)

   city19 = City(1040, 950)
   tourmanager.addCity(city19)
   #x_list.append(1040)
   #y_list.append(950)

   city20 = City(590, 1390)
   tourmanager.addCity(city20)
   #x_list.append(590)
   #y_list.append(1390)

   city21 = City(830, 1770)
   tourmanager.addCity(city21)
   #x_list.append(830)
   #y_list.append(1770)

   city22 = City(490, 500)
   tourmanager.addCity(city22)
   #x_list.append(490)
   #y_list.append(500)

   city23 = City(1840, 1240)
   tourmanager.addCity(city23)
   #x_list.append(1840)
   #y_list.append(1240)

   city24 = City(1260, 1500)
   tourmanager.addCity(city24)
   #x_list.append(1260)
   #y_list.append(1500)

   city25 = City(1280, 790)
   tourmanager.addCity(city25)
   #x_list.append(1280)
   #y_list.append(790)

   city26 = City(490, 2130)
   tourmanager.addCity(city26)
   #x_list.append(490)
   #y_list.append(2130)

   city27 = City(1460, 1420)
   tourmanager.addCity(city27)
   #x_list.append(1460)
   #y_list.append(1420)

   city28 = City(1260, 1910)
   tourmanager.addCity(city28)
   #x_list.append(1260)
   #y_list.append(1910)

   city29 = City(360, 1980)
   tourmanager.addCity(city29)
   #x_list.append(360)
   #y_list.append(1980)
   
   
   pop = Population(tourmanager, 1000, True);
   print ("Initial distance: " + str(pop.getFittest().getDistance()))
   
   
   ga = GA(tourmanager)
   pop = ga.evolvePopulation(pop)
   for i in range(0, 100):
      pop = ga.evolvePopulation(pop)
   
   # Print final results
   print ("Finished")
   print ("Final distance: " + str(pop.getFittest().getDistance()))
   print ("Solution:")

   print(pop.getFittest())
   
   x_list.append(1170)
   x_list.append(1030)
   x_list.append(1260)
   x_list.append(1150)
   x_list.append(1260)
   x_list.append(970)
   x_list.append(1280)
   x_list.append(1460)
   x_list.append(1490)
   x_list.append(1840)
   x_list.append(1650)
   x_list.append(1280)
   x_list.append(1040)
   x_list.append(840)
   x_list.append(490)
   x_list.append(230)
   x_list.append(510)
   x_list.append(460)
   x_list.append(750)
   x_list.append(750)
   x_list.append(710)
   x_list.append(590)
   x_list.append(630)
   x_list.append(830)
   x_list.append(750)
   x_list.append(360)
   x_list.append(40)
   x_list.append(490)
   x_list.append(790)

   y_list.append(2300)
   y_list.append(2070)
   y_list.append(1910)
   y_list.append(1760)
   y_list.append(1500)
   y_list.append(1340)
   y_list.append(1200)
   y_list.append(1420)
   y_list.append(1630)
   y_list.append(1240)
   y_list.append(650)
   y_list.append(790)
   y_list.append(950)
   y_list.append(550)
   y_list.append(500)
   y_list.append(590)
   y_list.append(700)
   y_list.append(860)
   y_list.append(900)
   y_list.append(1100)
   y_list.append(1310)
   y_list.append(1390)
   y_list.append(1660)
   y_list.append(1770)
   y_list.append(2030)
   y_list.append(1980)
   y_list.append(2090)
   y_list.append(2130)
   y_list.append(2260)


   fig,ax = plt.subplots()
   data_name=['12','6','28','1','24','13','16','27','8','23','7','25','19','11','22','17','14','18','15','4','10','20','2','21','5','29','3','26','9']
   ax.scatter(x_list,y_list)
   plt.plot(x_list,y_list)
   for i,j,k in zip(x_list,y_list,data_name):
        ax.annotate(k,(i,j))
   plt.show()