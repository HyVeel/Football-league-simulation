import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Ustawienia symulacji
config = {
	"leaguesNum": 5000, # liczba lig do symulacji
	"teamsToGenerate": 16, # liczba drużyn do wygenerowania (ustawić 0 kiedy chcemy zaimportować)
	"leagueToImport": "None", # drużyny z ligi "None" / "Ekstraklasa" / "La Liga" do zaimportowania
	"histogramBinsNum": 25, # liczba klas w histogramie

	"showMatchResults": False, # wyświetlanie w konsoli wyników meczów
	"showLeagueTable": False, # wyświetlanie w konsoli końcowej tabeli ligi
	"showLeagueSummary": False, # wyświetlanie w konsoli podsumowaninia ligi
	"showAllLeaguesSummary": True, # wyświetlenie w konsoli podsumowania wszystkich lig
	"showHistogram": True, # wyświetlenie końcowego histogramu
	"showFitFunction": True, # wyświetlenie w konsoli funkcji dopasowania wraz z parametrami

	"saveDataToFile": True, # zapis danych (goli w ligach) do pliku
	"saveHistogramToFile": True, # zapis histogramu do pliku

	"dataFileName": "goals.txt", # nazwa pliku do zapisu danych
	"histogramFileName": "histogram.png" # nazwa pliku do zapisu histogramu
}

# Drużyny z lig do importu
leaguesToImport = {
	"Ekstraklasa": [
		("Legia Warszawa", 53/90),
		("Raków Częstoch.", 75/90),
		("Pogoń Szczecin", 66/90),
		("Lech Poznań", 69/90),
		("Widzew Łódź", 56/90),
		("Śląsk Wrocław", 44/90),
		("Górnik Zabrze", 45/90),
		("Piast Gliwice", 49/90),
		("Jagiellonia Bi.", 50/90),
		("Zagłębie Lubin", 39/90),
		("Lechia Gdańsk", 38/90),
		("Korona Kielce", 40/90),
		("Wisła Kraków", 38/90),
		("Miedź Legnica", 37/90),
		("ŁKS Łódź", 41/90),
		("Radomiak Radom", 42/90)
	],
	"La Liga": [
		("Real Madryt", 88/90),
		("FC Barcelona", 85/90),
		("Atlético Madryt", 80/90),
		("Real Sociedad", 68/90),
		("Real Betis", 65/90),
		("Villarreal CF", 59/90),
		("Athletic Bilbao", 59/90),
		("Rayo Vallecano", 52/90),
		("Valencia CF", 48/90),
		("Celta Vigo", 47/90),
		("Sevilla FC", 41/90),
		("Getafe CF", 40/90),
		("Almería", 38/90),
		("Osasuna", 37/90),
		("Espanyol Barce.", 36/90),
		("Granada CF", 34/90)
	],
	"None": []
}

class Weather:
	def __init__(self, type="Sunny", temperature=20.0, windSpeed=0):
		self.type = type
		self.temperature = temperature
		self.windSpeed = windSpeed
		self.idealTemperature = 20
		self.idealWind = 0

	@property
	def weatherGoalChance(self):
		weatherGoalChances = {
			"Sunny": 1, # Sunny
			"Cloudy": 0.98, # Cloudy
			"Foggy": 0.9, # Foggy
			"Drizzle": 0.8, # Drizzle
			"Rainy": 0.7, # Rainy
			"Snowy": 0.8, # Snowy
			"Stormy": 0.5 # Stormy
			}

		return weatherGoalChances[self.type]

	@property
	def temperatureGoalChance(self):
		return 1 - abs(self.idealTemperature - self.temperature) / 100

	@property
	def windGoalChance(self):
		return 1 - abs(self.windSpeed - self.idealWind) / 100

	@property
	def goalChance(self):
		return max(self.weatherGoalChance * self.temperatureGoalChance * self.windGoalChance, 0) # min 0

	def __str__(self):
		return f"{self.type}\t{self.temperature}°C\t{self.windSpeed} km/h\t| {self.goalChance:.2f}"

	def generateType(self):
		self.weatherTypes = ["Sunny", "Cloudy", "Foggy", "Drizzle", "Rainy", "Snowy", "Stormy"]
		self.weatherProbabilities = [0.5, 0.25, 0.1, 0.05, 0.05, 0.04, 0.01]
		self.type = np.random.choice(a=self.weatherTypes, p=self.weatherProbabilities)

	def generateTemperature(self):
		mean, stdDev = 15, 10
		self.temperature = round(np.random.normal(mean, stdDev), 1)

	def generateWindSpeed(self):
		lam = 10
		self.windSpeed = round(np.random.exponential(lam))

	def generate(self):
		self.generateType()
		self.generateTemperature()
		self.generateWindSpeed()

