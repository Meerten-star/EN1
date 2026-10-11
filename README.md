Dit python programma is gemaakt voor het vak Experimentele Natuurkunde 1, Experiment 4: YBCO supergeleider.
Duo nummer 6. 

Het programma laat de gebruiker een selectie maken van de data, waarna het programma de transitiebreedte van de supergeleider berekend.
Gemaakt met matplotlib.
Het bestand 'test_data.csv' bevat de meetwaarden van de eerste versie van het experiment. Hiermee is het programma getest.

Stappenplan werking van programma
1) Het data-bestand wordt uitgelezen door functie DataLists.readData().
2) Er wordt een selectie gestart met Selection.\_\_init__() en de gebruiker krijgt de interface te zien door de functie Selection.displayAndSelect().
3) De gebruiker kan nu 
   - inzoomen op het gewenste gebied met datapunten met behulp van de RangeSlider van matplotlib.widgets.
   - een selectie van de data maken door op de grafiek te klikken, dit is gemaakt met de SpanSelector van matplotlib.widgets.
   - het programma sluiten door op Esc te drukken.
4) Nu wordt T(10%) en T(90%) van de selectie en daarmee ook de transitiebreedte uitgerekend, en geprint in het terminal en weergegeven naast de grafiek.
    Deze temperatuurwaarden worden op de volgende manier berekend:
   1) De gegeven selectie 'snapt' op een meetpunt van de temperatuur. In self.domain staat nu de minimale en de maximale temperatuur opgeslagen.
   2) Met de functie Selection.calcTransitiebreedte() wordt alles berekend. Allereerst wordt de temperatuur omgezet naar een index in de data.
   3) Vervolgens wordt deze index gebruikt om een lokaal gemiddelde te berekenen van de YBCO-weerstand bij die index met de functie Selection.localDeviation().
   4) Hiermee wordt de 10% & 90% YBCO weerstand uitgerekend.
   5) Deze worden omgezet in een bijbehorende temperatuur met functie Selection.ybcoToTemp() door een index te vinden bij die punten en daarvoor de temperatuur te bekijken. Dit is niet ideaal, aangezien dit afhankelijk is van de aanwezigheid van voldoende meetpunten rond dit gebied. Idealiter zou hier een fit voor gebruikt kunnen worden. Dit is een verbeterpunt voor een vervolg van het experiment.
   6) Het verschil tussen de 10% en 90% temperatuur wordt berekend: de transitiebreedte.