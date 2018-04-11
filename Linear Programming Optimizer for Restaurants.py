from pulp import * 
import math
# Creates a list of the Ingredients
allproducts =  []
SRP = {}
MaxServe = {}
Discount = {}
Categories = {}
UCategories = list(set([x for x in Categories.values()]))
#High Profit
products = []
# Create Dictionaries
MustOrder={}

class MaxOpti:

    def __init__(self, budget, meals, capacity):
        self.budget = int(budget)
        self.valuedeal = int(budget)*1.15
        self.meals = int(meals)
        self.capacity = int(capacity)
        
        self.NetCost = {i:SRP[i]*(1+Discount[i]) for i in allproducts}
        self.RequiredServings = {i:math.ceil(self.capacity/MaxServe[i])*MaxServe[i] for i in allproducts}
        self.SRPServe={i:float('{0:.2f}'.format(SRP[i]/MaxServe[i])) for i in allproducts}
        self.NetCostServe={i:self.NetCost[i]/MaxServe[i] for i in allproducts}
    def CatSelection(self, req):
        CategorySRP = [i for i, j in Categories.items() if j == UCategories[req]] #Index is inputted and search corresponding category to product list of products
        SRPCategory = {i: self.SRPServe[i] for i in CategorySRP}
        TopChoices = sorted(SRPCategory, key=lambda key:SRPCategory[key], reverse=True)[:3]
        prob = LpProblem('', LpMaximize)
        binary_var = LpVariable.dicts("", TopChoices,0)             #Binary Variable
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in TopChoices]) #Objective Function
        prob += lpSum([binary_var[i]*MaxServe[i] for i in TopChoices]) <= client.capacity, "Capacity" #Constraint
        prob.solve()
        OptimizedChoices1 = {str(v)[1:].replace("_"," ") : math.ceil(v.varValue) for v in prob.variables()}
        PotentialSRP,PotentialNet = client.SRPNETCalculator(OptimizedChoices1)  
        
        prob = LpProblem('', LpMaximize)
        binary_var = LpVariable.dicts("", TopChoices,0)             #Binary Variable
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in TopChoices]) #Objective Function
        prob += lpSum([binary_var[i]*MaxServe[i] for i in TopChoices]) <= client.capacity, "Capacity" #Constraint
        prob += binary_var[TopChoices[1]] >= 1, 'Force'
        prob.solve()
        OptimizedChoices2 = {str(v)[1:].replace("_"," ") : math.ceil(v.varValue) for v in prob.variables()}
        PotentialSRP2,PotentialNet2 = client.SRPNETCalculator(OptimizedChoices2) 
        
        prob = LpProblem('', LpMaximize)
        binary_var = LpVariable.dicts("", TopChoices,0)             #Binary Variable
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in TopChoices]) <=client.budget #Objective Function
        prob += lpSum([binary_var[i]*MaxServe[i] for i in TopChoices]) #<= client.capacity, "Capacity" #Constraint
        prob.solve()
        OptimizedChoices3 = {str(v)[1:].replace("_"," ") : math.ceil(v.varValue) for v in prob.variables()}
        PotentialSRP3,PotentialNet3 = client.SRPNETCalculator(OptimizedChoices2)
        
        client.CatCalculator(TopChoices, OptimizedChoices1,OptimizedChoices2,OptimizedChoices3)
        return TopChoices
    def CatCalculator(self,TopChoices, Selection, Selection2, Selection3): #FIX THE FORMATTING TO PRICE PER SERVING (MULTIPLY THE SERVINGS AND PRICE PER SERVINGS)
        OptimalSelection = {key:MaxServe[key]*value for key,value in Selection.items()}
        Weight = {key: OptimalSelection[key]/sum(OptimalSelection.values()) for key, value in Selection.items()}
        TotalSRPServe='{0:.2f}'.format(sum(self.SRPServe[key]*Weight[key]  for key, value in Selection.items()))
        TotalNetCostServe='{0:.2f}'.format(sum(self.NetCostServe[key]*Weight[key] for key, value in Selection.items()))
        
        OptimalSelection2 = {key:MaxServe[key]*value for key,value in Selection2.items()}
        Weight2 = {key: OptimalSelection2[key]/sum(OptimalSelection2.values()) for key, value in Selection.items()}
        TotalSRPServe2='{0:.2f}'.format(sum(self.SRPServe[key]*Weight2[key]  for key, value in Selection.items()))
        TotalNetCostServe2='{0:.2f}'.format(sum(self.NetCostServe[key]*Weight2[key] for key, value in Selection.items()))
        
        OptimalSelection3 = {key:MaxServe[key]*value for key,value in Selection3.items()}
        Weight3 = {key: OptimalSelection3[key]/sum(OptimalSelection3.values()) for key, value in Selection.items()}
        TotalSRPServe3='{0:.2f}'.format(sum(self.SRPServe[key]*Weight3[key]  for key, value in Selection.items()))
        TotalNetCostServe3='{0:.2f}'.format(sum(self.NetCostServe[key]*Weight3[key] for key, value in Selection.items()))
        print ('\n{0: <30}'.format("Items ")+ '{0: ^9}'.format("Servings") +'{0: <15}'.format("Price/Serving") 
        + '{0: <9}'.format("0") + '{0: <9}'.format("1") + '{0: <9}'.format("2") )
        for key in TopChoices:
            print( '{0: <30}'.format(key) +'{0: ^9}'.format(str(MaxServe[key])) 
                                    +'{0: ^15}'.format(str(self.SRPServe[key])) 
                                    +'{0: <9}'.format(str(OptimalSelection[key]))
                                    +'{0: <9}'.format(str(OptimalSelection2[key]))
                                    +'{0: <9}'.format(str(OptimalSelection3[key])))
        print('{0: >35}'.format("Total Servings") 
                                    + '{0: >21}'.format(str(sum(OptimalSelection.values())))
                                    + '{0: >9}'.format(str(sum(OptimalSelection2.values())))
                                    + '{0: >9}'.format(str(sum(OptimalSelection3.values()))))
        print('{0: >35}'.format("SRP/Serving") + '{0: >24}'.format(str(TotalSRPServe))
                                                + '{0: >9}'.format(str(TotalSRPServe2))
                                                + '{0: >9}'.format(str(TotalSRPServe3)))
        print('{0: >35}'.format(" DP/Serving") + '{0: >24}'.format(str(TotalNetCostServe))
                                                +'{0: >9}'.format(str(TotalNetCostServe2))
                                                +'{0: >9}'.format(str(TotalNetCostServe3))) # Totals
        print('{0: >35}'.format("Savings")+ '{0:>22}'.format(MaxOpti.CatPercentageCalc(TotalSRPServe,TotalNetCostServe))
                                        + '{0:>9}'.format(MaxOpti.CatPercentageCalc(TotalSRPServe2,TotalNetCostServe2))
                                        + '{0:>9}'.format(MaxOpti.CatPercentageCalc(TotalSRPServe3,TotalNetCostServe3)))#Savings
        
    def OrderIntegration(self, CatSelect, OrderSelect):                          #This takes the List of the Items and the Index chosen 
        cost = self.RequiredServings[CatSelect[OrderSelect]]*self.NetCostServe[CatSelect[OrderSelect]]
        if cost > self.budget:
            return print ("You don't have enough budget!\n")
        self.budget -= cost
        self.valuedeal -=cost
        print('Order Integration ;' + str(self.budget))
        #MustOrder = {CatSelect[OrderSelect]: 1.0}
        MustOrder[CatSelect[OrderSelect]] = MustOrder.get(CatSelect[OrderSelect],0)+1
        return MustOrder
    def SRPNETCalculator(self,Orders):
        TotalSRP = {key: self.SRPServe[key]*Orders[key]*self.RequiredServings[key] for key, value in Orders.items()}   #Absolute Savings, Discounted Price, Total SRP         
        TotalNet = {key: self.NetCostServe[key]*Orders[key]*self.RequiredServings[key] for key, value in Orders.items()}

        return TotalSRP, TotalNet
    def Meals():
        pass

    def Optimize(self, MustOrder):
        if MustOrder == None: MustOrder = {}
        #Choice 1
        prob = LpProblem('Choice 1', LpMaximize)
        binary_var = LpVariable.dicts("", products, cat='Binary')             #Binary Variable
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in products]) #Objective Function
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in products]) <= client.budget, "Budget" #Constraint
        prob.solve()
        Orders = {str(v)[1:].replace("_"," ") : v.varValue for v in prob.variables() if v.varValue>0}
        Orders = {**MustOrder, **Orders}
        TotalSRP, TotalNet = client.SRPNETCalculator(Orders)
        client.TableCalculator(TotalSRP, TotalNet, 1, Orders)

        #Choice 2
        prob = LpProblem('Choice 2', LpMaximize)
        binary_var = LpVariable.dicts("", products, cat='Binary')             #Binary Variable
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in products]) #Objective Function
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in products]) <= client.budget, "Budget" #Constraint
        prob.solve()
        Orders2 = {str(v)[1:].replace("_"," ") : v.varValue for v in prob.variables() if v.varValue>0} # Orders
        Orders2 = {**MustOrder, **Orders2}
        TotalSRP2, TotalNet2 = client.SRPNETCalculator(Orders2)
        client.TableCalculator(TotalSRP2, TotalNet2, 2, Orders2)
    
        #Choice 3
        prob = LpProblem('Choice 3', LpMaximize)
        binary_var = LpVariable.dicts("", products, cat='Binary')             #Binary Variable
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in products]) #Objective Function
        prob += lpSum([binary_var[i]*self.RequiredServings[i]*self.NetCostServe[i] for i in products]) <= client.valuedeal, "Budget" #Constraint
        prob.solve()
        Orders3 = {str(v)[1:].replace("_"," ") : v.varValue for v in prob.variables() if v.varValue>0} # Orders
        Orders3 = {**MustOrder, **Orders3}
        TotalSRP3, TotalNet3 = client.SRPNETCalculator(Orders3)
        client.TableCalculator(TotalSRP3, TotalNet3, 3, Orders3)
        return
    def TableCalculator(self,TotalSRP,b, j,Orders): #FIX THE FORMATTING TO PRICE PER SERVING (MULTIPLY THE SERVINGS AND PRICE PER SERVINGS)
        TotalSRPServe=sum({key:self.SRPServe[key] for key, value in Orders.items()}.values())
        print ('\n{0: <35}'.format("Choice "+str(j))+ '{0: <15}'.format("Price/Serving") + '{0: <9}'.format("Quantity") + '{0: <9}'.format("Servings") )
        for key,value in TotalSRP.items():
            print( '{0: <35}'.format(key) + '{0: <15}'.format(str(self.SRPServe[key])) +'{0: <9}'.format(str(Orders[key]))+ str(self.RequiredServings[key]))
        print( '{0: >35}'.format("Total   ") + '{0: <15}'.format(str(TotalSRPServe)) + '{0: <9}'.format("For " + str(self.capacity)))
        print( '{0: >35}'.format("Total SRP   ") + '{0: <15}'.format(str(sum(TotalSRP.values())))) # Totals
        print( '{0: >35}'.format("Total DP   ") + '{0: <15}'.format(str(sum(b.values()))))
        print('{0: >35}'.format("Savings   ")+'{0: <15}'.format(MaxOpti.PercentageCalc(TotalSRP,b))) #Savings
    
    
    @staticmethod
    def PercentageCalc (a, b):
        return '{0:0}'.format(math.ceil(((sum(a.values())-sum(b.values()))/sum(a.values()))*100))+'%'
    def CatPercentageCalc (TotalSRPServe, TotalNetCostServe):
        return str(int(((float(TotalSRPServe)-float(TotalNetCostServe))/float(TotalSRPServe))*100))+'%'
    
    @staticmethod
    def SelectionPrinter(List):
        for i, j in enumerate(List):
            print(str(i)+'. '+str(j))
        print(str(len(List))+ '. Done')

client = MaxOpti(input("What is your total budget per head per day?: "),
                    input("How many meals do you need to provide?: "),
                input("How many people do you need to feed?: "))

#client.CustReq(input("Do you have any non-negotiables?: \n1. Protein\n2. Pizza\n3. Donuts\n4. Rice \n5. Dessert\n6. None\nPlease input a number: "))

#client = MaxOpti(50000,1, 50)
while True:
    client.SelectionPrinter(UCategories)                                        # 1. Chicken 2. Pizza etc.
    req =int(input("Do you have anynon-negotiables? Please input a number: "))
    if req == 9: break
    CatSelect = client.CatSelection(req)                                        #Input to get the Top Three Orders
    #client.SelectionPrinter(CatSelect)                                          #Print out the Top Three Items
    OrderSelect = int(input("Please select an item: "))
    MustOrders = client.OrderIntegration(CatSelect,OrderSelect)                   #Input Top Three Item List
client.Optimize(MustOrders)