class Team:
	def __init__(self, name = "Team", power = 0, matches = 0, wins = 0, draws = 0, losses = 0, goalsFor = 0, goalsAgainst = 0, points = 0):
		self.name = name
		self.power = power
		self.matches = matches
		self.wins = wins
		self.draws = draws
		self.losses = losses
		self.goalsFor = goalsFor
		self.goalsAgainst = goalsAgainst
		self.points = points

	@property
	def goalDifference(self):
		return self.goalsFor - self.goalsAgainst

	@property
	def avgGoals(self):
		return self.goalsFor / self.matches if self.matches > 0 else 0

	def __str__(self):
		return f"{self.name}\t{self.power:.2f}\t{self.matches}|{self.wins}/{self.draws}/{self.losses}\t{self.goalsFor}/{self.goalsAgainst}/{self.goalDifference}|{self.avgGoals:.2f}\t{self.points}"

class Match:
	def __init__(self, home, away, homeGoals=0, awayGoals=0, weather=Weather()):
		self.home = home
		self.away = away
		self.homeGoals = homeGoals
		self.awayGoals = awayGoals
		self.weather = weather

	@property
	def score(self):
		return f"{self.homeGoals}:{self.awayGoals}"

	def __str__(self):
		return f"{self.home.name} [{self.score}] {self.away.name}\t{self.weather}{' !' if self.weather.goalChance <= 0.45 else ' *' if self.weather.goalChance >= 0.95 else ''}"

	def generateWeather(self):
		self.weather.generate()

	def play(self):
		home = self.home
		away = self.away
		weather = self.weather

		home.matches += 1
		away.matches += 1

		# Losowanie liczby goli strzelonych przez każdą drużynę zależne od siły drużyny, kto jest gospodarzem i pogody
		base = 1
		self.homeBonus = 0.1
		self.awayPenalty = -0.05

		homeGoals = np.random.poisson(lam = (base + home.power + self.homeBonus) * weather.goalChance)
		home.goalsFor += homeGoals
		away.goalsAgainst += homeGoals

		awayGoals = np.random.poisson(lam = (base + away.power + self.awayPenalty) * weather.goalChance)
		away.goalsFor += awayGoals
		home.goalsAgainst += awayGoals

		if homeGoals > awayGoals: # drużyna 1 wygrała
			home.wins += 1
			away.losses += 1
			home.points += 3
		elif awayGoals > homeGoals: # drużyna 2 wygrała
			away.wins += 1
			home.losses += 1
			away.points += 3
		else: # remis
			home.draws += 1
			away.draws += 1
			home.points += 1
			away.points += 1

		self.homeGoals = homeGoals
		self.awayGoals = awayGoals

class League:
	def __init__(self, name="League"):
		self.name = name
		self.teams = []
		self.goals = 0
		self.matches = 0

	@property
	def teamsNum(self):
		return len(self.teams)

	@property
	def avgGoalsPerMatch(self):
		return self.goals / self.matches if self.matches > 0 else 0

	@property
	def avgTeamGoalsPerMatch(self):
		return self.avgGoalsPerMatch / 2

	def importTeams(self, teamsList):
		for name, power in teamsList:
			team = Team(name, power)
			self.teams.append(team)

	def generateTeams(self, number):
		startLetter = "A" # startowy prefiks nazw drużyn

		for i in range(number):
			name = "Team " + chr(ord(startLetter) + i)
			power = np.random.uniform(0, 1)

			team = Team(name, power)
			self.teams.append(team)

	def simulate(self):
		if config['showMatchResults']: print(f"\n{self.name} results:")

		# Generowanie listy meczów pomiędzy wszystkimi parami drużyn z rewanżami
		matchesList = [(home, away) for home in self.teams for away in self.teams if home != away]

		for home, away in matchesList:
			match = Match(home, away)
			match.generateWeather()
			match.play()

			if config['showMatchResults']: print(match)

			self.goals += match.homeGoals + match.awayGoals
			self.matches += 1

	def showTable(self, sortBy1="points", sortBy2="goalDifference", desc=True):
		sortedTeams = sorted(self.teams, key=lambda x: (getattr(x, sortBy1, x.points), getattr(x, sortBy2, x.goalDifference)), reverse=desc) # sortowanie po dwóch właściwościach

		print(f"\n{self.name} table:\nPos\tName\tPower\tMP|W/D/L\tGF/GA/GD|Avg\tPts")

		for i in range(self.teamsNum): print(f"{i + 1}.\t{sortedTeams[i]}")

	def showSummary(self):
		print(f"\n{self.name} summary:\nMatches: {self.matches}\nGoals: {self.goals}\nAvg goals/match: {round(self.avgGoalsPerMatch, 2)}\nAvg team goals/match: {round(self.avgTeamGoalsPerMatch, 2)}")

