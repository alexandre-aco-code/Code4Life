import sys


# STATE
class State(object):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot):

        self.myRobot = myRobot
        self.samples = samples
        self.availables_mols = available_mols
        self.projects = projects
        self.ennemyRobot = ennemyRobot

        # DONNEES MODIFIABLES -------------
        self.step_yellow = 8
        self.step_red = 15

        # REGLES DU JEU
        self.rank = 1
        self.max_number_of_samples_to_carry = 3
        self.max_number_of_mols_to_carry = 10

        # VARIABLES CREEES
        self.expertise = self.get_expertise()
        self.number_of_expertise = self.get_sum_expertise()

        self.number_of_samples_carried = self.get_number_of_samples_carried()
        self.number_of_mols_carried = self.get_number_of_mols_carried()
        self.set_needs_attribute()

        self.mols_carried = self.get_carried_mols()
        self.mols_force = self.get_mols_force()
        self.needs = self.get_needs()
        self.ordered_needs = self.get_needs_sorted_by_sum_needs()

        self.samples_avail = self.get_samples_avail()
        self.samples_carried = self.get_samples_carried()
        self.samples_to_diag = self.get_samples_to_diag()
        self.samples_id_doable = self.get_samples_id_doable()
        self.samples_doable = self.get_samples_doable()
        self.samples_id_ready = self.get_samples_id_ready()

        # NOT TAKING WHAT I CARRY INTO ACCOUNT
        self.first_sample_full_needs = self.get_sample_full_needs(1)
        self.second_sample_full_needs = self.get_sample_full_needs(2)
        self.third_sample_full_needs = self.get_sample_full_needs(3)

        # TAKING WHAT I CARRY INTO ACCOUNT
        self.first_sample_left_needs = self.get_sample_left_needs(1)
        self.second_sample_left_needs = self.get_sample_left_needs(2)
        self.third_sample_left_needs = self.get_sample_left_needs(3)

        self.second_and_first_samples_needs = self.get_second_and_first_samples_needs()
        self.all_samples_needs = self.get_all_samples_needs()

        # self.message = ""

        # PRINTS
        # print("------GENERAL INFOS-----",file=sys.stderr)
        # print("samples_id_doable",self.samples_id_doable, file=sys.stderr)
        print("sample1", self.first_sample_left_needs, file=sys.stderr)
        print("samples1+2", self.second_and_first_samples_needs, file=sys.stderr)
        print("samples1+2+3", self.all_samples_needs, file=sys.stderr)
        # print("carried_mols",self.number_of_mols_carried, file=sys.stderr)
        # print("INFOS :", self.message, file=sys.stderr)
        # print("ordered_needs", self.ordered_needs, file=sys.stderr)
        # print("second_sample_left_needs",self.second_sample_left_needs, file=sys.stderr)
        # print("third_sample_left_needs",self.third_sample_left_needs, file=sys.stderr)
        # print("first_sample_full_needs",self.first_sample_full_needs, file=sys.stderr)
        # print("second_sample_full_needs",self.second_sample_full_needs, file=sys.stderr)
        # print("third_sample_full_needs",self.third_sample_full_needs, file=sys.stderr)
        # print("projects", self.projects, file=sys.stderr)
        print("-----------", file=sys.stderr)
        print("avail_mols", self.availables_mols, file=sys.stderr)
        print("expert_mols:", self.expertise, file=sys.stderr)
        print("carried_mols", self.mols_carried, file=sys.stderr)
        # doable = [a+e+c for (a,e,c) in zip(self.availables_mols, self.expertise, self.mols_carried)]
        print("mols_force (a+e+c)", self.mols_force, file=sys.stderr)

        # print("samples_id ready :",self.samples_id_ready, file=sys.stderr)

    # Prints
    def goto_diagnosis(self):
        print("GOTO DIAGNOSIS")

    def goto_molecules(self):
        print("GOTO MOLECULES")

    def goto_laboratory(self):
        print("GOTO LABORATORY")

    def goto_samples(self):
        print("GOTO SAMPLES")

    def wait(self):
        print("WAIT")

    # Général
    def get_samples_avail(self):
        return sorted((s for s in self.samples if s.carried_by <= 0),
                      key=lambda s: s.health)

    def get_samples_carried(self):
        return sorted((s for s in self.samples if s.carried_by == 0),
                      key=lambda s: s.health)

    def get_carried_mols(self):
        mols_carried = [self.myRobot.storage_a, self.myRobot.storage_b, self.myRobot.storage_c, self.myRobot.storage_d,
                        self.myRobot.storage_e]
        return mols_carried

    def get_number_of_mols_carried(self):
        sum_mols = self.myRobot.storage_a + self.myRobot.storage_b + self.myRobot.storage_c + self.myRobot.storage_d + self.myRobot.storage_e
        return int(sum_mols)

    def get_sum_expertise(self):
        sum_expertise = int(
            self.myRobot.expertise_a + self.myRobot.expertise_b + self.myRobot.expertise_c + self.myRobot.expertise_d + self.myRobot.expertise_e)
        return sum_expertise

    def get_needs(self):
        needs = {}
        s_carried = self.get_samples_carried()
        if s_carried != []:
            for s in s_carried:
                if s.health != -1:
                    A = max(0, s.cost_a - self.myRobot.expertise_a - self.myRobot.storage_a)
                    B = max(0, s.cost_b - self.myRobot.expertise_b - self.myRobot.storage_b)
                    C = max(0, s.cost_c - self.myRobot.expertise_c - self.myRobot.storage_c)
                    D = max(0, s.cost_d - self.myRobot.expertise_d - self.myRobot.storage_d)
                    E = max(0, s.cost_e - self.myRobot.expertise_e - self.myRobot.storage_e)
                    needs[s.sample_id] = [A, B, C, D, E]
        marklist = sorted(needs.items(), key=lambda x: x[0])
        needs = dict(marklist)
        return needs

    def get_needs_sorted_by_sum_needs(self):
        ordered_needs = {}
        sample_list = list(self.needs.items())
        length = len(sample_list)
        for i in range(length):
            for j in range(i + 1, length):
                if sum(sample_list[i][1]) > sum(sample_list[j][1]):
                    t = sample_list[i]
                    sample_list[i] = sample_list[j]
                    sample_list[j] = t
            ordered_needs = dict(sample_list)
        return ordered_needs

    def get_expertise(self):
        expertise = [self.myRobot.expertise_a, self.myRobot.expertise_b, self.myRobot.expertise_c,
                     self.myRobot.expertise_d, self.myRobot.expertise_e]
        return expertise

    def get_second_and_first_samples_needs(self):
        needs = [x + y for x, y in zip(self.second_sample_full_needs, self.first_sample_full_needs)]
        expertise = self.get_expertise()
        carry = self.get_carried_mols()
        res = [max(0, int(x - e - y)) for x, y, e in zip(needs, expertise, carry)]
        return res

    def get_all_samples_needs(self):
        needs = [x + y + z for x, y, z in
                 zip(self.first_sample_full_needs, self.second_sample_full_needs, self.third_sample_full_needs)]
        expertise = self.get_expertise()
        carry = self.get_carried_mols()
        res = [max(0, int(x - e - y)) for x, y, e in zip(needs, expertise, carry)]
        return res

    #     sample_id 35
    # sample_needs [0, 2, 1, 0, 0]
    # samples_id_doable [33, 34]
    # sample_id 34
    # sample_needs [0, 0, 5, 0, 0]
    # samples_id_doable [33, 34]
    # sample_needs_OK [0, 0, 5, 0, 0]
    # sample_id 33
    # sample_needs [0, 0, 0, 0, 5]
    # samples_id_doable [33, 34]
    # sample_needs_OK [0, 0, 0, 0, 5]
    # ------GENERAL INFOS-----
    # sample1_needs []
    # samples1+2_needs [0, 2, 8, 0, 0]
    # samples1+2+3_needs [2, 2, 8, 0, 5]
    # carried_mols 1
    # expertise : 14

    def get_sample_left_needs(self, number):
        k = list(self.ordered_needs.keys())
        l = list(self.ordered_needs.values())

        # print("k ", k , file=sys.stderr)
        # print("l", l, file=sys.stderr)
        try:
            sample_id = k[number - 1]
            sample_needs = l[number - 1]

            return sample_needs
        except:
            return []

        # print("sample_id", sample_id, file=sys.stderr)
        # print("sample_needs", sample_needs, file=sys.stderr)
        # print("samples_id_doable", self.samples_id_doable, file=sys.stderr)

        # if sample_id in self.samples_id_doable:
        # print("number", number, file=sys.stderr)
        # print("sample_needs_OK", sample_needs, file=sys.stderr)
        # return sample_needs
        # else :
        # return []
        # except :
        # return []

    def get_sample_full_needs(self, number):
        k = list(self.ordered_needs.keys())
        try:
            sample_id = k[number - 1]
            res = self.get_needs_from_sample_id(sample_id)
            return res
        except:
            return []

    def set_needs_attribute(self):
        for s in self.samples:
            s.needs = [s.cost_a, s.cost_b, s.cost_c, s.cost_d, s.cost_e]

    def get_needs_from_sample_id(self, id):
        res = []
        for s in self.samples:
            if s.sample_id == id:
                res = [s.cost_a, s.cost_b, s.cost_c, s.cost_d, s.cost_e]
        return res

    def get_needs_of_a_sample(self, id):
        return self.needs.get(id)

    # DIAG
    def all_samples_are_diagnosised(self):
        is_diag = all(s.health >= 0 for s in self.samples_avail)
        return is_diag

    def get_samples_to_diag(self):
        return [s for s in self.samples_avail if s.health == -1]

    def get_number_of_samples_carried(self):
        return int(len(self.get_samples_carried()))

    # MOLS
    def get_samples_id_doable(self):
        samples_id_doable = []
        for key, value in self.needs.items():
            dif = list(map(int.__sub__, self.availables_mols, value))
            sum_needs_of_this_sample = sum(value)
            number_of_mols_i_can_take = self.max_number_of_mols_to_carry - self.number_of_mols_carried
            dif_mols_left = number_of_mols_i_can_take - sum_needs_of_this_sample
            neg_nos = [num for num in dif if num < 0]
            if neg_nos == [] and dif_mols_left >= 0:
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
                for x in value:
                    r += x
                if r < mini:
                    mini = r
                    id = key
        return id

    def get_lowest_needs_sample(self):
        lowest_needs_sample = [s for s in self.samples_avail if s.sample_id == self.lowest_needs_sample_id]
        if lowest_needs_sample == []:
            return None
        return lowest_needs_sample[0]

    def is_first_sample_done(self):
        if self.first_sample_left_needs == [0] * 5:
            return True
        else:
            return False

    def is_second_sample_done(self):
        if self.second_and_first_samples_needs == [0] * 5:
            return True
        else:
            return False

    def is_third_sample_done(self):
        if self.all_samples_needs == [0] * 5:
            return True
        else:
            return False

    # LABO
    def get_samples_id_ready(self):
        empty_needs = [0] * 5
        sample_ids = [key for key, value in self.needs.items() if value == empty_needs]
        return sample_ids

    def get_mols_force(self):

        doable = [a + e + c for (a, e, c) in zip(self.availables_mols, self.expertise, self.mols_carried)]
        return doable


