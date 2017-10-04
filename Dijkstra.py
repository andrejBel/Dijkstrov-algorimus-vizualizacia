import sys
import numpy as np
import matplotlib.pyplot as plot
import networkx as nx
from copy import deepcopy

class Vrchol:

    nekonecno = (sys.maxsize / 2) - 1

    def __init__(self, oznacenieVrchola):
        self._oznacenieVrchola = oznacenieVrchola
        self.docasny = True
        self.predchadzajuciVrchol = None
        self.t = Vrchol.nekonecno
        self._zoznamSusedov = []
        self.riadiaciVrchol = False

    def inicializuj(self):
        self.docasny = True
        self.predchadzajuciVrchol = None
        self.t = Vrchol.nekonecno

    def setPredchadzajuciVrchol(self, vrchol):
        self.predchadzajuciVrchol = vrchol
        return self

    def setDefinitivny(self):
        self.docasny = False
        self.riadiaciVrchol = True
        return self

    def unSetRiadiaci(self):
        self.riadiaciVrchol = False


    def pridajSuseda(self, sused):
        if sused is not None:
            self._zoznamSusedov.append(sused)

    def oznacenieT(self):
        return "N" if self.t == Vrchol.nekonecno else str(self.t)

    def oznaceniePredchadzajucehoVrchola(self):
        return "-" if self.predchadzajuciVrchol is None else str(self.predchadzajuciVrchol.oznacenieVrchola)

    @property
    def oznacenieVrchola(self):
        return self._oznacenieVrchola

    @property
    def zoznamSusedov(self):
        return self._zoznamSusedov

    def farba(self):
        return 'red' if self.riadiaciVrchol else 'white' if self.docasny else 'green'

    def __eq__(self, inyVrchol):
        return self.oznacenieVrchola == inyVrchol.oznacenieVrchola

    def __str__(self):
        return '{}'.format(self.oznacenieVrchola)


