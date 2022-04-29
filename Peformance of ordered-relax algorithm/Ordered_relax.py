from pulp import *
import csv
import numpy
from os import walk
import collections

######ALL KEY VARIABLES###### (Temporary variables without significant meaning are not explained here)
##n: no. of voters##
##m: no. of projects##
##budget: total budget available##
##'projects' is an m x 2 matrix such that:##
    ##projects[i][0]: the project ID of project indexed i## (projects are indexed from 0 to m-1 for the sake of convenience)
    ##projects[i][1]: cost of project indexed i##
##'votes' is an n x m binary matrix such that:##
    ##vote[i][j]: 1 if voter indexed i approves project indexed j, and 0 otherwise## (voters are indexed from 0 to n-1 for the sake of convenience)
##selected_projects: an m-sized binary array such that:##
    ##selected_projects[i]: 1 if project indexed i is selected, and 0 otherwise##
##selected_IDs: Collection of IDs of all selected projects##
##integral_optimal: Optimal utility of worse-off voter##
##or_optimal: Utility of worse-off voter form our algorithm ordered_relax##

###INTEGRAL LP FUNCTION - Solves ILP and returns optimal solution###
def integral_lp(n,m,projects,votes,budget,name):
    prob = LpProblem("name", LpMaximize)
    #Create m variables corresponding to selection of projects
    x = LpVariable.dicts("x", range(m + 1), 0, 1, LpInteger)
    q = LpVariable("final", 0, None)
    #Create objective function
    prob += q
    #Create constraints
    prob += lpSum(projects[i][1]*x[i] for i in range(m)) <= budget
    for i in range(n):
        prob += lpSum(projects[j][1]*votes[i][j]*x[j] for j in range(m)) >= q #For each voter, add a constraint to capture that q is min of all utilities
    #The problem data is written to an .lp file
    prob.writeLP(name+".lp")
    #The problem is solved using PuLP's choice of Solver
    prob.solve()
    #The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])
    selected_IDs = []
    #Each of the variables is printed with it's resolved optimum value
    for v in prob.variables():
        if(v.varValue == 1 and v.name != "q"):
            selected_index = int(str(v.name)[2:4])
            selected_IDs.append(projects[selected_index][0])  
    if(value(prob.objective) > 0):
        print("----------------------------------------------")
        print("Optimal outcome selects the following projects: "+str(selected_IDs))
        print("----------------------------------------------")
    return(value(prob.objective))
    
###RETURNS UTILITY OF THE WORSE-OFF AGENT FROM A GIVEN SET OF PROJECTS###
def max_min(n,m,projects,votes,budget,selected_projects):
    util = [0 for i in range(n)] #Initialize utilities of all voters to zero
    for i in range(n):
        for j in range(m):
            #Add the cost of selected approved projects of voter i to utility of i
            util[i] = util[i] + votes[i][j]*selected_projects[j]*projects[j][1] #(whether i approved project j*whether j is selected*cost of j)
    util.sort() #Sort utilities of all the agents in ascending order
    return(util[0]) #Return minimum utility
    
###ORDERED RELAX FUNCTION - Solves fractional LP, performs the succeding steps and returns the output of our ordered_relax algorithm###
def ordered_relax(n,m,projects,votes,budget,name):
    prob = LpProblem(name, LpMaximize)
    #Create variables corresponding to selection of projects
    x = LpVariable.dicts("x", range(m + 1), 0, 1) #Note that the integrality requirement is relaxed, that is the only change in LP
    q = LpVariable("final", 0, None)
    #Create Objective function
    prob += q
    #Create constraints
    prob += lpSum(projects[i][1]*x[i] for i in range(m)) <= budget
    for i in range(n):
        prob += lpSum(projects[j][1]*votes[i][j]*x[j] for j in range(m)) >= q
    #The problem data is written to an .lp file
    prob.writeLP(name+".lp")
    #The problem is solved using PuLP's choice of Solver
    prob.solve()
    #The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])
    xas = [0 for i in range(m)] #Stores values assigned to each project by fractional LP, each value lies between 0 and 1. In paper, we used x_p^* to denote this.
    skip = 0
    for v in prob.variables():
        if(skip > 0):
            temp = str(v.name)[2:].strip()
            now_index = int(temp) #Extract the index of the project corresponding to LP variable
            xas[now_index] = v.varValue #Store the value assigned LP variable in the array xas
        skip = skip + 1
    caxas = [projects[i][1]*xas[i] for i in range(m)] #Calculate c_p.x_p^* for every project p
    sorted_indices = sorted(range(len(caxas)), key=caxas.__getitem__, reverse=True) #Sort the project indices w.r.t. decreasing order of c_p.x_p^*
    covered_budget = 0
    selected_projects = [0 for i in range(m)]
    for i in range(m):
        if(covered_budget + projects[sorted_indices[i]][1] <= budget): #Add projects in that order until we cannot accommodate the next project
            covered_budget = covered_budget + projects[sorted_indices[i]][1]
            selected_projects[sorted_indices[i]] = 1
        else:
            break
    selected_IDs = []
    for i in range(m):
        if(selected_projects[i] == 1):
            selected_IDs.append(projects[i][0]) #Extract the IDs of all the selected projects by our algorithm
    print("------------------------------------------------------")
    print("Ordered-relax algorithm selects the following projects: "+str(selected_IDs))
    or_utility = max_min(n,m,projects,votes,budget,selected_projects) #Calculate the utility of worse-off agent from the algorithm
    return(or_utility)