# Funkcja Gaussa
def gaussian(x, a, mean, sigma):
	return a * np.exp(-0.5 * ((x - mean) / sigma) ** 2)

# Tworzy histogram z danych
def createHistogram(data, binsNum, fitFunction, title="", xlabel="", ylabel=""):
	# Tworzy histogram
	count, bins, ignored = plt.hist(data, bins=binsNum)

	# Środki każdej klasy histogramu
	binCenters = (bins[:-1] + bins[1:]) / 2

	# Dopasowanie funkcji
	parameters, covariance = curve_fit(fitFunction, binCenters, count, p0=[1, np.mean(data), np.std(data)])
	parameters = tuple(round(param) for param in parameters) # zaokrąglanie parametrów

	# Wartości dopasowanej funkcji
	x_fit = np.linspace(min(data), max(data), 1000)
	y_fit = fitFunction(x_fit, *parameters)

	# Rysowanie histogramu i dopasowanej funkcji
	plt.plot(x_fit, y_fit, color="red", label=f"{fitFunction.__name__}{parameters}")

	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)

	if config['showFitFunction']:
		plt.legend()
		print(f"\nHistogram fit function: {fitFunction.__name__}{parameters}")

	if config['saveHistogramToFile']:
		plt.savefig(config['histogramFileName'])
		print(f"\nHistogram saved to {config['histogramFileName']}")

	if config['showHistogram']: plt.show()

# Zapisuje dane do pliku
def writeDataToFile(data, fileName):
	file = open(fileName, "w")

	for d in data:
		file.write(f"{d}\n")

	file.close()

# ----------------------------------------- #
# Symulacja wielu lig i zbieranie statystyk #
# ----------------------------------------- #

# Importowanie dużyn z ligi, jeśli wybrano jakąś
importedLeague = leaguesToImport[config["leagueToImport"]]

if config['leaguesNum'] > 0 and config['teamsToGenerate'] + len(importedLeague) >= 2: # min 1 liga i 2 drużyny
	goalsInLeagues = []
	matchesInLeagues = []

	# Symulacja lig
	for i in range(config['leaguesNum']):
		league = League()
		if importedLeague: league.importTeams(importedLeague)
		league.generateTeams(config['teamsToGenerate'])
		league.simulate()

		goalsInLeagues.append(league.goals)
		matchesInLeagues.append(league.matches)

		# Tabela i podsumowanie ligi
		if config['showLeagueTable']: league.showTable()
		if config['showLeagueSummary']: league.showSummary()

	# Podsumowanie wszystkich lig
	if config['showAllLeaguesSummary']:
		allMatchesInLeagues = sum(matchesInLeagues)
		allGoalsInLeagues = sum(goalsInLeagues)
		avgGoalsInLeagues = allGoalsInLeagues / config['leaguesNum']
		minGoalsInLeagues = min(goalsInLeagues)
		maxGoalsInLeagues = max(goalsInLeagues)
		rangeOfGoalsInLeagues = maxGoalsInLeagues - minGoalsInLeagues
		avgGoalsPerMatchInLeagues = allGoalsInLeagues / allMatchesInLeagues if allMatchesInLeagues > 0 else 0
		avgTeamGoalsPerMatchInLeagues = avgGoalsPerMatchInLeagues / 2

		print(f"\nAll ({config['leaguesNum']}) leagues summary:\nMatches: {allMatchesInLeagues}\nGoals: {allGoalsInLeagues}"
		+ f"\nAvg goals/league: {round(avgGoalsInLeagues, 2)}\nMin goals/league: {minGoalsInLeagues}\nMax goals/league: {maxGoalsInLeagues}"
		+ f"\nRange goals/league: {rangeOfGoalsInLeagues}\nAvg goals/match: {round(avgGoalsPerMatchInLeagues, 2)}\nAvg team goals/match: {round(avgTeamGoalsPerMatchInLeagues, 2)}")

	# Zapis danych do pliku
	if config['saveDataToFile']:
		writeDataToFile(goalsInLeagues, config['dataFileName'])

		print(f"\nResults saved to file {config['dataFileName']}")

	# Histogram
	if config['leaguesNum'] > 1 and (config['showHistogram'] or config['saveHistogramToFile']):
		title = f"Goals in {config['leaguesNum']} leagues"
		xlabel = "Goals"
		ylabel = "Count"

		createHistogram(goalsInLeagues, config['histogramBinsNum'], gaussian, title, xlabel, ylabel)