class Digraf:
    def __init__(self, nazov_suboru='hrany.txt'):
        nacitanehrany = np.genfromtxt(nazov_suboru, str)
        if nacitanehrany.size == 3:
            nacitanehrany = [nacitanehrany]
        self.riadiaciVrchol = Vrchol(None)
        self.vrcholy = []
        self.hrany = {}
        self.digraf = nx.DiGraph()
        self.stavyVrcholov = []
        for v1, v2, cena in nacitanehrany:
            if v1 != v2:
                if not v1 in self.digraf.nodes():
                    self.vrcholy.append(Vrchol(v1))
                if not v2 in self.digraf.nodes():
                    self.vrcholy.append(Vrchol(v2))
                if (v1, v2) not in self.hrany:
                    self.hrany[(v1, v2)] = int(cena)
                    self.najdiVrcholPodlaOznacenia(v1).pridajSuseda(self.najdiVrcholPodlaOznacenia(v2))
                self.digraf.add_edge(v1, v2, weight=cena)
        self.vrcholy.sort(key=lambda v: v.oznacenieVrchola)
        try:
            nacitaneSuradnice = np.loadtxt("Suradnice/suradnice" + str(len(self.vrcholy)) + ".txt", int)
            self.position = {vrchol.oznacenieVrchola: nacitaneSuradnice[i] for i, vrchol in enumerate(self.vrcholy)}
        except IOError:
            self.position = nx.circular_layout(self.digraf)
        self.poziciaPopisiek = {k: [v[0] - 0.2, v[1] + 0.5] for k, v in self.position.items()}
        self.edgeLabels = {(v1, v2): self.hrany[v1, v2] for v1, v2 in self.hrany.keys()}
        self.stavyVrcholov.append(deepcopy(self.vrcholy))

    def najdiVrcholPodlaOznacenia(self, oznacenieVrchola, zoznamVrcholov=None):
        if zoznamVrcholov is None:
            zoznamVrcholov = self.vrcholy
        for v in zoznamVrcholov:
            if str(v.oznacenieVrchola) == str(oznacenieVrchola):
                return v

    def najdiVrcholSMinimalnouZnackouT(self):
        neoznacene = [v.t for v in self.vrcholy if v.docasny]
        if len(neoznacene) > 0:
            minimum = min(neoznacene)
        else:
            return None
        for v in self.vrcholy:
            if v.docasny and v.t == minimum:
                return v

    def inicializacia(self, startovaciVrchol):
        for v in self.vrcholy:
            v.inicializuj()
        startovaciVrchol.t = 0

    def hranyIncidentneSVrcholom(self, vrchol):
        return [hrana for hrana in self.hrany if hrana.vrchol1 == vrchol and hrana.vrchol2.docasny]

    def dijkstrovAlgoritmus(self, startovaciVrchol):
        if startovaciVrchol is not None:
            self.inicializacia(startovaciVrchol)
            while self.najdiVrcholSMinimalnouZnackouT() is not None:
                self.riadiaciVrchol = self.najdiVrcholSMinimalnouZnackouT().setDefinitivny()
                self.stavyVrcholov.append(deepcopy(self.vrcholy))
                for incidentnyVrchol in [vrchol for vrchol in self.riadiaciVrchol.zoznamSusedov if vrchol.docasny]:
                    if incidentnyVrchol.t > self.riadiaciVrchol.t + self.hrany[
                        self.riadiaciVrchol.oznacenieVrchola, incidentnyVrchol.oznacenieVrchola]:
                        incidentnyVrchol.t = self.riadiaciVrchol.t + self.hrany[
                            self.riadiaciVrchol.oznacenieVrchola, incidentnyVrchol.oznacenieVrchola]
                        incidentnyVrchol.setPredchadzajuciVrchol(self.riadiaciVrchol)
                self.stavyVrcholov.append(deepcopy(self.vrcholy))
                self.riadiaciVrchol.unSetRiadiaci()
            self.stavyVrcholov.append(deepcopy(self.vrcholy))
            vystup = ''
            for vrchol in self.vrcholy:
                if vrchol.t < Vrchol.nekonecno:
                    vystup += 'Najkratsia cesta z vrchola {} do vrchola {} je {}, jej dlzka je {} \n'.format(
                        startovaciVrchol, vrchol, self.zrekonstruujCestu(startovaciVrchol, vrchol), vrchol.t)
                else:
                    vystup += 'Cesta z vrchola {} do vrchola {} neexistuje \n'.format(startovaciVrchol, vrchol)
            return vystup

    def zrekonstruujCestu(self, vrchol1, vrchol2):
        zapisanyVrchol = vrchol2
        cesta = list([vrchol2])
        while zapisanyVrchol != vrchol1:
            cesta.append(zapisanyVrchol.predchadzajuciVrchol)
            zapisanyVrchol = cesta[len(cesta) - 1]
        cesta.reverse()
        result = ''
        for i in range(0, len(cesta) - 1):
            result += str(cesta[i]) + '-'
        result += str(cesta[len(cesta) - 1])
        return result

    def kresliGraf(self, vrcholy=None):
        if vrcholy is None:
            vrcholy = self.vrcholy
        poslabels = {str(vrchol): vrchol.oznacenieT() + "/" + vrchol.oznaceniePredchadzajucehoVrchola() for vrchol in
                     vrcholy}
        nodeColors = [self.najdiVrcholPodlaOznacenia(vrchol, vrcholy).farba() for vrchol in self.digraf.nodes()]
        nx.draw_networkx_edge_labels(self.digraf, self.position, edge_labels=self.edgeLabels)
        nx.draw_networkx_labels(self.digraf, pos=self.poziciaPopisiek, labels=poslabels, font_size=12,
                                font_color="blue")
        nx.draw(self.digraf, pos=self.position, node_color=nodeColors, edge_labels=self.edgeLabels, with_labels=True)
        plot.show()

    def nakresliItyStav(self, cislo):
        self.kresliGraf(self.stavyVrcholov[cislo])

    def __str__(self):
        result = 'Vrcholy:\n'
        for vrchol in self.vrcholy:
            result += str(vrchol) + '\n'
        result += 'Hrany:\n'
        for v1, v2 in sorted(self.hrany):
            result += '{} - {} , cena {}\n'.format(v1, v2, self.hrany[v1, v2])
        return result


g = Digraf()
print(g)
g.kresliGraf()
print(g.dijkstrovAlgoritmus(g.najdiVrcholPodlaOznacenia('1')))
print(g.dijkstrovAlgoritmus(g.najdiVrcholPodlaOznacenia('2')))