############################## STATES ##############################

############################## SAMPLES ##############################

class Samples(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot)
        self.action()

    def action(self):
        if (self.number_of_samples_carried < self.max_number_of_samples_to_carry):
            self.take_sample()
        else:
            self.goto_diagnosis()

    def take_sample(self):

        # if self.number_of_expertise <= self.step_yellow:
        #     self.rank = 1
        # elif self.number_of_expertise >= self.step_yellow and self.number_of_expertise < self.step_red:
        #     self.rank = 2
        # elif self.number_of_expertise >= self.step_red:
        #     self.rank = 3

        num_sam = self.number_of_samples_carried

        if self.number_of_expertise <= self.step_yellow:

            # self.expertise_level = 1

            if num_sam == 0:
                self.rank = 2
            elif num_sam == 1:
                self.rank = 1
            elif num_sam == 2:
                self.rank = 1

        if self.number_of_expertise >= self.step_yellow and self.number_of_expertise < self.step_red:

            # self.expertise_level = 2

            # self.rank = 2
            if num_sam == 0:
                self.rank = 3
            elif num_sam == 1:
                self.rank = 2
            elif num_sam == 2:
                self.rank = 2


        elif self.number_of_expertise >= self.step_red:

            self.expertise_level = 3
            # self.rank = 3

            if num_sam == 0:
                self.rank = 3
            elif num_sam == 1:
                self.rank = 3
            elif num_sam == 2:
                self.rank = 3

        print("CONNECT", self.rank)


