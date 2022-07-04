import sys

#CONSTANTES
DEBUG = True

MAX_SAMPLES = 3
MAX_MOLS = 10

CLOUD_ID = -1
MYROBOT_ID = 0
ENNEMYROBOT_ID = 1

STEP_YELLOW = 6
STEP_RED = 12

#DEBUG
def debug(*args):
    if (DEBUG):
        print(args, file
              =sys.stderr)  

#PRINTS
def goto_diagnosis():
    print("GOTO DIAGNOSIS")

def goto_molecules():
    print("GOTO MOLECULES")

def goto_laboratory():
    print("GOTO LABORATORY")

def goto_samples():
    print("GOTO SAMPLES")

def goto_wait():
    print("WAIT")

    
#GENERAL FUNCTIONS
#Somme les valeurs de deux dictionnaires et ordonne en fonction des keys
def sum_two_dicts(x,y):

    #fait la somme des dict mais pas ordonné (par exemple renvoie pas de manière propre => A B C D E)
    sum_dic = {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}
    
    #ordonne en fonction des keys
    ord_dic = dict(sorted(sum_dic.items(),key = lambda x:x[0]))

    return ord_dic


#CLASSES TO STORE INPUTS
class Robot():

    def __init__(self, values):
        self.target = values[0]
        self.eta = int(values[1])
        self.score = int(values[2])
        self.storage_a = int(values[3])
        self.storage_b = int(values[4])
        self.storage_c = int(values[5])
        self.storage_d = int(values[6])
        self.storage_e = int(values[7])
        self.expertise_a = int(values[8])
        self.expertise_b = int(values[9])
        self.expertise_c = int(values[10])
        self.expertise_d = int(values[11])
        self.expertise_e = int(values[12])

    def get_storage(self):
        return {'A': self.storage_a, 'B': self.storage_b, 'C': self.storage_c, 'D': self.storage_d, 'E': self.storage_e}

    def get_storage_count(self):
        return self.storage_a + self.storage_b + self.storage_c + self.storage_d + self.storage_e
        
    def get_expertise(self):
        return {'A': self.expertise_a, 'B': self.expertise_b, 'C': self.expertise_c, 'D': self.expertise_d, 'E': self.expertise_e}

    def get_expertise_count(self):
        return self.expertise_a + self.expertise_b + self.expertise_c + self.expertise_d + self.expertise_e
    
    # Somme de Storage + Expertise
    def get_capacity(self):
        return sum_two_dicts(self.get_storage(), self.get_expertise())


class Sample():

    def __init__(self, values):
        self.sample_id = int(values[0])
        self.carried_by = int(values[1])
        self.rank = int(values[2])
        self.expertise_gain = values[3]
        self.health = int(values[4])
        self.cost_a = int(values[5])
        self.cost_b = int(values[6])
        self.cost_c = int(values[7])
        self.cost_d = int(values[8])
        self.cost_e = int(values[9]) 
        
    def get_cost(self):
        return {'A': self.cost_a, 'B': self.cost_b, 'C': self.cost_c, 'D': self.cost_d, 'E': self.cost_e}

    def get_cost_count(self):
        return self.cost_a + self.cost_b + self.cost_c + self.cost_d + self.cost_e


#GET INPUTS
# Rècupère une fois les inputs des projets
def get_data_projects():
    project_count = int(input())
    projects = []
    for i in range(project_count):
        a, b, c, d, e = [int(j) for j in input().split()]
        projects.append([a, b, c, d, e])
    return projects
    
projects = get_data_projects() # trouver un moyen plus propre d'envoyer la variable projects ? 

#Récupère les inputs du jeu
def get_data():
    myRobot = None
    ennemyRobot = None

    # ROBOTS
    for i in range(2):
        if i == MYROBOT_ID:
            myRobot = Robot(input().split())
        if i == ENNEMYROBOT_ID:
            ennemyRobot = Robot(input().split())

    # AVAILABLE
    available_mols = [int(i) for i in input().split()]

    # SAMPLES
    samples = []
    sample_count = int(input())
    for i in range(sample_count):
        sample = Sample(input().split())
        samples.append(sample)

    return myRobot, samples, available_mols, projects, ennemyRobot


