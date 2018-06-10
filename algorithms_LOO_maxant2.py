# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 14:30:26 2018

@author: Andrea Silva
"""



class ReadData:
    
    def __init__(self):
        self.dados = []
        self.read()
        
    def read(self):    
        with open('sai') as f:
            l = f.readline()
        data = eval(l)
        
        print(data)
        
        for i in data:
            seq = []
            for j in data[i]:
                if j['Classify'] == "Accepted":
                    seq.append(j["Problem"])
            self.dados.append(" ".join(str(x) for x in seq))
        print(self.dados)
        
        CreateInputFile('input.txt',self.dados)



class CreateInputFile:
    
    def __init__(self, inputfile, dados):
        self.inputname = inputfile
        self.dados = dados
        self.create()
        
    def create(self):
        f = open(self.inputname, "w")
        for seq in self.dados:
            linha = seq.split(" ")
            s = ""
            for i in linha:
                s += (i)
                s += (" -1 ")
            s += ("-2")
            f.write(s)
            f.write("\n")
        f.close()
        print("Ficheiro de input gerado")
        
 
    
#ReadData()



class ReadOutputFile:

    def __init__(self, outputfile):
        self.outputname = outputfile
        self.lines = []
        self.valores = {}
        
    def read(self):
        output = open(self.outputname,"r")
        linhas = output.read().splitlines()
        
        for l in linhas:
            linha = l.rsplit(" ")
            self.lines.append(linha)
        
        output.close()
        
        for i in self.lines:
            if i[0] not in self.valores.keys():
                self.valores[i[0]] = {i[2]:(i[6],i[4])}
            else:
                self.valores[i[0]][i[2]] = (i[6],i[4])
        
        return self.valores

#ReadOutputFile("output.txt").read()




import subprocess

class TRuleGrowth:
    def __init__(self, input, output):
        self._executable = "spmf.jar"
        self._input = input
        self._output = output

    def run(self, min_supp=0.1, min_conf = 0.1, window_size = 4, max_ant = 1, max_cons = 1):
        # java -jar spmf.jar run VMSP contextPrefixSpan.txt output.txt 50%
        subprocess.call(["java", "-jar", self._executable, "run", "TRuleGrowth", self._input, self._output, str(min_supp), str(min_conf), str(window_size), str(max_ant), str(max_cons)])


        
class ExecuteTRuleGrowth:
    
    def __init__(self, input_name = "input.txt", output_name = "output.txt"):
        self.trg = TRuleGrowth(input_name,output_name)
        self.runalgorithm()
        
    def runalgorithm(self):    
        self.trg.run()
        
#ExecuteTRuleGrowth()



class RuleGrowth:
    def __init__(self, input, output):
        self._executable = "spmf.jar"
        self._input = input
        self._output = output

    def run(self, min_supp=0.1, min_conf = 0.1, max_ant = 2, max_cons = 1):
        # java -jar spmf.jar run VMSP contextPrefixSpan.txt output.txt 50%
        subprocess.call(["java", "-jar", self._executable, "run", "RuleGrowth", self._input, self._output, str(min_supp), str(min_conf), str(max_ant), str(max_cons)])


class ExecuteRuleGrowth:
    
    def __init__(self, input_name = "input.txt", output_name = "output.txt"):
        self.trg = RuleGrowth(input_name,output_name)
        self.runalgorithm()
        
    def runalgorithm(self):    
        self.trg.run()



class PredictNextItem:
    
    def __init__(self, item, outputname = "output.txt"):
        self.output = outputname
        self.rules = ReadOutputFile(self.output).read()
        self.item = item
        self.possibilities = {}
        
    def search(self):
        item_with_antecedent = ""
        if self.item[2] in self.rules.keys():
            print("Searching ", self.item[2], "...")
            for key in self.rules[self.item[2]].keys():
                self.possibilities[key] = self.rules[self.item[2]][key]
        if self.item[0] != None and self.item[1] != None:
            item_with_antecedent += self.item[0]+","+self.item[1]+","+self.item[2]
            print("Searching with antecedente", item_with_antecedent, "...")
            if item_with_antecedent in self.rules.keys():
                for key in self.rules[item_with_antecedent].keys():
                    if key in self.possibilities.keys() and self.possibilities[key][0] < self.rules[item_with_antecedent][key][0]:
                        self.possibilities[key] = self.rules[item_with_antecedent][key]
                    elif key not in self.possibilities.keys():
                        self.possibilities[key] = self.rules[item_with_antecedent][key]
        item_with_antecedent = ""
        if self.item[1] != None:
            item_with_antecedent += self.item[1]+","+self.item[2]
            print("Searching with antecedente", item_with_antecedent, "...")
            if item_with_antecedent in self.rules.keys():
                for key in self.rules[item_with_antecedent].keys():
                    if key in self.possibilities.keys() and self.possibilities[key][0] < self.rules[item_with_antecedent][key][0]:
                        self.possibilities[key] = self.rules[item_with_antecedent][key]
                    elif key not in self.possibilities.keys():
                        self.possibilities[key] = self.rules[item_with_antecedent][key]
        print(self.possibilities)
        if len(self.possibilities) != 0:
            bestitem = self.BestPredictNextItem()       
            return(bestitem)
        else:
            return None
        
    def BestPredictNextItem(self):
        nextitem = []
        nextitem.append(sorted(self.possibilities, key = self.possibilities.get, reverse = True)[0])
        print(nextitem)
        conf = self.possibilities[nextitem[0]][0]
        for key in self.possibilities.keys():
            if self.possibilities[key][0] == conf and self.possibilities[key][1] == self.possibilities[nextitem[0]][1] and key not in nextitem:
                nextitem.append(key)
            elif self.possibilities[key][0] == conf and self.possibilities[key][1] > self.possibilities[nextitem[0]][1]:
                nextitem = key
        print(nextitem)
        return nextitem
        

#print(PredictNextItem(['5','6']).search())


class LOO:
    def __init__(self, inputfile):
        self.inputname = inputfile
        self.utilizadores = []
        self.leave_one_out()
        
    def leave_one_out(self):
        f = open(self.inputname, "r")
        linhas = f.read().splitlines()
        for l in linhas:
            self.utilizadores.append(l.replace("-1 ","").replace(" -2",""))
        
        
        accuracys = []
        for i in range(len(self.utilizadores)):
            print('TESTE ', i)
            right = 0 
            wrong = 0
            total = 0
            infilename = "input"+str(i)+".txt"
            outfilename = "output"+str(i)+".txt"
            
            treino = self.utilizadores[:i] + self.utilizadores[i+1:]
            CreateInputFile(infilename, treino)
            
            ExecuteTRuleGrowth(infilename, outfilename)
            
            teste = self.utilizadores[i].split(" ")
            print('VARIÁVEL DE TESTE ',teste)
            for item in range(len(teste)-1):
                print("NEW ITEM ")
                print(teste[item], '-->', teste[item+1])
                if item == 0:
                    nextitems = PredictNextItem([None, None, teste[item]],outfilename).search()
                elif item == 1:
                    nextitems = PredictNextItem([None, teste[item-1],teste[item]],outfilename).search()
                else:
                    nextitems = PredictNextItem([teste[item-2],teste[item-1],teste[item]],outfilename).search()
                print(nextitems)
                if nextitems != None and teste[item+1] in nextitems:
                    right += 1
                else:
                    wrong += 1
                total += 1
                print(right, ', ', (wrong), ', ',total)
            accuracy = right/total
            print('ACCURACY DO TESTE ', i, ': ', accuracy)
            accuracys.append(accuracy)
            print('ACCURACYS ACUMULADAS: ', accuracys)
        final_accuracy = sum(accuracys)/len(accuracys)
        print('ACCURACY FINAL: ', final_accuracy)


LOO("input.txt")