############################## DIAGNOSIS ##############################

class Diagnosis(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot)
        self.action()

    def action(self):
        if self.all_samples_are_diagnosised():

            if self.are_samples_blocked():
                self.message = "SAMPLES ARE BLOCKED"
                self.remove_sample()

            elif self.samples_id_doable == []:
                self.goto_samples()

            else:
                self.goto_molecules()

        else:
            self.get_diagnosis()

    def get_diagnosis(self):
        print("CONNECT", self.samples_to_diag[0].sample_id)

    def are_samples_blocked(self):

        if self.all_samples_are_diagnosised() and self.samples_id_doable == [] and self.number_of_samples_carried == 3:
            return True
        else:
            return False

    def remove_sample(self):
        print("CONNECT", self.samples_carried[0].sample_id)


############################## MOLECULES ##############################

class Molecules(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot)
        self.action()

    def action(self):
        if self.number_of_mols_carried >= self.max_number_of_mols_to_carry:
            if self.is_first_sample_done():
                self.goto_laboratory()
            else:
                self.goto_diagnosis()
        else:
            if self.is_first_sample_doable():
                self.get_mol(self.first_sample_left_needs)
            elif self.is_first_sample_done():
                if self.is_second_sample_doable():
                    self.get_mol(self.second_and_first_samples_needs)
                elif self.is_second_sample_done():
                    if self.is_third_sample_doable():
                        self.get_mol(self.all_samples_needs)
                    elif self.is_third_sample_done():
                        self.goto_laboratory()
                    else:
                        self.goto_laboratory()
                else:
                    self.goto_laboratory()
            else:
                self.goto_samples()

    def is_first_sample_doable(self):
        sum_mols = int(sum(self.first_sample_left_needs))
        if sum_mols == 0:
            return False

        dif = [int(x) - int(y) for (x, y) in zip(self.availables_mols, self.first_sample_left_needs)]

        for x in dif:
            if x < 0:
                return False

        mols_to_get = self.number_of_mols_carried + sum_mols

        return mols_to_get <= self.max_number_of_mols_to_carry
        # if mols_to_get <= self.max_number_of_mols_to_carry:
        #     return True
        # else :
        #     return False

    def is_second_sample_doable(self):
        sum_mols = int(sum(self.second_and_first_samples_needs))
        if sum_mols == 0:
            return False
        dif = [int(x) - int(y) for (x, y) in zip(self.availables_mols, self.second_and_first_samples_needs)]

        for x in dif:
            if x < 0:
                # self.message = "second sample NOT POSSIBL"
                return False
        mols_to_get = self.number_of_mols_carried + sum_mols
        if mols_to_get <= self.max_number_of_mols_to_carry:
            return True
        else:
            return False

    def is_third_sample_doable(self):
        sum_mols = int(sum(self.all_samples_needs))
        if sum_mols == 0:
            return False
        dif = [int(x) - int(y) for (x, y) in zip(self.availables_mols, self.all_samples_needs)]
        for x in dif:
            if x < 0:
                # self.message = "third sample NOT POSSIBLE"
                return False
        mols_to_get = self.number_of_mols_carried + sum_mols
        if mols_to_get <= self.max_number_of_mols_to_carry:
            return True
        else:
            return False

    # recupere la mol la moins disponible et permettant de compléter un sample
    def get_mol(self, needs):
        mol = ""
        dif = []
        j = 0
        for i in needs:
            if i == 0:
                dif.append(100)
                j += 1
            else:
                # comparaison entre mols dispo et besoins pour le sample
                # (expertise deja prise en compte dans les needs du sample)
                dif.append(self.availables_mols[j] - i)
                j += 1
        temp = min(dif)
        pos = [i for i, j in enumerate(dif) if j == temp][0]
        if pos == 0:
            mol = "A"
        elif pos == 1:
            mol = "B"
        elif pos == 2:
            mol = "C"
        elif pos == 3:
            mol = "D"
        elif pos == 4:
            mol = "E"
        print("CONNECT", mol)