############################## STATE - Classe parent ##############################

class State(object):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot, n):
        self.myRobot = myRobot
        self.samples = samples
        self.availables_mols = available_mols
        self.projects = projects
        self.ennemyRobot = ennemyRobot
        self.n = n
        
        #VARIABLES CREEES
        # myRobot_samples = self._get_player_samples(MYROBOT_ID)

        #GET BEST SAMPLE BY HEALTH, 3+2+1 => 1+2 => 2+3 => 1 => 2 => 3 for example
        # self._get_most_health_sample()


        self.needs = self.get_needs()
        self.ordered_needs = self.get_needs_sorted_by_sum_needs()

        self.samples_avail = self.get_samples_avail()
        self.samples_to_diag = self.get_samples_to_diag()
        self.samples_id_doable = self.get_samples_id_doable()
        self.samples_doable = self.get_samples_doable()
        self.samples_id_ready = self.get_samples_id_ready()

        #NOT TAKING WHAT I CARRY INTO ACCOUNT
        self.first_sample_full_needs = self.get_sample_full_needs(1)
        self.second_sample_full_needs = self.get_sample_full_needs(2)
        self.third_sample_full_needs = self.get_sample_full_needs(3)

        #TAKING WHAT I CARRY INTO ACCOUNT
        self.first_sample_left_needs = self.get_sample_left_needs(1)
        self.second_sample_left_needs = self.get_sample_left_needs(2)
        self.third_sample_left_needs = self.get_sample_left_needs(3)
        self.second_and_first_samples_needs = self.get_second_and_first_samples_needs()
        self.all_samples_needs = self.get_all_samples_needs()

        #DEBUGS
        debug("tour:",n)
        debug("s1",self.first_sample_left_needs)
        debug("s1+2",self.second_and_first_samples_needs)
        debug("s1+2+3",self.all_samples_needs)
        debug("myRobot_capacity",self.myRobot.get_capacity())

    #Général
    def _get_player_samples(self, player_id):
        return [x for x in self.samples if x.carried_by == player_id]

    def get_samples_avail(self):
        return sorted((s for s in self.samples if s.carried_by <= 0),
                      key=lambda s: s.health)

    def get_needs(self):
        needs = {}
        s_carried = self._get_player_samples(MYROBOT_ID)
        if s_carried != []:
            for s in s_carried :
                if s.health != -1:
                    A = max(0,s.cost_a - self.myRobot.expertise_a - self.myRobot.storage_a)
                    B = max(0,s.cost_b - self.myRobot.expertise_b - self.myRobot.storage_b)
                    C = max(0,s.cost_c - self.myRobot.expertise_c - self.myRobot.storage_c)
                    D = max(0,s.cost_d - self.myRobot.expertise_d - self.myRobot.storage_d)
                    E = max(0,s.cost_e - self.myRobot.expertise_e - self.myRobot.storage_e)
                    needs[s.sample_id] = [A,B,C,D,E]
        marklist = sorted(needs.items(), key=lambda x:x[0])
        needs = dict(marklist)
        return needs 

    def get_needs_sorted_by_sum_needs(self):
        ordered_needs = {}
        sample_list=list(self.needs.items())
        length = len(sample_list)
        for i in range(length):
            for j in range(i+1,length):
                if sum(sample_list[i][1])>sum(sample_list[j][1]):
                    t=sample_list[i]
                    sample_list[i]=sample_list[j]
                    sample_list[j]=t
            ordered_needs=dict(sample_list)
        return ordered_needs

    def get_second_and_first_samples_needs(self):
        needs = [x + y for x, y in zip(self.second_sample_full_needs, self.first_sample_full_needs)]
        expertise = list(self.myRobot.get_expertise().values())
        carry = list(self.myRobot.get_storage().values())
        res = [max(0,int(x-e-y)) for x, y, e in zip(needs, expertise, carry)]
        return res

    def get_all_samples_needs(self):
        needs = [x + y + z for x, y,z in zip(self.first_sample_full_needs, self.second_sample_full_needs, self.third_sample_full_needs)]
        expertise = list(self.myRobot.get_expertise().values())
        carry = list(self.myRobot.get_storage().values())
        res = [max(0,int(x-e-y)) for x, y, e in zip(needs, expertise, carry)]
        return res

    def get_sample_left_needs(self, number):
        k = list(self.ordered_needs.keys())
        l = list(self.ordered_needs.values())
        try :
            sample_id = k[number-1]
            sample_needs = l[number-1]
            
            return sample_needs
        except:
            return []
        
    def get_sample_full_needs(self, number):
        k = list(self.ordered_needs.keys())
        try :
            sample_id = k[number-1]
            res = self.get_needs_from_sample_id(sample_id)
            return res
        except :
            return []

    def get_needs_from_sample_id(self,id):
        res = []
        for s in self.samples:
            if s.sample_id == id:
                res = [s.cost_a,s.cost_b,s.cost_c,s.cost_d,s.cost_e]
        return res

    def get_needs_of_a_sample(self,id):
        return self.needs.get(id)

    #DIAG
    def all_samples_are_diagnosised(self):
        is_diag = all(s.health >= 0 for s in self.samples_avail)
        return is_diag

    def get_samples_to_diag(self):
        return [s for s in self.samples_avail if s.health == -1]

    #MOLS 
    def get_samples_id_doable(self):
        samples_id_doable = []
        for key, value in self.needs.items():
            dif = list(map(int.__sub__, self.availables_mols, value))
            sum_needs_of_this_sample = sum(value)
            number_of_mols_i_can_take = MAX_MOLS - self.myRobot.get_storage_count()
            dif_mols_left = number_of_mols_i_can_take - sum_needs_of_this_sample
            neg_nos = [num for num in dif if num < 0]
            if neg_nos == [] and dif_mols_left >= 0 :
                samples_id_doable.append(key)
        return samples_id_doable

    def get_samples_doable(self):
        samples_doable = [s for s in self.samples_avail if s.sample_id in self.samples_id_doable]
        return samples_doable

    def get_lowest_needs_sample_id(self):
        mini = 1000000 
        id = None
        for key, value in self.needs.items():
            if key in self.samples_id_doable:
                r = 0
                for x in value :
                    r += x
                if r < mini :
                    mini = r
                    id = key
        return id

    def get_lowest_needs_sample(self):
        lowest_needs_sample = [s for s in self.samples_avail if s.sample_id == self.lowest_needs_sample_id]
        if lowest_needs_sample == []:
            return None
        return lowest_needs_sample[0]
    def is_first_sample_doable(self):
        sum_mols = int(sum(self.first_sample_left_needs))
        if sum_mols == 0 :
            return False

        dif = [int(x) - int(y) for (x,y) in zip(self.availables_mols,self.first_sample_left_needs)]
        
        for x in dif:
            if x < 0 :
                return False
        mols_to_get = self.myRobot.get_storage_count() + sum_mols
        return mols_to_get <= MAX_MOLS

    def is_second_sample_doable(self):
        sum_mols = int(sum(self.second_and_first_samples_needs))
        if sum_mols == 0 :
            return False
        dif = [int(x) - int(y) for (x,y) in zip(self.availables_mols,self.second_and_first_samples_needs)]
        
        for x in dif:
            if x < 0 :
                return False
        mols_to_get = self.myRobot.get_storage_count() + sum_mols
        if mols_to_get <= MAX_MOLS:
            return True
        else : 
            return False

    def is_third_sample_doable(self):
        sum_mols = int(sum(self.all_samples_needs))
        if sum_mols == 0 :
            return False
        dif = [int(x) - int(y) for (x,y) in zip(self.availables_mols,self.all_samples_needs)]
        for x in dif:
            if x < 0 :
                return False
        mols_to_get = self.myRobot.get_storage_count() + sum_mols
        if mols_to_get <= MAX_MOLS:
            return True
        else : 
            return False

    def is_first_sample_done(self):
        if self.first_sample_left_needs == [0] * 5:
            return True
        else :
            return False

    def is_second_sample_done(self):
        if self.second_and_first_samples_needs == [0] * 5:
            return True
        else :
            return False

    def is_third_sample_done(self):
        if self.all_samples_needs == [0] * 5:
            return True
        else :
            return False

    #LABO
    def get_samples_id_ready(self):
        empty_needs = [0]*5
        sample_ids = [key for key, value in self.needs.items() if value == empty_needs]
        return sample_ids