###SEARCH FOR INDEX OF PROJECT BY ITS ID###
def index_of_proj(projects,projID,m):
    for i in range(m):
        if(projects[i][0] == projID):
            return i
            
###SEARCH FOR COST OF PROJECT BY ITS ID###
def cost_of_proj(projects,projID,m):
    for i in range(m):
        if(projects[i][0] == projID):
            return proj[i][1]

###READ THE FILE, EXTRACT THE VALUES OF VARIABLES, CALL LPs, AND FINALLY RETURN THE APPROXIMATION RATIO###
def ratio(filename):
    path = "./Sample datasets/"+filename #Give relative path: change "./Sample datasets/" to ".\\Sample datasets\\" if you use windows and to "Sample datasets/" if you use macOS
    with open(path, 'r', newline='', encoding="utf-8") as csvfile: #Opened the .pb file
        meta = {}
        section = ""
        header = []
        reader = csv.reader(csvfile, delimiter=';')
        dummy = 0
        end_meta = 0
        project_counter = 0
        vote_counter = 0
        for row in reader:
            if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                section = str(row[0]).strip().lower()
                header = next(reader)
            elif section == "meta":
                meta[row[0]] = row[1].strip()
            elif section == "projects":
                if(end_meta == 0):
                    m = meta["num_projects"].strip().replace(',','') #Extract the number of projects
                    n = meta["num_votes"].strip().replace(',','') #Extract the number of votes
                    budget = meta["budget"].strip().replace(',','') #Extract the budget available
                    if(not m.isdigit() or not n.isdigit() or not budget.isdigit()):
                        return "Template of the file is changed (near n or m or budget i.e.., at line #9, #10 or #11)" #If the file is not following template, report it.
                    m = int(m)
                    n = int(n)
                    budget = int(budget)
                    end_meta = end_meta + 1
                    projects = [[0 for i in range(2)] for j in range(m)]
                    votes = [[0 for i in range(m)] for j in range(n)]
                if(not row[0].strip().isdigit() or not row[1].strip().isdigit()):
                    return "Template of the file is changed (Line #21 does not start with project ID and cost)" #If the file is not following template, report it.
                projects[project_counter][0] = int(row[0].strip()) #Extract and save the project ID
                projects[project_counter][1] = int(row[1].strip()) #Extract and save the project cost
                project_counter = project_counter+1
            elif section == "votes":
                approvedIDs = row[4].strip().split(",")
                for each_ID in approvedIDs:
                    if(each_ID.strip().isdigit()):
                        ID_now = int(each_ID.strip())
                        votes[vote_counter][index_of_proj(projects,ID_now,m)] = 1 #Set votes[i][j]=1 if ID of project indexed j is approved by voter i
                    else:
                        return "Template of the file is changed (Vote is not the fifth field in VOTES section)" #If the file is not following template, report it.
                vote_counter = vote_counter+1
        integral_optimal = integral_lp(n,m,projects,votes,budget,filename) #Call ILP to get the optimal solution          
        or_optimal = ordered_relax(n,m,projects,votes,budget,filename) #Call ordered_relax to get the output of our algorithm
        if(integral_optimal == 0):
            print("The output of ordered-relax is optimal since the optimal minimum utility is zero")
            approx_ratio = 1 #This implies it is impossible to give non-zero utility to all voters in the instance and hence any set is optimal.
        else:
            if(or_optimal == 0):
                approx_ratio = 0
            else:
                print("The optimal minimum utility of a voter is "+str(integral_optimal))
                print("The minimum utility of a voter from ordered-relax is "+str(or_optimal))
                approx_ratio = float(or_optimal/integral_optimal)
        print("The approximation ratio achieved is "+str(approx_ratio))
        return(approx_ratio)
        
filename = input("Enter the dataset name: (e.g., poland_warszawa_2017_piaski.pb)")
ratio(filename)
