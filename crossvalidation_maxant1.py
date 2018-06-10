# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 18:22:50 2018

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

    def run(self, min_supp=0.1, min_conf = 0.1, window_size = 5, max_ant = 1, max_cons = 1):
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

    def run(self, min_supp=0.1, min_conf = 0.1, max_ant = 1, max_cons = 1):
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
        if self.item in self.rules.keys():
            print("Searching...")
            for key in self.rules[self.item].keys():
                self.possibilities[key] = self.rules[self.item][key]
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
    
    

from random import randrange

class CrossValidation:
    def __init__(self, inputfile):
        self.inputname = inputfile
        self.utilizadores = []
        self.cross_validation()
        
    def cross_validation(self):
        f = open(self.inputname, "r")
        linhas = f.read().splitlines()
        for l in linhas:
            self.utilizadores.append(l.replace("-1 ","").replace(" -2",""))
        print(self.utilizadores)
        cross_data = self.cross_validation_split(self.utilizadores, 7)
        
        accuracys = []
        for i in range(len(cross_data)):
            print('TESTE ', i)
            right = 0 
            wrong = 0
#            conf = 0.0
            total = 0
            infilename = "input"+str(i)+".txt"
            outfilename = "output"+str(i)+".txt"
            
            treino = []
            for j in range(len(cross_data)):
                if j != i:
                    treino += cross_data[j]
            
            CreateInputFile(infilename, treino)
            
            ExecuteRuleGrowth(infilename, outfilename)
            
            testes = cross_data[i]
            
            for i in testes:
                teste = i.split(" ")
                print('VARIÁVEL DE TESTE ',teste)
                for item in range(len(teste)-1):
                    print("NEW ITEM ")
                    print(teste[item], '-->', teste[item+1])
                    nextitems = PredictNextItem(teste[item],outfilename).search()
                    print(nextitems)
                    if nextitems != None and teste[item+1] in nextitems:
                        right += 1
                    else:
                        wrong += 1
                    total += 1
                    print(right, ', ', (wrong), ', ',total)
            accuracy = right/total
            print('ACCURACY DO TESTE: ', i, ': ', accuracy)
            accuracys.append(accuracy)
            print('ACCURACYS ACUMULADAS: ', accuracys)
        final_accuracy = sum(accuracys)/len(accuracys)
        print('ACCURACY FINAL: ', final_accuracy)
            
        
    def cross_validation_split(self, dataset, folds=3):
        dataset_split = list()
        dataset_copy = list(dataset)
        fold_size = int(len(dataset) / folds)
        for i in range(folds):
            fold = list()
            while len(fold) < fold_size:
                index = randrange(len(dataset_copy))
                fold.append(dataset_copy.pop(index))
            dataset_split.append(fold)
        return dataset_split
    
CrossValidation("input.txt")
        