############################## STATES ##############################

############################## SAMPLES ##############################

class Samples(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot, n):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot, n)
        self.action()

    def action(self):

        #au premier tour, prendre que 2 samples maxi
        reduction_samples = 0
        if (self.n < 8):
            reduction_samples = 1 

        if (len(self._get_player_samples(MYROBOT_ID)) < MAX_SAMPLES - reduction_samples):
            self.take_sample()
        else:
            goto_diagnosis()

    def take_sample(self):

        r = 2
        s = len(self._get_player_samples(MYROBOT_ID))
        e = self.myRobot.get_expertise_count()
        n = self.n

        #######################


        if self.myRobot.get_expertise_count() <= STEP_YELLOW :
            r = 1
        elif self.myRobot.get_expertise_count() >= STEP_YELLOW and self.myRobot.get_expertise_count() < STEP_RED :
            r = 2
        elif self.myRobot.get_expertise_count() >= STEP_RED :
            r = 3

        #######################

        # ranks = [1, 1, 1]
        # ranks = [2, 1, 1]
        # ranks = [2, 2, 1]
        # ranks = [2, 2, 2]
        # ranks = [3, 2, 2]
        # ranks = [3, 3, 2]
        # ranks = [3, 3, 3]


        #######################

        # if s == 0:
        #     r = 3
        # elif s == 1:
        #     r = 2
        # elif s == 2:
        #     r = 1



        #######################

        # if n < 30:
        #     if s == 0:
        #         r = 1
        #     elif s == 1:
        #         r = 1
        #     elif s == 2:
        #         r = 1

        # if n > 30:
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 1


        #######################

        # if e < 3:
        #     if s == 0:
        #         r = 1
        #     elif s == 1:
        #         r = 1
        #     elif s == 2:
        #         r = 1

        # if e < 6 and e >= 3:
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 1
        #     elif s == 2:
        #         r = 1

        # if e < 9 and e >= 6:
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 1

        # if e < 12 and e >= 9:
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 2

        # if e < 15 and e >= 12:
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 2

        # if e < 18 and e >= 15:
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 3
        #     elif s == 2:
        #         r = 2

        # if e < 21 and e >= 18:
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 3
        #     elif s == 2:
        #         r = 3        


        ################################

        # if n < 25 and n > 0 :
        #     if s == 0:
        #         r = 1
        #     elif s == 1:
        #         r = 1
        #     elif s == 2:
        #         r = 1

        # if n < 50 and n > 25 :
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 1
        #     elif s == 2:
        #         r = 1

        # if n < 75 and n > 50 :
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 1

        # if n < 100 and n > 75 :
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 2

        # if n < 125 and n > 100 :
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 2

        # if n < 150 and n > 125 :
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 3
        #     elif s == 2:
        #         r = 2

        # if n > 150 :
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 3
        #     elif s == 2:
        #         r = 3

        ###################

        # if n < 50 and n > 0 :
        #     if s == 0:
        #         r = 1
        #     elif s == 1:
        #         r = 1
        #     elif s == 2:
        #         r = 1 

        # if n < 100 and n > 50 :
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 1
        #     elif s == 2:
        #         r = 1
                
        # if n < 150 and n > 100 :
        #     if s == 0:
        #         r = 2
        #     elif s == 1:
        #         r = 2
        #     elif s == 2:
        #         r = 2


        # if n > 150 :
        #     if s == 0:
        #         r = 3
        #     elif s == 1:
        #         r = 3
        #     elif s == 2:
        #         r = 3


        #########################


        print("CONNECT", r)