############################## LABORATORY ##############################

class Laboratory(State):

    def __init__(self, myRobot, samples, available_mols, projects, ennemyRobot):
        super().__init__(myRobot, samples, available_mols, projects, ennemyRobot)
        self.action()

    def action(self):
        if self.samples_id_ready != []:
            self.validate_sample()
        elif self.number_of_samples_carried > 0 and self.samples_id_doable != []:
            self.goto_molecules()
        else:
            self.goto_samples()

    def validate_sample(self):
        print("CONNECT", self.samples_id_ready[0])


### --- FSM - Device --- ###

class Computer(object):

    def execute(self, myRobot, ennemyRobot, samples, available_mols, projects):

        self.myRobot = myRobot
        self.ennemyRobot = ennemyRobot
        self.samples = samples
        self.available_mols = available_mols
        self.projects = projects

        if myRobot.eta > 0:
            State(myRobot, samples, available_mols, projects, ennemyRobot)
            print('')
        else:
            if self.myRobot.target == "START_POS":
                State(myRobot, samples, available_mols, projects, ennemyRobot)
                print("GOTO SAMPLES")

            if self.myRobot.target == "SAMPLES":
                Samples(myRobot, samples, available_mols, projects, ennemyRobot)

            if self.myRobot.target == "DIAGNOSIS":
                Diagnosis(myRobot, samples, available_mols, projects, ennemyRobot)

            if self.myRobot.target == "MOLECULES":
                Molecules(myRobot, samples, available_mols, projects, ennemyRobot)

            if self.myRobot.target == "LABORATORY":
                Laboratory(myRobot, samples, available_mols, projects, ennemyRobot)


# CLASSES VALUES

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


# INSTANCIATION
r = Computer()

myRobot = None
ennemyRobot = None

# INPUTS
project_count = int(input())

projects = []

for i in range(project_count):
    a, b, c, d, e = [int(j) for j in input().split()]
    projects.append([a, b, c, d, e])

# GAME LOOP
while True:

    # ROBOTS
    for i in range(2):
        inputs = input().split()
        if i == 0:
            myRobot = Robot(inputs)
        if i == 1:
            ennemyRobot = Robot(inputs)

    # MOLECULES
    available_a, available_b, available_c, available_d, available_e = [int(i) for i in input().split()]
    available_mols = [available_a, available_b, available_c, available_d, available_e]

    # SAMPLES
    samples = []
    sample_count = int(input())
    for i in range(sample_count):
        inputs = input().split()
        sample = Sample(inputs)
        samples.append(sample)

    # EXECUTION
    r.execute(myRobot, ennemyRobot, samples, available_mols, projects)