############################## DIAGNOSIS ##############################

class Diagnosis(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot, n):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot, n)
        self.action()

    def action(self):
        if self.all_samples_are_diagnosised():

            if self.are_samples_blocked():
                self.remove_sample()

            elif self.samples_id_doable == []:
                goto_samples()

            else :
                goto_molecules()

        else:
            self.get_diagnosis()

    def are_samples_blocked(self):
        if self.all_samples_are_diagnosised() and self.samples_id_doable == [] and len(self._get_player_samples(MYROBOT_ID)) == 3:
            return True
        else :
            return False

    def remove_sample(self):
        print("CONNECT",self._get_player_samples(MYROBOT_ID)[0].sample_id)

    def get_diagnosis(self):
        print("CONNECT",self.samples_to_diag[0].sample_id)


############################## MOLECULES ##############################

class Molecules(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot, n):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot, n)
        self.action()

    def action(self):
        if self.myRobot.get_storage_count() >= MAX_MOLS :

            if self.is_first_sample_done():
                goto_laboratory()

            else:        
                goto_diagnosis()

        else :

            if self.is_first_sample_doable():
    
                self.get_mol(self.first_sample_left_needs)

            elif self.is_first_sample_done():

                if self.is_second_sample_doable():

                    self.get_mol(self.second_and_first_samples_needs)

                elif self.is_second_sample_done():
                    
                    if self.is_third_sample_doable():

                        self.get_mol(self.all_samples_needs)

                    elif self.is_third_sample_done():
                        goto_laboratory()

                    else :
                        goto_laboratory()
                        # on attend que l'ennemi valide ses samples pour récuperer les molécules
                        # if self.ennemyRobot.target == "LABORATORY":
                        #     goto_wait()
                        # else: 
                        #     goto_laboratory()
                else :
                    goto_laboratory()

                    # on attend que l'ennemi valide ses samples pour récuperer les molécules
                    # if self.ennemyRobot.target == "LABORATORY":
                    #     goto_wait()
                    # else: 
                    #     goto_laboratory()
            else : 
                goto_samples()


    #recupere la mol la moins disponible et permettant de compléter un sample
    def get_mol(self, needs):
        mol = ""
        dif = []
        j = 0
        for i in needs :
            if i == 0 :
                dif.append(100)
                j += 1
            else :
                #comparaison entre mols dispo et besoins pour le sample
                #(expertise deja prise en compte dans les needs du sample)
                dif.append(self.availables_mols[j] - i)
                j += 1
        temp = min(dif)
        pos = [i for i, j in enumerate(dif) if j == temp][0]

        if pos == 0: mol = "A"
        elif pos == 1: mol = "B"
        elif pos == 2: mol = "C"
        elif pos == 3: mol = "D"
        elif pos == 4: mol = "E"
        print("CONNECT", mol)


############################## LABORATORY ##############################

class Laboratory(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot, n):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot, n)
        self.action()

    def action(self):
        if self.samples_id_ready != []:
            self.validate_sample()

        #si le robot a encore au moins 1 sample faisable il va chercher les molecules
        elif len(self._get_player_samples(MYROBOT_ID)) > 0 and self.samples_id_doable != []:
            goto_molecules()

        else:
            goto_samples()

    def validate_sample(self):
        print("CONNECT", self.samples_id_ready[0])


############################## GAME - FINISHED ELEMENT STATE MACHINE ##############################

class Game(object):

    n = 0 #nombre de tours

    def run(self):

        myRobot, samples, available_mols, projects, ennemyRobot = get_data()

        #on ajoute un tour à chaque run
        self.n += 1

        #si le robot est en déplacement entre deux machines, on renvoie rien
        if myRobot.eta > 0:
            State(myRobot, samples, available_mols, projects, ennemyRobot, self.n)
            print('')
            return None

        if myRobot.target == "START_POS":
            State(myRobot, samples, available_mols, projects, ennemyRobot, self.n)
            print("GOTO SAMPLES")

        elif myRobot.target == "SAMPLES":
            Samples(myRobot, samples, available_mols, projects, ennemyRobot, self.n)

        elif myRobot.target == "DIAGNOSIS":
            Diagnosis(myRobot, samples, available_mols, projects, ennemyRobot, self.n)

        elif myRobot.target == "MOLECULES":
            Molecules(myRobot, samples, available_mols, projects, ennemyRobot, self.n)

        elif myRobot.target == "LABORATORY":
            Laboratory(myRobot, samples, available_mols, projects, ennemyRobot, self.n)


# INSTANCIATION
game = Game()
# GAME LOOP 
while True:
    # EXECUTION => Send datas
    game.run()
